"""
G*Power Clone Engine: One-Way ANOVA Power and Sample Size Engine
Test: ANOVA: Fixed effects, omnibus, one-way
"""

from typing import Dict, Any, Optional
from scipy.stats import f as f_dist, ncf


def validate_inputs(
    f_val: float,
    alpha: float,
    power: Optional[float],
    num_groups: int,
    mode: str,
    n_total: Optional[int] = None,
) -> Optional[str]:
    """
    Validate input parameters against G*Power's admissible ranges.
    Returns an error message string if invalid, or None if valid.
    """
    # Effect size f check
    if f_val <= 1e-06 or f_val >= 50.0:
        return "Effect size f is outside the admissible range (1e-06; 50)."

    # Alpha check
    if alpha <= 1e-07 or alpha >= 1.0:
        return "Alpha is outside the admissible range (1e-07; 1)."

    # Power check
    if mode == "a-priori":
        if power is None or power <= 1e-07 or power >= 1.0:
            return "Power is outside the admissible range (1e-07; 1)."
    elif power is not None:
        if power <= 1e-07 or power >= 1.0:
            return "Power is outside the admissible range (1e-07; 1)."

    # Number of groups check
    if num_groups < 2:
        return "There must be at least 2 groups."

    # Post-hoc total sample size check
    if mode == "post-hoc":
        if n_total is None:
            return "Total sample size (--n) is required for post-hoc mode."
        if n_total < 2 * num_groups:
            return "Total sample size must be at least 2 * num_groups."

    return None


def compute_post_hoc(
    f_val: float,
    alpha: float,
    num_groups: int,
    n_total: int
) -> Dict[str, Any]:
    """
    Calculate statistical power and related parameters given sample size N.
    """
    df1 = int(num_groups - 1)
    df2 = int(n_total - num_groups)
    ncp = float((f_val ** 2) * n_total)
    critical_f = float(f_dist.ppf(1.0 - alpha, df1, df2))
    actual_power = float(ncf.sf(critical_f, df1, df2, ncp))

    return {
        "n_total": int(n_total),
        "actual_power": actual_power,
        "critical": critical_f,
        "df1": df1,
        "df2": df2,
        "ncp": ncp,
    }


def compute_a_priori(
    f_val: float,
    alpha: float,
    target_power: float,
    num_groups: int
) -> Dict[str, Any]:
    """
    Iteratively find the smallest sample size N (as a multiple of k, with equal
    group sizes n_group >= 2) that achieves at least target_power.
    """
    def eval_n_group(n_grp: int) -> float:
        res = compute_post_hoc(f_val, alpha, num_groups, n_grp * num_groups)
        return res["actual_power"]

    # Minimum 2 participants per group
    low = 2
    if eval_n_group(low) >= target_power:
        return compute_post_hoc(f_val, alpha, num_groups, low * num_groups)

    # Exponential bracket search for upper bound
    high = 4
    while eval_n_group(high) < target_power:
        low = high
        high *= 2
        if high > 10_000_000:
            break

    # Binary search for minimal n_group
    best_n = high
    while low <= high:
        mid = (low + high) // 2
        if eval_n_group(mid) >= target_power:
            best_n = mid
            high = mid - 1
        else:
            low = mid + 1

    return compute_post_hoc(f_val, alpha, num_groups, best_n * num_groups)
