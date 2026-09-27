from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from finalist_entry.amp_prompt import AmpPromptStream, audit_checkpoint_state, prepare_torch
from finalist_entry import cuda_gate
from finalist_entry.fasta_io import read_fasta
from finalist_entry.library import collect_library
from finalist_entry.lock import load_finalist_lock
from finalist_entry.publish import publish_staged, stage_outputs
from finalist_entry import pipeline
from finalist_entry.library import LibraryResult


class FixedBatches:
    batch_size = 4

    def __init__(self, batches):
        self._batches = iter(batches)

    def sample_batch(self):
        return next(self._batches)


class TestFailClosedAndEligibility(unittest.TestCase):
    def test_missing_final_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError, "FINALIST.lock.json is absent"):
                load_finalist_lock(Path(td))

    def test_duplicate_reference_length_and_raw_accounting(self):
        reference = "ACDEFGHI"
        source = FixedBatches([
            [reference, reference, "AAAAAAA", "ACDEFGHIK"],
            ["CDEFGHIKL", "DEFGHIKLM", "EFGHIKLMN", "FGHIKLMNP"],
        ])
        batches = []
        result = collect_library(
            source, {reference}, target=3, raw_ceiling=8,
            batch_observer=lambda index, rows: batches.append((index, rows)),
        )
        self.assertEqual(result.sequences, ["ACDEFGHIK", "CDEFGHIKL", "DEFGHIKLM"])
        self.assertEqual(result.raw_generated, 8)
        self.assertEqual(result.raw_examined, 6)
        self.assertEqual(result.rejection_counts, {
            "alphabet_or_length": 1,
            "exact_reference": 2,
        })
        self.assertEqual([len(rows) for _, rows in batches], [4, 4])
        ledger = [row for _, rows in batches for row in rows]
        self.assertEqual([row["raw_index"] for row in ledger], list(range(8)))
        self.assertEqual([row["disposition"] for row in ledger[-2:]], [
            "AFTER_TARGET_IN_FINAL_BATCH", "AFTER_TARGET_IN_FINAL_BATCH",
        ])

    def test_raw_output_is_not_repaired(self):
        source = FixedBatches([
            ["acdefghi", " ACDEFGHI", "ACDEFGHI\n", "ACDEXGHI"],
            ["ACDEFGHI", "CDEFGHIK", "DEFGHIKL", "EFGHIKLM"],
        ])
        result = collect_library(source, set(), target=2, raw_ceiling=8)
        self.assertEqual(result.sequences, ["ACDEFGHI", "CDEFGHIK"])
        self.assertEqual(result.rejection_counts, {"alphabet_or_length": 4})


class TestContinuousRng(unittest.TestCase):
    def test_mock_generator_has_one_continuous_rng_stream(self):
        class MockStream:
            batch_size = 128

            def __init__(self, seed):
                self.rng = random.Random(seed)

            def sample_batch(self):
                return [self.rng.randrange(10**9) for _ in range(self.batch_size)]

        stream = MockStream(901)
        observed = stream.sample_batch() + stream.sample_batch()
        control = random.Random(901)
        expected = [control.randrange(10**9) for _ in range(256)]
        self.assertEqual(observed, expected)
        self.assertNotEqual(observed[:128], observed[128:])

    def test_authentic_batch_method_contains_no_rng_reset(self):
        tree = ast.parse(textwrap.dedent(inspect.getsource(AmpPromptStream.sample_batch)))
        calls = [
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        self.assertFalse({"seed", "manual_seed", "manual_seed_all"} & set(calls))

    def test_conflicting_cublas_configuration_fails_before_torch_import(self):
        previous = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
        try:
            with self.assertRaisesRegex(RuntimeError, "frozen value"):
                prepare_torch("cpu_required", {})
        finally:
            if previous is None:
                os.environ.pop("CUBLAS_WORKSPACE_CONFIG", None)
            else:
                os.environ["CUBLAS_WORKSPACE_CONFIG"] = previous


class FakeTensor:
    def __init__(self, shape, value, pointer):
        self.shape = shape
        self.value = value
        self.pointer = pointer


class TestCheckpointAudit(unittest.TestCase):
    def test_all_174_tensors_and_embedding_tie_are_audited(self):
        residue = FakeTensor([25, 768], "residue", 100)
        learned = FakeTensor([10, 768], "learned", 200)
        checkpoint = {
            "transformer.wte.learned_embedding": learned,
            "transformer.wte.wte.weight": residue,
            "lm_head.weight": residue,
        }
        for index in range(171):
            checkpoint[f"tensor.{index}"] = FakeTensor([1], index, 1000 + index)
        reconstructed = dict(checkpoint)
        result = audit_checkpoint_state(
            checkpoint,
            reconstructed,
            equal=lambda left, right: left.shape == right.shape and left.value == right.value,
            data_ptr=lambda tensor: tensor.pointer,
        )
        self.assertEqual(result["checkpoint_tensor_count"], 174)
        self.assertTrue(result["every_checkpoint_tensor_exact"])
        self.assertTrue(result["lm_head_shared_storage"])


class TestAtomicPublication(unittest.TestCase):
    def test_complete_outputs_replace_prior_run_and_repeat_exactly(self):
        library = ["ACDEFGHI", "CDEFGHIK"]
        top = ["CDEFGHIK"]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "generate"
            output.mkdir()
            (output / "sentinel").write_text("old")
            first = root / "stage-first"
            stage_outputs(first, library, top, {"run": 1})
            publish_staged(first, output, "first")
            self.assertFalse((output / "sentinel").exists())
            first_library = (output / "library.fasta").read_bytes()
            first_top = (output / "top.fasta").read_bytes()
            second = root / "stage-second"
            stage_outputs(second, library, top, {"run": 2})
            publish_staged(second, output, "second")
            self.assertEqual((output / "library.fasta").read_bytes(), first_library)
            self.assertEqual((output / "top.fasta").read_bytes(), first_top)

    def test_incomplete_stage_cannot_replace_current_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "generate"
            output.mkdir()
            (output / "sentinel").write_text("retain")
            stage = root / "incomplete"
            stage.mkdir()
            (stage / "library.fasta").write_text(">seq1\nACDEFGHI\n")
            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                publish_staged(stage, output, "bad")
            self.assertEqual((output / "sentinel").read_text(), "retain")


class TestRunEvidence(unittest.TestCase):
    @staticmethod
    def _mechanical_sequences(count):
        alphabet = "ACDEFGHIKLMNPQRSTVWY"
        result = []
        for number in range(count):
            chars = []
            for _ in range(8):
                number, index = divmod(number, len(alphabet))
                chars.append(alphabet[index])
            result.append("".join(chars))
        return result

    @staticmethod
    def _lock(root):
        reference = root / "reference.fasta"
        reference.write_text(">ref\nWWWWWWWW\n")

        class Lock:
            sha256 = "0" * 64
            data = {
                "raw_ceiling": 50176,
                "selection_universe": "score_blind_subset",
                "selection_pool_size": 100,
                "pool_seed": 7,
                "top_eligibility_order": "top_e_then_hash",
                "scientific_authorization_sha256": "1" * 64,
                "arm": "AMP-Prompt",
                "selector": "CONSENSUS_FIXED",
            }

            def path_value(self, key):
                assert key == "reference_path"
                return reference

        return Lock()

    def test_completed_generation_is_durable_before_scorer_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lock = self._lock(root)
            sequences = self._mechanical_sequences(50_000)
            pool_rows = [{"sequence": sequence, "raw_index": index} for index, sequence in enumerate(sequences[:100])]
            pool = {
                "schema_version": "frontier-finalist-pool-v1", "seed": 7,
                "target": 100, "eligible_count": 100, "selected_count": 100,
                "status": "COMPLETE", "rows": pool_rows,
            }
            with (
                mock.patch.object(pipeline, "preflight",
                                  return_value=(lock, {"status": "READY_NO_INFERENCE"},
                                                {"status": "CUDA_OK", "healthy": True})),
                mock.patch.object(pipeline, "AmpPromptStream", return_value=SimpleNamespace(batch_size=128)),
                mock.patch.object(pipeline, "collect_library", return_value=LibraryResult(sequences, 50176, 50000, {})),
                mock.patch.object(pipeline, "qualify_and_choose_universe", return_value=pool),
                mock.patch.object(pipeline, "score_pool", side_effect=RuntimeError("mechanical scorer failure")),
            ):
                with self.assertRaisesRegex(RuntimeError, "mechanical scorer failure"):
                    pipeline.run(root)
            run_root = next((root / ".finalist-runs").iterdir())
            evidence = run_root / "evidence"
            self.assertTrue((evidence / "accepted_library.fasta").is_file())
            self.assertTrue((evidence / "qualified_pool.json").is_file())
            self.assertTrue((evidence / "scoring_input_manifest.json").is_file())
            failure = json.loads((run_root / "FAILED.json").read_text())
            self.assertEqual(failure["phase"], "SCORING")
            self.assertFalse((root / "generate").exists())

    def test_midgeneration_failure_keeps_flushed_complete_batch(self):
        class FailingStream:
            batch_size = 4

            def __init__(self):
                self.calls = 0
                self.binding = SimpleNamespace()
                self.checkpoint_audit = {}

            def sample_batch(self):
                self.calls += 1
                if self.calls == 1:
                    return ["ACDEFGHI", "CDEFGHIK", "DEFGHIKL", "EFGHIKLM"]
                raise RuntimeError("mechanical generator interruption")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lock = self._lock(root)
            with (
                mock.patch.object(pipeline, "preflight",
                                  return_value=(lock, {"status": "READY_NO_INFERENCE"},
                                                {"status": "CUDA_OK", "healthy": True})),
                mock.patch.object(pipeline, "AmpPromptStream", return_value=FailingStream()),
            ):
                with self.assertRaisesRegex(RuntimeError, "mechanical generator interruption"):
                    pipeline.run(root)
            run_root = next((root / ".finalist-runs").iterdir())
            rows = (run_root / "evidence/raw_ledger.jsonl").read_text().splitlines()
            self.assertEqual(len(rows), 4)
            self.assertEqual([json.loads(row)["raw_index"] for row in rows], list(range(4)))
            failure = json.loads((run_root / "FAILED.json").read_text())
            self.assertEqual(failure["phase"], "GENERATION")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Some checks compare this package against the author's canonical working tree.
# That tree is not part of the submission, so the path is taken from the
# environment and the checks skip cleanly wherever it is absent.
_CANONICAL_ROOT = os.environ.get("AMP_CANONICAL_ROOT")


def _canonical(relative: str) -> Path | None:
    if not _CANONICAL_ROOT:
        return None
    return Path(_CANONICAL_ROOT) / relative


class TestFrozenSelector(unittest.TestCase):
    def test_vendor_source_has_registered_bytes(self):
        path = ROOT / "vendor/frozen_selector/common_core.py"
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(),
            "963085ddb945b04173a6f81c2cab4f016bab366eb497584e1edddcf76f927679",
        )

    @unittest.skipUnless(
        (_canonical("common/common_core.py") or Path("/nonexistent")).is_file(),
        "canonical tournament source is unavailable",
    )
    def test_consensus_output_matches_canonical_module(self):
        canonical_path = _canonical("common/common_core.py")
        vendor = _load_module("test_vendor_core", ROOT / "vendor/frozen_selector/common_core.py")
        canonical = _load_module("test_canonical_core", canonical_path)
        alphabet = "ACDEFGHIKLMNPQRSTVWY"

        def sequence(number):
            chars = []
            for _ in range(8):
                number, index = divmod(number, len(alphabet))
                chars.append(alphabet[index])
            return "".join(chars)

        rows = []
        for index in range(120):
            seq = sequence(index)
            apex = [float(1 + ((index * 13 + head * 7) % 97)) for head in range(11)]
            ania = [float(((index * 11 + head * 3) % 41) / 10) for head in range(3)]
            rows.append({
                "sequence": seq,
                "raw_index": index,
                "top_eligible": True,
                "reference": {"maximum_ratio": 0.0},
                "features": vendor.score_features(apex, ania),
            })
        anchor = {
            "status": "AVAILABLE",
            "count": 100,
            "apex": [float(x) / 10 for x in range(100)],
            "ania": [float(x) / 10 for x in range(100)],
        }
        observed = vendor.run_selectors(rows, anchor=anchor, top_k=100)["CONSENSUS_FIXED"]
        expected = canonical.run_selectors(rows, anchor=anchor, top_k=100)["CONSENSUS_FIXED"]
        self.assertEqual(observed, expected)


class TestEvaluatorProvenance(unittest.TestCase):
    @unittest.skipUnless(
        (_canonical("amp_designer/ASSET_ACQUISITION.json") or Path("/nonexistent")).is_file(),
        "canonical AMP asset acquisition is unavailable",
    )
    def test_amp_retrieval_pins_match_canonical_acquisition(self):
        acquisition = json.loads(_canonical("amp_designer/ASSET_ACQUISITION.json").read_text())
        sources = json.loads((ROOT / "ASSET_SOURCES.json").read_text())["amp_prompt"]
        self.assertEqual(sources["archive_bytes"], acquisition["size_bytes"])
        self.assertEqual(sources["archive_md5"], acquisition["observed_md5"])
        self.assertEqual(sources["archive_sha256"], acquisition["zip_sha256"])

    def test_current_evaluator_snapshots_have_registered_bytes(self):
        expected = {
            "RUNTIME_MANIFEST.json": "ecacbe1ed1fa840ecd9c684ccf781e808ba33a3f97420384473e3d3115e77fa7",
            "runtime_config.json": "2c925e17a4b9c25b3b413b2e748d5f1566d80bf2643bec9538b29de4c8648162",
            "score_batch.py": "5773d025790141833670b0a939f583034e9a9073012a44572ae80ab91845a80c",
        }
        for name, registered in expected.items():
            observed = hashlib.sha256((ROOT / "vendor/evaluator" / name).read_bytes()).hexdigest()
            self.assertEqual(observed, registered, name)

    def test_dual_runtime_projects_are_separate_and_locked(self):
        generator = (ROOT / "pyproject.toml").read_text()
        scorer_project = ROOT / "vendor/scorer_subproject"
        scorer = (scorer_project / "pyproject.toml").read_text()
        self.assertIn('requires-python = "==3.12.*"', generator)
        self.assertIn('requires-python = "==3.10.20"', scorer)
        self.assertTrue((ROOT / "uv.lock").is_file())
        self.assertTrue((scorer_project / "uv.lock").is_file())

    def test_worker_preserves_member_arrays_and_platform_build_pins(self):
        worker = (ROOT / "vendor/scorer_subproject/scorer_worker.py").read_text()
        adapter = (ROOT / "scoring_adapter.py").read_text()
        self.assertIn("apex_base_mic_uM=apex_members", worker)
        self.assertIn('"apex_member_order"', worker)
        self.assertIn('("Linux", "x86_64"): ("2.5.1+cu124", "12.4")', adapter)
        self.assertIn("71328e1bbe39d213b8721678f9dcac30dfc452a46d586f1d514a6aa0a99d4744", adapter)

    def test_pending_scorer_runtime_cannot_probe(self):
        scoring_adapter = _load_module("test_scoring_adapter", ROOT / "scoring_adapter.py")
        template = json.loads((ROOT / "SCORER_RUNTIME.lock.template.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            runtime = Path(td)
            (runtime / "SCORER_RUNTIME.lock.json").write_text(json.dumps(template))
            with self.assertRaisesRegex(RuntimeError, "pending cross-evaluator"):
                scoring_adapter.probe(runtime)


class TestOfficialInterface(unittest.TestCase):
    def test_console_script_is_generate(self):
        pyproject = (ROOT / "pyproject.toml").read_text()
        self.assertIn('generate = "finalist_entry.cli:main"', pyproject)

    def test_cli_fails_closed_before_heavy_imports(self):
        """The entry point must refuse, in preflight, when a pinned prerequisite is absent.

        On a fresh clone the scorer runtime has not been built yet, so preflight is
        expected to stop there. What matters is that it stops in the lock/preflight
        layer, never reaches a model load, and leaves no output directory behind.
        """
        environment = dict(os.environ, PYTHONPATH=str(SRC))
        result = subprocess.run(
            [sys.executable, "-m", "finalist_entry.cli", "--preflight-only", "--no-prepare"],
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            # A fully prepared checkout legitimately passes preflight.
            self.assertIn("READY_NO_INFERENCE", result.stdout)
            return
        self.assertRegex(
            result.stderr,
            r"missing (scoring runtime lock|reference|vocabulary|frozen anchor|scoring adapter)"
            r"|FINALIST\.lock\.json is absent",
        )
        self.assertIn("finalist_entry/lock.py", result.stderr)
        self.assertNotIn("torch", result.stderr)
        self.assertNotIn("transformers", result.stderr)
        self.assertFalse((ROOT / "generate").exists())

    def test_cli_reports_absent_lock_explicitly(self):
        """With no FINALIST.lock.json at all, the refusal names the lock."""
        environment = dict(os.environ, PYTHONPATH=str(SRC))
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "checkout"
            empty.mkdir()
            result = subprocess.run(
                [sys.executable, "-m", "finalist_entry.cli", "--preflight-only", "--no-prepare"],
                cwd=empty,
                env=dict(environment, FINALIST_PROJECT_ROOT=str(empty)),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertNotEqual(result.returncode, 0)

    def test_fasta_writer_contract_is_round_trip_safe(self):
        with tempfile.TemporaryDirectory() as td:
            stage = Path(td) / "stage"
            sequences = ["ACDEFGHI", "CDEFGHIK"]
            stage_outputs(stage, sequences, sequences[:1], {})
            self.assertEqual(read_fasta(stage / "library.fasta"), sequences)
            self.assertEqual(read_fasta(stage / "top.fasta"), sequences[:1])




# --- device gate ------------------------------------------------------------------------------
# The gate exists because a host once presented a healthy RTX 5090 to nvidia-smi while no PyTorch
# build could initialise CUDA, and generation silently fell back to CPU. These tests drive the real
# child-process probe source against a stub `torch`, so both failure shapes are exercised for real
# rather than mocked away: CUDA absent, and CUDA present but unable to execute.

TORCH_STUB = textwrap.dedent('''
    import os

    _MODE = os.environ["STUB_TORCH_MODE"]
    __version__ = "2.8.0+cu128"
    float32 = "float32"


    class _Tensor:
        def __init__(self, total):
            self._total = total

        def __matmul__(self, other):
            return _Tensor(64 * 64 * 2.0)

        def __add__(self, other):
            return _Tensor(self._total + other._total)

        def sum(self):
            return self

        def item(self):
            return self._total


    def eye(n, dtype=None, device=None):
        if _MODE == "raise_on_allocate":
            raise RuntimeError("CUDA error: unknown error")
        return _Tensor(float(n))


    def full(shape, value, dtype=None, device=None):
        return _Tensor(shape[0] * shape[1] * value)


    def use_deterministic_algorithms(flag):
        pass


    class _Matmul:
        allow_tf32 = True


    class _CudaBackend:
        matmul = _Matmul()


    class _Cudnn:
        allow_tf32 = True
        deterministic = False
        benchmark = True


    class backends:
        cuda = _CudaBackend()
        cudnn = _Cudnn()


    class cuda:
        @staticmethod
        def is_available():
            return _MODE != "unavailable"

        @staticmethod
        def device_count():
            return 0 if _MODE == "unavailable" else 1

        @staticmethod
        def set_device(index):
            pass

        @staticmethod
        def get_device_name(index):
            return "STUB RTX 5090"

        @staticmethod
        def get_device_capability(index):
            return (12, 0)

        @staticmethod
        def synchronize():
            pass

        @staticmethod
        def mem_get_info():
            return (1 << 30, 1 << 31)
    ''')


class TestDeviceGate(unittest.TestCase):
    def _probe_with_stub(self, mode, *, corrupt=False):
        # The probe source is used verbatim; `corrupt` instead makes the stub GPU return a
        # wrong number from a kernel that ran, which is the silent-corruption case.
        source = cuda_gate._PROBE_SOURCE
        with tempfile.TemporaryDirectory() as td:
            stub = Path(td) / "torch.py"
            body = TORCH_STUB
            if corrupt:
                body = body.replace("return _Tensor(64 * 64 * 2.0)", "return _Tensor(1.0)")
            stub.write_text(body)
            env = dict(os.environ, PYTHONPATH=td, STUB_TORCH_MODE=mode)
            completed = subprocess.run([sys.executable, "-c", source],
                                       capture_output=True, text=True, env=env, timeout=120)
            return json.loads(completed.stdout.strip()), completed

    def test_probe_source_reports_healthy_cuda(self):
        report, completed = self._probe_with_stub("healthy")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["probe_value"], cuda_gate.PROBE_EXPECTED)
        self.assertEqual(report["device_name"], "STUB RTX 5090")
        self.assertEqual(report["stage"], "done")

    def test_probe_source_detects_unavailable_cuda(self):
        report, _ = self._probe_with_stub("unavailable")
        self.assertFalse(report["ok"])
        self.assertFalse(report["available"])
        self.assertEqual(report["device_count"], 0)

    def test_probe_source_detects_cuda_that_cannot_allocate(self):
        """The RTX 5090 shape of the failure: available() may pass, execution does not."""
        report, _ = self._probe_with_stub("raise_on_allocate")
        self.assertFalse(report["ok"])
        self.assertTrue(report["available"])
        self.assertEqual(report["stage"], "allocate")
        self.assertIn("unknown error", report["error"])

    def test_probe_source_detects_a_wrong_result(self):
        report, _ = self._probe_with_stub("healthy", corrupt=True)
        self.assertFalse(report["ok"])
        self.assertNotEqual(report["probe_value"], cuda_gate.PROBE_EXPECTED)

    def test_gate_raises_on_the_production_path(self):
        unhealthy = {"ok": False, "stage": "availability", "available": False, "device_count": 0,
                     "error": "torch.cuda.is_available() is False or no device is visible"}
        with mock.patch.object(cuda_gate, "probe_cuda_execution", return_value=unhealthy):
            with mock.patch.dict(os.environ, {}, clear=False):
                os.environ.pop(cuda_gate.ALLOW_CPU_ENV, None)
                with self.assertRaises(RuntimeError) as caught:
                    cuda_gate.gate_generation_device("auto_prefer_cuda", enforce=True)
        message = str(caught.exception)
        self.assertIn("REFUSING TO GENERATE", message)
        self.assertIn("would silently fall back to CPU", message)
        self.assertIn(cuda_gate.ALLOW_CPU_ENV, message)

    def test_gate_reports_without_raising_in_preflight(self):
        unhealthy = {"ok": False, "available": True, "device_count": 1, "error": "boom"}
        with mock.patch.object(cuda_gate, "probe_cuda_execution", return_value=unhealthy):
            verdict = cuda_gate.gate_generation_device("auto_prefer_cuda", enforce=False)
        self.assertEqual(verdict["status"], "CUDA_UNUSABLE")
        self.assertFalse(verdict["healthy"])

    def test_explicit_cpu_override_is_allowed_and_loud(self):
        unhealthy = {"ok": False, "available": False, "device_count": 0, "error": "no cuda"}
        with mock.patch.object(cuda_gate, "probe_cuda_execution", return_value=unhealthy):
            with mock.patch.dict(os.environ, {cuda_gate.ALLOW_CPU_ENV: "1"}):
                with mock.patch("sys.stderr", new_callable=io.StringIO) as err:
                    verdict = cuda_gate.gate_generation_device("auto_prefer_cuda", enforce=True)
        self.assertTrue(verdict["status"].endswith("_CPU_OVERRIDE_ACCEPTED"))
        self.assertIn("will NOT match the submitted artifacts", err.getvalue())

    def test_healthy_cuda_passes_and_is_recorded(self):
        healthy = {"ok": True, "device_name": "NVIDIA GeForce RTX 4090", "probe_value": 8256.0}
        with mock.patch.object(cuda_gate, "probe_cuda_execution", return_value=healthy):
            verdict = cuda_gate.gate_generation_device("auto_prefer_cuda", enforce=True)
        self.assertEqual(verdict["status"], "CUDA_OK")
        self.assertTrue(verdict["healthy"])
        self.assertEqual(verdict["probe"]["device_name"], "NVIDIA GeForce RTX 4090")

    def test_cpu_required_lock_needs_no_gpu_and_never_probes(self):
        """A lock that asks for CPU has no CUDA path to protect; local CPU work stays possible."""
        with mock.patch.object(cuda_gate, "probe_cuda_execution",
                               side_effect=AssertionError("must not probe")):
            verdict = cuda_gate.gate_generation_device("cpu_required", enforce=True)
        self.assertEqual(verdict["status"], "CPU_REQUIRED_BY_LOCK")
        self.assertTrue(verdict["healthy"])

    def test_child_that_emits_nothing_is_a_failure_not_a_pass(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "silent"
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
            report = cuda_gate.probe_cuda_execution(python_executable=str(fake))
        self.assertFalse(report["ok"])
        self.assertEqual(report["stage"], "child_crash")

    def test_missing_interpreter_is_a_failure_not_a_pass(self):
        report = cuda_gate.probe_cuda_execution(python_executable="/nonexistent/python")
        self.assertFalse(report["ok"])
        self.assertEqual(report["stage"], "spawn")

    def test_the_gate_never_touches_the_scorer(self):
        """Local CPU scoring must remain possible; the gate reads only the generator policy.

        Checked against the parsed module, not its text --- the docstring legitimately *mentions*
        the scorer in order to say it is out of scope, and an earlier version of this test flagged
        that prose as a defect.
        """
        tree = ast.parse(Path(cuda_gate.__file__).read_text())
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                    for alias in node.names}
        imported |= {node.module or "" for node in ast.walk(tree)
                     if isinstance(node, ast.ImportFrom)}
        for forbidden in ("scoring", "scoring_adapter", ".scoring", "finalist_entry.scoring"):
            self.assertNotIn(forbidden, imported)
        called = {node.func.id for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        called |= {node.func.attr for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        for forbidden in ("probe_scoring", "score_pool"):
            self.assertNotIn(forbidden, called)

    def test_production_process_gains_no_cuda_work(self):
        """The real tensor probe must stay out of process, so generation numerics cannot shift."""
        tree = ast.parse(Path(cuda_gate.__file__).read_text())
        top_level_torch = [n for n in ast.walk(tree)
                           if isinstance(n, (ast.Import, ast.ImportFrom))
                           and "torch" in ast.dump(n)]
        self.assertEqual(top_level_torch, [],
                         "cuda_gate must not import torch in the generating process")
        self.assertIn("subprocess.run", Path(cuda_gate.__file__).read_text())


if __name__ == "__main__":
    unittest.main()
