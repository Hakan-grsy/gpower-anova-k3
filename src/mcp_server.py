"""
Model Context Protocol (MCP) Server Adapter for G*Power Clone
Exposes G*Power ANOVA Omnibus A Priori calculation as an MCP Tool.
Note: This is a thin adapter over src.engine; no calculation logic is duplicated.
"""

import sys
import json
from typing import Dict, Any, Union
from src.engine import validate_inputs, compute_a_priori

# Try importing official MCP 2.x server; provide fallback for environments without MCP SDK
try:
    from mcp.server.mcpserver import MCPServer
    HAS_MCP = True
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
        HAS_MCP = True
    except ImportError:
        HAS_MCP = False


def calculate_anova_a_priori(
    f: float,
    alpha: float,
    power: float,
    num_groups: int
) -> Dict[str, Any]:
    """
    Calculate required sample size and statistical parameters for One-Way ANOVA
    Omnibus test (A Priori power analysis) with balanced group allocation.

    Args:
        f: Cohen's effect size f (must be in open range 1e-6 < f < 50)
        alpha: Significance level / Type I error rate (must be in open range 1e-7 < alpha < 1)
        power: Desired statistical power 1 - beta (must be in open range 1e-7 < power < 1)
        num_groups: Number of independent groups k (integer >= 2)

    Returns:
        Dict containing:
            - n_total (int): Total required sample size across all groups (multiple of k)
            - actual_power (float): Achieved statistical power with integer sample size
            - critical (float): Critical F statistic value
            - df1 (int): Numerator degrees of freedom (k - 1)
            - df2 (int): Denominator / error degrees of freedom (N - k)
            - ncp (float): Noncentrality parameter lambda (f^2 * N)
        Or dict with 'error' key if input parameters are invalid.
    """
    error = validate_inputs(
        f_val=f,
        alpha=alpha,
        power=power,
        num_groups=num_groups,
        mode="a-priori"
    )
    if error is not None:
        return {"error": error}

    return compute_a_priori(
        f_val=f,
        alpha=alpha,
        target_power=power,
        num_groups=num_groups
    )


# Initialize MCP server and register tool if MCP library is installed
if HAS_MCP:
    server = MCPServer(
        name="gpower-anova-server",
        instructions="G*Power One-Way ANOVA Power Analysis MCP Server"
    )

    @server.tool(
        name="calculate_anova_a_priori",
        description="Compute A Priori required sample size and statistical power for One-Way ANOVA omnibus F-test"
    )
    def mcp_tool_calculate_anova_a_priori(
        f: float,
        alpha: float,
        power: float,
        num_groups: int
    ) -> Dict[str, Any]:
        return calculate_anova_a_priori(f=f, alpha=alpha, power=power, num_groups=num_groups)


def run_stdio_server():
    """Run MCP server in stdio mode."""
    if not HAS_MCP:
        print(json.dumps({"error": "MCP SDK is not installed"}))
        sys.exit(1)
    server.run()


if __name__ == "__main__":
    run_stdio_server()
