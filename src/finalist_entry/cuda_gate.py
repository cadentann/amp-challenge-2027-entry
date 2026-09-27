"""Production runtime gate: refuse to generate when the intended CUDA path cannot execute.

Why this exists
---------------
The locked device policy is ``auto_prefer_cuda``, which silently resolves to CPU whenever CUDA is
unavailable. On 2026-09-26 a rented host presented a healthy RTX 5090 to ``nvidia-smi`` while
**every** PyTorch build returned ``torch.cuda.is_available() == False`` with ``CUDA unknown error``.
Generation started anyway, on CPU, and began producing sequences that would **not** match the
submitted library --- and nothing in the output announced the fallback. This gate converts that
silent multi-hour wrong answer into an immediate, explicit failure.

Two checks, because the failure has two distinct shapes
------------------------------------------------------
1. CUDA is not available at all, or reports no device. Cheap, in-process, pure control flow.
2. CUDA reports available but cannot actually execute --- allocation or a kernel raises, or returns
   a wrong value. This needs a **real tensor operation**; ``is_available()`` alone does not catch it.

Check 2 runs in a **child process using this same interpreter**. That is deliberate, and it is a
trade-off worth stating. An in-process probe would be a marginally stronger test, but it would make
the generating process create a CUDA context and launch a kernel that it did not launch when the
submitted artifacts were produced. This project's artifacts are byte-reproducible and every receipt
binds those exact bytes; we will not add un-receipted CUDA work to the path that produces them. In
the child, the production process performs exactly the CUDA work it performed before this gate
existed --- no extra context, no extra allocation, no extra kernel, no RNG touched. The cost is one
short interpreter start before a ~50-minute generation.

The child is launched with ``sys.executable``, which inside this entry is the locked generator
environment (Python 3.12, torch 2.8.0+cu128), never an unrelated system interpreter.

What this gate does not do
--------------------------
It says nothing about, and does nothing to, the **scorer**. APEX and ANIA run in a separate pinned
runtime and legitimately run on CPU; ``scoring.py`` and ``scoring_adapter.py`` are untouched, and
this module is never consulted by them.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

#: Set to "1" to generate on CPU anyway. The output will NOT match the submitted artifacts.
ALLOW_CPU_ENV = "FINALIST_ALLOW_CPU_GENERATION"

#: ``eye(64) @ full((64, 64), 2.0)`` has 2.0 in every entry, so the sum is 64 * 64 * 2 = 8192;
#: adding ``eye(64)`` contributes its 64 ones. Every value is exactly representable in float32, so
#: a correct GPU must return exactly this. A silent-corruption failure shows up as a mismatch.
PROBE_EXPECTED = 8256.0

_PROBE_SOURCE = f'''
import json, os, sys
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
out = {{"stage": "import"}}
try:
    import torch
    out["torch_version"] = str(torch.__version__)
    out["stage"] = "availability"
    out["available"] = bool(torch.cuda.is_available())
    out["device_count"] = int(torch.cuda.device_count())
    if not out["available"] or out["device_count"] < 1:
        out["ok"] = False
        out["error"] = "torch.cuda.is_available() is False or no device is visible"
    else:
        out["stage"] = "configure"
        torch.cuda.set_device(0)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True)
        out["device_name"] = torch.cuda.get_device_name(0)
        out["capability"] = list(torch.cuda.get_device_capability(0))
        out["stage"] = "allocate"
        eye = torch.eye(64, dtype=torch.float32, device="cuda:0")
        twos = torch.full((64, 64), 2.0, dtype=torch.float32, device="cuda:0")
        out["stage"] = "matmul"
        value = float((eye @ twos + eye).sum().item())
        torch.cuda.synchronize()
        free, total = torch.cuda.mem_get_info()
        out["probe_value"] = value
        out["free_bytes"] = int(free)
        out["total_bytes"] = int(total)
        out["ok"] = value == {PROBE_EXPECTED!r}
        if not out["ok"]:
            out["error"] = "CUDA returned %r where %r is exact" % (value, {PROBE_EXPECTED!r})
        out["stage"] = "done"
except BaseException as error:
    out["ok"] = False
    out["error"] = "%s: %s" % (type(error).__name__, error)
sys.stdout.write(json.dumps(out))
'''

_CPU_MESSAGE = """\
REFUSING TO GENERATE: the intended CUDA generation path cannot execute.

{detail}

The locked device policy is {policy!r}, which would silently fall back to CPU. CPU generation
produces a DIFFERENT library from the submitted artifacts, and nothing downstream would tell you
so --- which is exactly the failure this check exists to prevent. Roughly 50 minutes of compute
would have been spent producing the wrong answer.

What to do:
  * Fix CUDA on this host and re-run. `nvidia-smi` showing a device is NOT sufficient; this check
    has already seen a host where it lied.
  * Or, if you genuinely want CPU output and accept that it will not match the submitted library,
    set {allow}=1. Do not use that to produce a submission.
"""


def _describe(result: dict) -> str:
    bits = [f"probe stage reached: {result.get('stage', 'unknown')}"]
    if "torch_version" in result:
        bits.append(f"torch: {result['torch_version']}")
    if "available" in result:
        bits.append(f"torch.cuda.is_available(): {result['available']}")
    if "device_count" in result:
        bits.append(f"visible devices: {result['device_count']}")
    if "device_name" in result:
        bits.append(f"device: {result['device_name']}")
    if result.get("error"):
        bits.append(f"error: {result['error']}")
    return "\n".join("  " + b for b in bits)


def probe_cuda_execution(*, python_executable: str | None = None, timeout: float = 300.0) -> dict:
    """Run the real-tensor CUDA probe in a child process and return its report."""
    executable = python_executable or sys.executable
    try:
        completed = subprocess.run(
            [executable, "-c", _PROBE_SOURCE],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "stage": "timeout",
                "error": f"CUDA probe did not finish within {timeout:.0f}s"}
    except OSError as error:
        return {"ok": False, "stage": "spawn", "error": f"{type(error).__name__}: {error}"}
    try:
        report = json.loads(completed.stdout.strip() or "{}")
    except json.JSONDecodeError:
        report = {}
    if not isinstance(report, dict) or "ok" not in report:
        return {"ok": False, "stage": "child_crash",
                "error": (f"CUDA probe returned exit {completed.returncode} without a usable "
                          f"report; stderr: {completed.stderr.strip()[-400:]!r}")}
    report.setdefault("child_returncode", completed.returncode)
    if completed.returncode != 0:
        report["ok"] = False
        report.setdefault("error", f"CUDA probe exited {completed.returncode}")
    return report


def gate_generation_device(device_policy: str, *, enforce: bool,
                           python_executable: str | None = None) -> dict:
    """Decide whether the intended generation device is actually usable.

    Args:
        device_policy: the locked ``device_policy``, taken from ``FINALIST.lock.json``.
        enforce: ``True`` on the production generation path --- raise instead of returning an
            unhealthy verdict. ``False`` in ``--preflight-only``, which reports and does not raise.
        python_executable: interpreter for the child probe; defaults to this one.

    Returns:
        A JSON-serialisable verdict recorded in the run receipt.
    """
    override = os.environ.get(ALLOW_CPU_ENV) == "1"
    verdict: dict = {"schema_version": "finalist-device-gate-v1",
                     "device_policy": device_policy,
                     "cpu_override_requested": override,
                     "enforced": bool(enforce)}

    if device_policy == "cpu_required":
        # The lock itself asks for CPU. There is no CUDA path to protect.
        verdict.update(status="CPU_REQUIRED_BY_LOCK", healthy=True)
        return verdict

    probe = probe_cuda_execution(python_executable=python_executable)
    verdict["probe"] = probe
    if probe.get("ok"):
        verdict.update(status="CUDA_OK", healthy=True)
        return verdict

    healthy = False
    if probe.get("available") is False or probe.get("device_count") == 0:
        verdict.update(status="CUDA_UNAVAILABLE", healthy=healthy)
    else:
        verdict.update(status="CUDA_UNUSABLE", healthy=healthy)

    detail = _describe(probe)
    if override:
        verdict["status"] += "_CPU_OVERRIDE_ACCEPTED"
        sys.stderr.write(
            "\n" + "!" * 78 + "\n"
            f"{ALLOW_CPU_ENV}=1 --- generating on CPU with a broken or absent CUDA path.\n"
            "The output will NOT match the submitted artifacts. Do not submit it.\n"
            f"{detail}\n" + "!" * 78 + "\n\n")
        sys.stderr.flush()
        return verdict
    if enforce:
        raise RuntimeError(_CPU_MESSAGE.format(detail=detail, policy=device_policy,
                                               allow=ALLOW_CPU_ENV))
    return verdict
