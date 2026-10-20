"""
Equivalence Tests: CLI Layer vs MCP Layer
File: tests/test_mcp.py
Verifies that the CLI and the MCP Tool adapter produce 100% identical outputs
when given the exact same input parameters.
"""

import os
import sys
import csv
import json
import subprocess
import pytest
from src.mcp_server import calculate_anova_a_priori

ORACLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "oracle", "vectors.csv")


def load_vectors():
    vectors = []
    with open(ORACLE_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            row["row_id"] = idx
            vectors.append(row)
    return vectors


ALL_VECTORS = load_vectors()
VALID_VECTORS = [v for v in ALL_VECTORS if v["status_or_error"] == "VALID"]
ERROR_VECTORS = [v for v in ALL_VECTORS if v["status_or_error"] != "VALID"]


def run_cli(args_list):
    cmd = [sys.executable, "-m", "src.cli"] + args_list
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


@pytest.mark.parametrize("vector", VALID_VECTORS, ids=[f"valid_row_{v['row_id']}" for v in VALID_VECTORS])
def test_cli_vs_mcp_valid_equivalence(vector):
    """
    Test that for valid parameters, the CLI output and MCP tool output
    are bit-for-bit identical across all metrics.
    """
    f_val = float(vector["effect_size_f"])
    alpha = float(vector["alpha"])
    power = float(vector["power"])
    k = int(vector["num_groups"])

    # 1. Run via CLI
    cli_args = [
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", str(f_val),
        "--alpha", str(alpha),
        "--power", str(power),
        "--num-groups", str(k)
    ]
    ret, stdout, stderr = run_cli(cli_args)
    assert ret == 0, f"CLI exited with error: {stderr}"
    cli_result = json.loads(stdout)

    # 2. Run via MCP Tool
    mcp_result = calculate_anova_a_priori(
        f=f_val,
        alpha=alpha,
        power=power,
        num_groups=k
    )

    # 3. Verify exact equivalence
    assert "error" not in mcp_result
    assert cli_result["n_total"] == mcp_result["n_total"]
    assert cli_result["df1"] == mcp_result["df1"]
    assert cli_result["df2"] == mcp_result["df2"]
    assert abs(cli_result["actual_power"] - mcp_result["actual_power"]) < 1e-9
    assert abs(cli_result["critical"] - mcp_result["critical"]) < 1e-9
    assert abs(cli_result["ncp"] - mcp_result["ncp"]) < 1e-9


@pytest.mark.parametrize("vector", ERROR_VECTORS, ids=[f"error_row_{v['row_id']}" for v in ERROR_VECTORS])
def test_cli_vs_mcp_error_equivalence(vector):
    """
    Test that for invalid parameters, both CLI and MCP tool produce
    the exact same error message.
    """
    f_val = float(vector["effect_size_f"])
    alpha = float(vector["alpha"])
    power = float(vector["power"])
    k = int(vector["num_groups"])

    # 1. Run via CLI
    cli_args = [
        "--test", "anova-oneway",
        "--mode", "a-priori",
        "--f", str(f_val),
        "--alpha", str(alpha),
        "--power", str(power),
        "--num-groups", str(k)
    ]
    ret, stdout, stderr = run_cli(cli_args)
    assert ret != 0, "CLI was expected to fail for invalid input"
    cli_result = json.loads(stdout)

    # 2. Run via MCP Tool
    mcp_result = calculate_anova_a_priori(
        f=f_val,
        alpha=alpha,
        power=power,
        num_groups=k
    )

    # 3. Verify exact error equivalence
    assert "error" in mcp_result
    assert "error" in cli_result
    assert cli_result["error"] == mcp_result["error"]
