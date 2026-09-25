#!/usr/bin/env python3
"""R-free, source-pinned port of the ANIA 20-letter kaos CGR encoder."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
CONSTANTS_PATH = HERE / "r_constants.json"
AUTHOR_FEATURE_SHA256 = "bd05a3695f4df9010e4210890cebdf19195dbe2c0d6e436efba23821fab18976"
PROPERTY_TABLE_SHA256 = "0d417fd0eb9a1a6edcff604507cf84b10c0334ef6ea0fffc9b8dad952c9bf95d"
PYTHON_HASH_PROBE = "ANIA_PORTABILITY_HASH_PROBE"
PYTHON_HASH_SEED_0_VALUE = 8998953309933277494
DEFAULT_PROPERTIES = (
    "ARGP820101",
    "CHAM830107",
    "FAUJ880103",
    "GRAR740102",
    "JANJ780101",
    "KYTJ820101",
    "NAKH920104",
    "ROSM880102",
    "WERD780104",
    "ZIMJ680101",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_CONSTANTS = json.loads(CONSTANTS_PATH.read_text())
ALPHABET = tuple(_CONSTANTS["alphabet"])
ALPHABET_SET = frozenset(ALPHABET)
BASE_X = tuple(float.fromhex(value) for value in _CONSTANTS["base_x_hex"])
BASE_Y = tuple(float.fromhex(value) for value in _CONSTANTS["base_y_hex"])
SCALING_FACTOR = float.fromhex(_CONSTANTS["scaling_factor_hex"])
BASE_BY_AA = dict(zip(ALPHABET, zip(BASE_X, BASE_Y)))


def require_python_hash_seed_zero() -> None:
    """Fail closed unless set iteration matches the frozen author-function run."""
    if os.environ.get("PYTHONHASHSEED") != "0" or hash(PYTHON_HASH_PROBE) != PYTHON_HASH_SEED_0_VALUE:
        raise RuntimeError(
            "ANIA property encoding requires CPython 3.10 started with PYTHONHASHSEED=0"
        )


@dataclass(frozen=True)
class CGRResult:
    """The subset of a kaos cgr object used by ANIA's author feature functions."""

    matrix: np.ndarray
    x: np.ndarray
    y: np.ndarray
    scaling_factor: float
    resolution: int

    def rx2(self, name: str):
        if name not in {"matrix", "x", "y", "scaling_factor", "resolution"}:
            raise KeyError(name)
        return getattr(self, name)


def cgr(sequence: str, resolution: int = 16) -> CGRResult:
    """Port kaos::cgr for its fixed 20-letter ``seq.base='AMINO'`` use."""
    if not isinstance(sequence, str):
        raise TypeError("sequence must be str")
    if not isinstance(resolution, int) or isinstance(resolution, bool) or resolution < 1:
        raise ValueError("resolution must be a positive integer")
    invalid = set(sequence) - ALPHABET_SET
    if invalid:
        raise ValueError(f"noncanonical amino acids: {''.join(sorted(invalid))}")

    matrix = np.zeros((resolution, resolution), dtype=np.int64)
    x_coordinates = np.empty(len(sequence), dtype=np.float64)
    y_coordinates = np.empty(len(sequence), dtype=np.float64)
    x = 0.0
    y = 0.0
    sf = SCALING_FACTOR

    # Keep the scalar operation order from cgr.R:
    # pt = pt + (base - pt) * sf
    for index, amino_acid in enumerate(sequence):
        base_x, base_y = BASE_BY_AA[amino_acid]
        x = x + (base_x - x) * sf
        y = y + (base_y - y) * sf
        x_coordinates[index] = x
        y_coordinates[index] = y

        # R uses 1-based A[x.matrix, y.matrix].  Preserve its expression order.
        x_matrix = math.ceil((x + 1.0) * resolution / (2.0 * 1.0))
        y_matrix = math.ceil((y + 1.0) * resolution / (2.0 * 1.0))
        if not (1 <= x_matrix <= resolution and 1 <= y_matrix <= resolution):
            raise AssertionError((index, x, y, x_matrix, y_matrix))
        matrix[x_matrix - 1, y_matrix - 1] += 1

    if int(matrix.sum()) != len(sequence):
        raise AssertionError("FCGR count does not equal sequence length")
    return CGRResult(matrix, x_coordinates, y_coordinates, sf, resolution)


def encode_cgr(sequences: Sequence[str], resolution: int = 16):
    """Return R-column-major FCGR rows and kaos-compatible coordinate objects."""
    results = [cgr(sequence, resolution) for sequence in sequences]
    if results:
        fcgr = np.stack([result.matrix.ravel(order="F") for result in results])
    else:
        fcgr = np.empty((0, resolution * resolution), dtype=np.int64)
    return fcgr, results


def load_author_feature_functions(source_path: Path):
    """Load only ANIA's pinned ``map_kmers`` and ``compute_props`` definitions."""
    source_path = Path(source_path)
    observed = sha256(source_path)
    if observed != AUTHOR_FEATURE_SHA256:
        raise ValueError(
            f"author feature source hash mismatch: {observed} != {AUTHOR_FEATURE_SHA256}"
        )
    tree = ast.parse(source_path.read_text())
    wanted = {"map_kmers", "compute_props"}
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    if {node.name for node in functions} != wanted:
        raise ValueError("pinned author feature functions were not both found")
    namespace = {"np": np}
    exec(
        compile(ast.Module(body=functions, type_ignores=[]), str(source_path), "exec"),
        namespace,
    )
    return namespace["map_kmers"], namespace["compute_props"]


def encode_ania_features(
    sequences: Sequence[str],
    author_feature_source: Path,
    property_table_path: Path,
    properties: Sequence[str] = DEFAULT_PROPERTIES,
    resolution: int = 16,
):
    """Build ANIA's 11x16x16 float32 tensor without R or rpy2."""
    require_python_hash_seed_zero()
    if tuple(properties) != DEFAULT_PROPERTIES:
        raise ValueError("property order differs from the pinned ANIA runtime")
    property_table_path = Path(property_table_path)
    observed = sha256(property_table_path)
    if observed != PROPERTY_TABLE_SHA256:
        raise ValueError(
            f"property table hash mismatch: {observed} != {PROPERTY_TABLE_SHA256}"
        )

    import pandas as pd

    fcgr, results = encode_cgr(sequences, resolution)
    map_kmers, compute_props = load_author_feature_functions(author_feature_source)
    kmer_maps = map_kmers(list(sequences), results, resolution)
    property_table = pd.read_csv(property_table_path, index_col="AminoAcid")
    channels = [fcgr.reshape(-1, resolution, resolution)]
    for property_id in properties:
        maps = compute_props(kmer_maps, property_table, property_id)
        matrix = np.zeros((len(sequences), resolution, resolution))
        for sequence_index, pixel_map in enumerate(maps):
            for (row, column), value in pixel_map.items():
                if not (0 <= row < resolution and 0 <= column < resolution):
                    raise AssertionError((sequence_index, row, column))
                matrix[sequence_index, row, column] = value
        channels.append(matrix)
    encoded = np.stack(channels, axis=1).astype(np.float32)
    expected_shape = (len(sequences), 11, resolution, resolution)
    if encoded.shape != expected_shape or not np.isfinite(encoded).all():
        raise AssertionError((encoded.shape, expected_shape))
    return encoded, fcgr, results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequences", required=True, type=Path)
    parser.add_argument("--ania-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    sequences = args.sequences.read_text().splitlines()
    features, fcgr, results = encode_ania_features(
        sequences,
        args.ania_root / "src/features/cgr_encoding.py",
        args.ania_root / "configs/AAindex_properties.csv",
    )
    args.output_dir.mkdir(parents=True)
    np.save(args.output_dir / "ania_encoded.npy", features)
    np.save(args.output_dir / "fcgr.npy", fcgr)
    np.savez(
        args.output_dir / "coordinates.npz",
        **{
            f"x_{index}": result.x
            for index, result in enumerate(results)
        },
        **{
            f"y_{index}": result.y
            for index, result in enumerate(results)
        },
    )


if __name__ == "__main__":
    main()
