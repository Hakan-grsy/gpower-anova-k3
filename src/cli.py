#!/usr/bin/env python3
"""
CLI entry point for G*Power Clone
Contract:
  --test anova-oneway --mode <a-priori|post-hoc> --f <effect_size>
  --alpha <alpha> --power <power> --num-groups <k> [--n <n_total>]
"""

import sys
import json
import argparse
from typing import Optional
from src.engine import validate_inputs, compute_a_priori, compute_post_hoc


class JsonArgumentParser(argparse.ArgumentParser):
    """
    Custom ArgumentParser that outputs a single-line JSON error
    instead of printing usage to stderr on syntax/parsing errors.
    """
    def error(self, message):
        print(json.dumps({"error": f"Invalid arguments: {message}"}))
        sys.exit(1)


def parse_args():
    parser = JsonArgumentParser(
        description="G*Power Clone: One-Way ANOVA Power and Sample Size Calculator",
        add_help=False
    )
    parser.add_argument("--help", "-h", action="store_true", help="Show help")
    parser.add_argument("--test", type=str, required=False, default="anova-oneway",
                        help="Statistical test family / type (default: anova-oneway)")
    parser.add_argument("--mode", type=str, required=False, default="a-priori",
                        help="Analysis mode: 'a-priori' or 'post-hoc'")
    parser.add_argument("--f", type=float, required=False, help="Effect size f")
    parser.add_argument("--alpha", type=float, required=False, help="Alpha level")
    parser.add_argument("--power", type=float, required=False, help="Target power (1 - beta)")
    parser.add_argument("--num-groups", type=int, required=False, help="Number of groups (k)")
    parser.add_argument("--n", type=int, required=False, default=None,
                        help="Total sample size (for post-hoc mode)")

    return parser.parse_args()


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(json.dumps({
            "usage": "--test anova-oneway --mode <a-priori|post-hoc> --f <effect_size> --alpha <alpha> --power <power> --num-groups <k> [--n <n_total>]"
        }))
        sys.exit(0)

    try:
        args = parse_args()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if args.test != "anova-oneway":
        print(json.dumps({"error": f"Unsupported test: '{args.test}'. Only 'anova-oneway' is supported."}))
        sys.exit(1)

    if args.mode not in ("a-priori", "post-hoc"):
        print(json.dumps({"error": f"Unsupported mode: '{args.mode}'. Must be 'a-priori' or 'post-hoc'."}))
        sys.exit(1)

    # Check for required numerical arguments
    if args.f is None:
        print(json.dumps({"error": "Missing required argument: --f"}))
        sys.exit(1)
    if args.alpha is None:
        print(json.dumps({"error": "Missing required argument: --alpha"}))
        sys.exit(1)
    if args.num_groups is None:
        print(json.dumps({"error": "Missing required argument: --num-groups"}))
        sys.exit(1)

    err = validate_inputs(
        f_val=args.f,
        alpha=args.alpha,
        power=args.power,
        num_groups=args.num_groups,
        mode=args.mode,
        n_total=args.n
    )
    if err is not None:
        print(json.dumps({"error": err}))
        sys.exit(1)

    try:
        if args.mode == "a-priori":
            result = compute_a_priori(
                f_val=args.f,
                alpha=args.alpha,
                target_power=args.power,
                num_groups=args.num_groups
            )
        else:
            result = compute_post_hoc(
                f_val=args.f,
                alpha=args.alpha,
                num_groups=args.num_groups,
                n_total=args.n
            )
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {str(e)}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
