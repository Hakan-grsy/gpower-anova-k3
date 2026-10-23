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
    groups: int,  # Sözleşmeye göre num_groups -> groups oldu
    mode: str,
    n_total: Optional[int] = None,
) -> Optional[Dict[str, str]]:
    """
    Validate input parameters against G*Power's admissible ranges.
    Returns a contract-compliant error dictionary if invalid, or None if valid.
    """
    # Effect size f check
    if f_val is None or f_val <= 1e-06 or f_val >= 50.0:
        return {"error": "Effect size f is outside the admissible range (1e-06; 50).", "code": "OUT_OF_RANGE", "field": "f"}

    # Alpha check
    if alpha is None or alpha <= 1e-07 or alpha >= 1.0:
        return {"error": "Alpha is outside the admissible range (1e-07; 1).", "code": "OUT_OF_RANGE", "field": "alpha"}

    # Number of groups check
    if groups is None or groups < 2:
        return {"error": "There must be at least 2 groups.", "code": "OUT_OF_RANGE", "field": "groups"}

    # Power check for a-priori
    if mode == "a-priori":
        if power is None:
            return {"error": "Power is missing for a-priori mode.", "code": "MISSING_PARAM", "field": "power"}
        if power <= 1e-07 or power >= 1.0:
            return {"error": "Power is outside the admissible range (1e-07; 1).", "code": "OUT_OF_RANGE", "field": "power"}
            
    # Power check for general existence
    elif power is not None:
        if power <= 1e-07 or power >= 1.0:
            return {"error": "Power is outside the admissible range (1e-07; 1).", "code": "OUT_OF_RANGE", "field": "power"}

    # Post-hoc total sample size check
    if mode == "post-hoc":
        if n_total is None:
            return {"error": "Total sample size (--n_total) is required for post-hoc mode.", "code": "MISSING_PARAM", "field": "n_total"}
        if n_total < 2 * groups:
            return {"error": "Total sample size must be at least 2 * groups.", "code": "OUT_OF_RANGE", "field": "n_total"}

    return None


def compute_post_hoc(
    f_val: float,
    alpha: float,
    groups: int,
    n_total: int
) -> Dict[str, Any]:
    """
    Calculate statistical power and related parameters given sample size N.
    """
    df1 = int(groups - 1)
    df2 = int(n_total - groups)
    ncp = float((f_val ** 2) * n_total)
    critical_f = float(f_dist.ppf(1.0 - alpha, df1, df2))
    actual_power = float(ncf.sf(critical_f, df1, df2, ncp))

    # Çıktı anahtarları sözleşmeye uyarlandı ("critical" -> "critical_f", "actual_power" -> "power")
    return {
        "ncp": ncp,
        "critical_f": critical_f,
        "df1": df1,
        "df2": df2,
        "power": actual_power,
    }


def compute_a_priori(
    f_val: float,
    alpha: float,
    target_power: float,
    groups: int
) -> Dict[str, Any]:
    """
    Iteratively find the smallest sample size N (as a multiple of k, with equal
    group sizes n_group >= 2) that achieves at least target_power.
    """
    def eval_n_group(n_grp: int) -> float:
        res = compute_post_hoc(f_val, alpha, groups, n_grp * groups)
        return res["power"]

    # Minimum 2 participants per group
    low = 2
    if eval_n_group(low) >= target_power:
        best_n = low
    else:
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

    # Hesaplanan best_n ile sonuçları sözleşme formatında dönüyoruz
    final_n_total = best_n * groups
    post_res = compute_post_hoc(f_val, alpha, groups, final_n_total)
    
    return {
        "ncp": post_res["ncp"],
        "critical_f": post_res["critical_f"],
        "df1": post_res["df1"],
        "df2": post_res["df2"],
        "n_total": int(final_n_total),
        "actual_power": post_res["power"],
    }