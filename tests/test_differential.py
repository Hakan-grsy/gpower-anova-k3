"""
Differential Testing Suite for G*Power ANOVA Clone vs Oracle (G*Power 3.1.9.7)
File: tests/test_differential.py
"""

import os
import sys
import csv
import json
import subprocess
import pytest

ORACLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "oracle", "vectors.csv")


def load_test_vectors():
    """Load all 30 oracle test vectors from CSV."""
    vectors = []
    with open(ORACLE_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            row["row_id"] = idx
            vectors.append(row)
    return vectors


VECTORS = load_test_vectors()
VALID_VECTORS = [v for v in VECTORS if v["status_or_error"] == "VALID"]
ERROR_VECTORS = [v for v in VECTORS if v["status_or_error"] != "VALID"]


def run_cli_subprocess(args_list):
    """Execute CLI in a separate subprocess, returning (exit_code, stdout_str, stderr_str)."""
    cmd = [sys.executable, "-m", "src.cli"] + args_list
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.parametrize("vector", VALID_VECTORS, ids=[f"row_{v['row_id']}_f={v['effect_size_f']}_a={v['alpha']}_p={v['power']}_k={v['num_groups']}" for v in VALID_VECTORS])
def test_valid_vector_differential(vector):
    """
    Test valid test vector against G*Power oracle:
    - Exit code must be 0
    - N total must be an EXACT 100% integer match
    - df1 and df2 must match exactly
    - ncp, critical_f, and actual_power must match within numerical tolerance (1e-4)
    """
    args = [
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", vector["effect_size_f"],
        "--alpha", vector["alpha"],
        "--power", vector["power"],
        "--num-groups", vector["num_groups"]
    ]

    ret, stdout, stderr = run_cli_subprocess(args)
    assert ret == 0, f"Expected returncode 0, got {ret}. Stderr: {stderr}"

    data = json.loads(stdout)

    expected_n = int(vector["n_total"])
    expected_df1 = int(vector["df1"])
    expected_df2 = int(vector["df2"])
    expected_ncp = float(vector["ncp"])
    expected_crit = float(vector["critical_f"])
    expected_power = float(vector["actual_power"])

    # 1. Total sample size N MUST MATCH 100% EXACTLY
    assert data["n_total"] == expected_n, (
        f"Row {vector['row_id']}: Sample size mismatch! Got {data['n_total']}, expected {expected_n}"
    )

    # 2. Degrees of freedom
    assert data["df1"] == expected_df1, f"df1 mismatch: {data['df1']} vs {expected_df1}"
    assert data["df2"] == expected_df2, f"df2 mismatch: {data['df2']} vs {expected_df2}"

    # 3. Noncentrality parameter (NCP)
    assert abs(data["ncp"] - expected_ncp) < 1e-4, f"ncp mismatch: {data['ncp']} vs {expected_ncp}"

    # 4. Critical F value
    assert abs(data["critical"] - expected_crit) < 1e-4, (
        f"critical F mismatch: {data['critical']} vs {expected_crit}"
    )

    # 5. Actual Power (at integer sample size N)
    assert abs(data["actual_power"] - expected_power) < 1e-4, (
        f"actual_power mismatch: {data['actual_power']} vs {expected_power}"
    )


@pytest.mark.parametrize("vector", ERROR_VECTORS, ids=[f"row_{v['row_id']}_error_test" for v in ERROR_VECTORS])
def test_error_vector_differential(vector):
    """
    Test error / edge cases against G*Power oracle:
    - Exit code must be non-zero (1)
    - Output must be JSON containing "error" key
    - Error message must match the expected G*Power error string
    """
    args = [
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", vector["effect_size_f"],
        "--alpha", vector["alpha"],
        "--power", vector["power"],
        "--num-groups", vector["num_groups"]
    ]

    ret, stdout, stderr = run_cli_subprocess(args)
    assert ret != 0, f"Expected non-zero exit code for invalid input, got {ret}"

    data = json.loads(stdout)
    assert "error" in data, f"JSON output does not contain 'error' key: {data}"

    raw_expected = vector["status_or_error"]
    assert raw_expected.startswith("ERROR: ")
    expected_msg = raw_expected[len("ERROR: "):].strip()

    assert data["error"] == expected_msg, (
        f"Error string mismatch! Got {data['error']!r}, expected {expected_msg!r}"
    )


def test_compliance_and_coverage_report():
    """
    Verify complete 100% test coverage across all 30 vectors in oracle/vectors.csv
    and generate compliance verification metrics.
    """
    assert len(VECTORS) == 30, f"Expected 30 vectors in oracle/vectors.csv, got {len(VECTORS)}"
    assert len(VALID_VECTORS) == 25, f"Expected 25 valid vectors, got {len(VALID_VECTORS)}"
    assert len(ERROR_VECTORS) == 5, f"Expected 5 error vectors, got {len(ERROR_VECTORS)}"

    n_matches = 0
    crit_matches = 0
    power_matches = 0

    for vec in VALID_VECTORS:
        args = [
            "--test", "anova-oneway",
            "--mode", "a-priori",
            "--f", vec["effect_size_f"],
            "--alpha", vec["alpha"],
            "--power", vec["power"],
            "--num-groups", vec["num_groups"]
        ]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret == 0
        data = json.loads(stdout)

        if data["n_total"] == int(vec["n_total"]):
            n_matches += 1
        if abs(data["critical"] - float(vec["critical_f"])) < 1e-4:
            crit_matches += 1
        if abs(data["actual_power"] - float(vec["actual_power"])) < 1e-4:
            power_matches += 1

    assert n_matches == 25, f"Expected 100% N match (25/25), achieved {n_matches}/25"
    assert crit_matches == 25, f"Expected 100% Critical F match, achieved {crit_matches}/25"
    assert power_matches == 25, f"Expected 100% Power match, achieved {power_matches}/25"

    print("\n" + "="*70)
    print(" G*POWER vs PYTHON CLONE DIFFERENTIAL TESTING REPORT")
    print("="*70)
    print(f" Total Oracle Vectors Tested: {len(VECTORS)}")
    print(f" Valid Vectors Tested:        {len(VALID_VECTORS)}")
    print(f" Error Boundary Cases Tested: {len(ERROR_VECTORS)}")
    print(f" Sample Size (N) Match Rate:  {n_matches}/{len(VALID_VECTORS)} (100.0%)")
    print(f" Critical F Value Match Rate: {crit_matches}/{len(VALID_VECTORS)} (100.0%)")
    print(f" Statistical Power Match Rate:{power_matches}/{len(VALID_VECTORS)} (100.0%)")
    print(" OVERALL RESULT: FULL STATISTICAL EQUIVALENCE ACHIEVED (PASS)")
    print("="*70)
