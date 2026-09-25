from __future__ import annotations

import importlib.util
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .hashing import require_file


SOURCE_COMMIT = "07d455dd6eb7ef61fe03b85732966caa32bf3dc4"
CHECKPOINT_SHA256 = "47944ff42f7ea6a448340d44c2027329833205dd658ec4777e77777bdab1adc9"
CONFIG_SHA256 = "e8f1bed7607065b7a11e5f338a5a5e618947ae78ee0bc0314689cf9801d7d62a"
VOCAB_SHA256 = "b887319d2f815b62750fbd32e4ecf4c730d6df7963983ca073972af79574fe58"
SOFT_EMBEDDING_SHA256 = "6673c6072e49fc01a7556fb9ed136362af0b90fb693f367ee3b096f1e980820f"
CHECKPOINT_TENSORS = 174
BATCH_SIZE = 128
TOP_K = 10
TOP_P = 1.0
MAX_NEW_TOKENS = 34


def audit_checkpoint_state(
    checkpoint: dict[str, Any],
    reconstructed: dict[str, Any],
    *,
    equal: Callable[[Any, Any], bool],
    data_ptr: Callable[[Any], int],
) -> dict[str, Any]:
    checkpoint_keys = set(checkpoint)
    reconstructed_keys = set(reconstructed)
    mismatches = sorted(
        key for key in checkpoint_keys & reconstructed_keys
        if not equal(checkpoint[key], reconstructed[key])
    )
    missing = sorted(checkpoint_keys - reconstructed_keys)
    extra = sorted(reconstructed_keys - checkpoint_keys)
    if len(checkpoint) != CHECKPOINT_TENSORS or missing or extra or mismatches:
        raise RuntimeError(
            f"checkpoint reconstruction failed: tensors={len(checkpoint)}, "
            f"missing={missing}, extra={extra}, mismatches={mismatches}"
        )
    learned = reconstructed["transformer.wte.learned_embedding"]
    residue = reconstructed["transformer.wte.wte.weight"]
    head = reconstructed["lm_head.weight"]
    if list(learned.shape) != [10, 768] or list(residue.shape) != [25, 768]:
        raise RuntimeError("restored embedding shapes differ from authenticated checkpoint")
    if not equal(head, residue) or data_ptr(head) != data_ptr(residue):
        raise RuntimeError("LM head is not exactly tied to the restored residue embedding")
    return {
        "status": "PASS",
        "checkpoint_tensor_count": len(checkpoint),
        "reconstructed_tensor_count": len(reconstructed),
        "every_checkpoint_tensor_exact": True,
        "keysets_equal": True,
        "learned_prompt_shape": [10, 768],
        "residue_embedding_shape": [25, 768],
        "lm_head_tied_exact": True,
        "lm_head_shared_storage": True,
    }


def _load_soft_embedding(path: Path):
    spec = importlib.util.spec_from_file_location("finalist_soft_prompt_embedding", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned SoftEmbedding source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SoftEmbedding


@dataclass
class DeviceBinding:
    logical_device: str
    name: str | None
    capability: list[int] | None


def prepare_torch(device_policy: str, lock_data: dict[str, Any]):
    cublas = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
    if cublas is not None and cublas != ":4096:8":
        raise RuntimeError(
            f"CUBLAS_WORKSPACE_CONFIG is already {cublas!r}; frozen value is ':4096:8'"
        )
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.environ.setdefault("PYTHONHASHSEED", "0")
    import numpy as np
    import torch
    import transformers

    if not str(torch.__version__).startswith(lock_data["torch_version_prefix"]):
        raise RuntimeError(f"Torch version mismatch: {torch.__version__}")
    if transformers.__version__ != lock_data["transformers_version"]:
        raise RuntimeError(f"Transformers version mismatch: {transformers.__version__}")
    if np.__version__ != lock_data["numpy_version"]:
        raise RuntimeError(f"NumPy version mismatch: {np.__version__}")
    if not sys.version.split()[0].startswith(lock_data["python_version_prefix"]):
        raise RuntimeError(f"Python version mismatch: {sys.version.split()[0]}")
    if device_policy == "private_cuda_required":
        if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
            raise RuntimeError("private CUDA policy requires exactly one visible GPU")
        logical = "cuda:0"
    elif device_policy == "auto_prefer_cuda":
        logical = "cuda:0" if torch.cuda.is_available() else "cpu"
    elif device_policy == "cpu_required":
        logical = "cpu"
    else:
        raise RuntimeError("unsupported device policy")
    if logical == "cuda:0":
        torch.cuda.set_device(0)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        binding = DeviceBinding(logical, torch.cuda.get_device_name(0), list(torch.cuda.get_device_capability(0)))
    else:
        binding = DeviceBinding(logical, None, None)
    torch.use_deterministic_algorithms(True)
    return torch, np, transformers, binding


class AmpPromptStream:
    """Stateful native sampler. RNGs are seeded once and never reset per batch."""

    batch_size = BATCH_SIZE

    def __init__(self, lock, project_root: Path):
        self.lock = lock
        self.project_root = Path(project_root)
        self.torch, self.np, transformers, self.binding = prepare_torch(
            lock.data["device_policy"], lock.data
        )
        seed = lock.data["generation_seed"]
        random.seed(seed)
        self.np.random.seed(seed)
        self.torch.manual_seed(seed)
        if self.torch.cuda.is_available():
            self.torch.cuda.manual_seed_all(seed)
        from transformers import BertTokenizer
        from transformers.models.gpt2 import GPT2LMHeadModel

        model_dir = lock.path_value("model_dir")
        vocab = lock.path_value("vocab_path")
        checkpoint = self.torch.load(model_dir / "pytorch_model.bin", map_location="cpu", weights_only=False)
        if not isinstance(checkpoint, dict):
            raise RuntimeError("released checkpoint is not a tensor state dictionary")
        model = GPT2LMHeadModel.from_pretrained(model_dir)
        soft_embedding_path = require_file(
            self.project_root / "vendor/amp_prompt/soft_prompt_embedding.py",
            SOFT_EMBEDDING_SHA256,
            label="authenticated SoftEmbedding source",
        )
        SoftEmbedding = _load_soft_embedding(soft_embedding_path)
        embedding = SoftEmbedding(model.get_input_embeddings(), n_tokens=10, initialize_from_vocab=True)
        embedding.learned_embedding.data = checkpoint["transformer.wte.learned_embedding"].clone()
        embedding.wte.weight.data = checkpoint["transformer.wte.wte.weight"].clone()
        model.set_input_embeddings(embedding)
        self.checkpoint_audit = audit_checkpoint_state(
            checkpoint, model.state_dict(), equal=self.torch.equal,
            data_ptr=lambda tensor: tensor.data_ptr(),
        )
        self.model = model.to(self.binding.logical_device).eval()
        self.tokenizer = BertTokenizer(vocab_file=str(vocab))
        self.prefix = list(range(100, 110)) + [self.tokenizer.cls_token_id]
        del checkpoint

    def sample_batch(self) -> list[str]:
        torch = self.torch
        device = self.binding.logical_device
        input_ids = torch.tensor([self.prefix] * self.batch_size, dtype=torch.long, device=device)
        sampled_tokens: list[list[str]] = [[] for _ in range(self.batch_size)]
        finished = [False] * self.batch_size
        with torch.inference_mode():
            for _ in range(MAX_NEW_TOKENS):
                logits = self.model(input_ids=input_ids).logits[:, -1, :]
                threshold = torch.topk(logits, min(TOP_K, logits.shape[-1]))[0][:, -1, None]
                logits = logits.masked_fill(logits < threshold, -float("inf"))
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                token_ids = torch.multinomial(probabilities, 1)
                token_text = self.tokenizer.convert_ids_to_tokens(
                    token_ids.squeeze(-1).detach().cpu().tolist()
                )
                for index, token in enumerate(token_text):
                    if not finished[index]:
                        if token == "[SEP]":
                            finished[index] = True
                        else:
                            sampled_tokens[index].append(token.upper())
                input_ids = torch.cat((input_ids, token_ids), dim=1)
                if all(finished):
                    break
        return ["".join(tokens) for tokens in sampled_tokens]
