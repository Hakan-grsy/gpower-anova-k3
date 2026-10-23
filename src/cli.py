#!/usr/bin/env python3
"""
CLI entry point for G*Power Clone
Contract: 1.0.0
"""

import sys
import json
import argparse
from src.engine import validate_inputs, compute_a_priori, compute_post_hoc

def main():
    # Sözleşme Kuralı 2.2: Sürüm sorgusu
    if "--version" in sys.argv:
        print(json.dumps({"contract_version": "1.0.0", "name": "K3-Takimi", "engine": "Python 3.12"}))
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--test", type=str)
    parser.add_argument("--mode", type=str)
    parser.add_argument("--f", type=float)
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--power", type=float)
    parser.add_argument("--groups", type=int)   # num-groups yerine sözleşme gereği groups oldu
    parser.add_argument("--n_total", type=int)  # Sözleşme gereği post-hoc için n_total oldu

    # Tanınmayan parametreleri yakalamak için parse_known_args kullanıyoruz
    args, unknown = parser.parse_known_args()

    # Sözleşme Kuralı 2.4: Tanınmayan alan hatası (UNKNOWN_PARAM, Çıkış Kodu: 2)
    if unknown:
        field = unknown[0].lstrip('-')
        print(json.dumps({"error": f"Taninmayan parametre: {unknown[0]}", "code": "UNKNOWN_PARAM", "field": field}))
        sys.exit(2)

    # Sözleşme Kuralı 2.4: Eksik parametre ve desteklenmeyen test hataları (Çıkış Kodu: 2)
    if args.test is None:
        print(json.dumps({"error": "--test parametresi eksik", "code": "MISSING_PARAM", "field": "test"}))
        sys.exit(2)
        
    if args.test != "anova-oneway":
        print(json.dumps({"error": f"Desteklenmeyen test: '{args.test}'", "code": "UNSUPPORTED", "field": "test"}))
        sys.exit(2)

    if args.mode is None:
        print(json.dumps({"error": "--mode parametresi eksik", "code": "MISSING_PARAM", "field": "mode"}))
        sys.exit(2)

    if args.mode not in ("a-priori", "post-hoc"):
        print(json.dumps({"error": f"Desteklenmeyen mod: '{args.mode}'", "code": "UNSUPPORTED", "field": "mode"}))
        sys.exit(2)

    if args.f is None:
        print(json.dumps({"error": "--f parametresi eksik", "code": "MISSING_PARAM", "field": "f"}))
        sys.exit(2)
    if args.alpha is None:
        print(json.dumps({"error": "--alpha parametresi eksik", "code": "MISSING_PARAM", "field": "alpha"}))
        sys.exit(2)
    if args.groups is None:
        print(json.dumps({"error": "--groups parametresi eksik", "code": "MISSING_PARAM", "field": "groups"}))
        sys.exit(2)

    # Motor üzerinden değer doğrulama (engine.py artık sözleşme uyumlu JSON döndürüyor)
    err = validate_inputs(
        f_val=args.f,
        alpha=args.alpha,
        power=args.power,
        groups=args.groups,
        mode=args.mode,
        n_total=args.n_total
    )
    
    if err is not None:
        print(json.dumps(err))
        sys.exit(2)

    # Hesaplama Aşaması
    try:
        if args.mode == "a-priori":
            result = compute_a_priori(
                f_val=args.f,
                alpha=args.alpha,
                target_power=args.power,
                groups=args.groups
            )
        else:
            result = compute_post_hoc(
                f_val=args.f,
                alpha=args.alpha,
                groups=args.groups,
                n_total=args.n_total
            )
        
        print(json.dumps(result))
        sys.exit(0) # Başarılı çıkış

    except Exception as e:
        # İç hata durumunda çıkış kodu 1 olmalı
        print(json.dumps({"error": "Hesaplama motoru ic hatasi", "code": "INTERNAL_ERROR", "field": "none"}))
        sys.exit(1)

if __name__ == "__main__":
    main()