#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 2: Keşif ve Parmak İzi (Reconnaissance)
Hedef sitenin teknoloji yığınını ve savunmasız sürümlerini tespit eder.
"""

import sys
import re
import requests
from utils import (
    print_phase_banner, check_target, info, success, warning, error,
    parse_target_arg, save_results, DEFAULT_HEADERS, is_vulnerable, Colors
)

def analyze_headers(target_url):
    """HTTP yanıt başlıklarını analiz eder"""
    info("HTTP Header Analizi başlatılıyor...")
    try:
        resp = requests.head(target_url, headers=DEFAULT_HEADERS, timeout=5)
        headers = resp.headers
        
        results = {
            "server": headers.get("Server", "Bilinmiyor"),
            "x_powered_by": headers.get("X-Powered-By", "Bulunamadı"),
            "nextjs_version": None,
            "suspicious_headers": []
        }
        
        # Next.js tespit
        if "Next.js" in results["x_powered_by"] or "Next.js" in results["server"]:
            success("Next.js tespit edildi!")
            # Sürüm tespiti başlıkta varsa (genelde olmaz ama kontrol edelim)
            version_match = re.search(r"Next\.js\s*([\d\.]+)", results["x_powered_by"])
            if version_match:
                results["nextjs_version"] = version_match.group(1)
                
        # Özel Next.js başlıkları
        for key in headers:
            if key.lower().startswith("x-nextjs"):
                results["suspicious_headers"].append(f"{key}: {headers[key]}")
                
        return results
    except Exception as e:
        error(f"Header analizi başarısız: {e}")
        return None

def find_framework_fingerprints(target_url):
    """Statik dosyalar üzerinden framework parmak izi tespiti"""
    info("Framework Parmak İzi Tespiti (buildManifest.js vb.)...")
    
    fingerprints = {
        "build_manifest_found": False,
        "nextjs_version_from_manifest": None,
        "react_version": None,
        "is_app_router": False
    }
    
    # Ana sayfayı çek
    try:
        resp = requests.get(target_url, headers=DEFAULT_HEADERS, timeout=5)
        html = resp.text
        
        # Next.js statik dosyalarını ara (/_next/static/...)
        next_static_patterns = re.findall(r'/_next/static/(.*?)\.js', html)
        if next_static_patterns:
            success(f"Next.js statik asset path'leri bulundu: {len(next_static_patterns)} adet")
            
        # App Router mi Pages Router mi?
        if "_next/static/chunks/app/" in html or "app-pages-internals" in html:
            fingerprints["is_app_router"] = True
            success("Next.js App Router (RSC destekler) kullanılıyor!")
            
        # React Sürümünü bulmaya çalış (bundle içinde)
        # Gerçek bir taramada bundle'lar indirilir ve "React v19.0.0" gibi stringler aranır
        # Eğitim amaçlı, basit bir regex kullanıyoruz
        react_match = re.search(r'react@([\d\.]+)', html) or re.search(r'React v([\d\.]+)', html)
        if react_match:
            fingerprints["react_version"] = react_match.group(1)
            success(f"React Sürümü bulundu: {fingerprints['react_version']}")
            
    except Exception as e:
        warning(f"Statik analizde hata (devam ediliyor): {e}")
        
    return fingerprints

def check_rsc_endpoint(target_url):
    """Server Actions/RSC endpoint'lerini tespit eder"""
    info("RSC / Server Actions Endpoint Keşfi...")
    
    endpoints = []
    
    # Temel RSC kontrolü (text/x-component payload'ı göndererek)
    headers = DEFAULT_HEADERS.copy()
    headers["Content-Type"] = "text/x-component"
    headers["Next-Action"] = "dummy-action-id"  # RSC'yi tetiklemek için sahte ID
    
    try:
        # Ana sayfaya boş RSC POST isteği
        resp = requests.post(target_url, headers=headers, data="[]", timeout=5)
        
        # Yanıt Flight formatında mı? Veya Server Action hatası mı?
        if "next-action" in resp.headers.get("x-powered-by", "").lower() or \
           "text/x-component" in resp.headers.get("content-type", "").lower() or \
           resp.status_code in [400, 500] and ("Server Action" in resp.text or "Error" in resp.text):
            
            success("RSC Endpoint bulundu: / (POST text/x-component)")
            endpoints.append({
                "path": "/",
                "method": "POST",
                "content_type": "text/x-component",
                "notes": "Server Action / RSC Uyumlu"
            })
            
    except Exception as e:
        warning(f"RSC kontrolünde hata: {e}")
        
    return endpoints

def run_recon(target_url):
    """Tüm keşif sürecini yönetir"""
    print_phase_banner(1, "Keşif ve Parmak İzi (Reconnaissance)")
    
    # 1. Hedef Doğrulama
    health_data = check_target(target_url)
    if not health_data:
        error("Hedef ulaşılamaz, keşif durduruluyor.")
        sys.exit(1)
        
    # Health endpoint'ten gelen sürümleri alalım (bizim test sitemiz sızdırıyor)
    actual_next = health_data.get("version", {}).get("next")
    actual_react = health_data.get("version", {}).get("react")
        
    # 2. Header Analizi
    header_results = analyze_headers(target_url)
    
    # 3. Statik Analiz
    static_results = find_framework_fingerprints(target_url)
    
    # 4. RSC Endpoint Tespiti
    rsc_endpoints = check_rsc_endpoint(target_url)
    
    # Sonuçları Derle
    print("\n" + "="*50)
    print(f"{Colors.BOLD}{Colors.CYAN}--- KEŞİF SONUÇLARI ---{Colors.RESET}")
    print("="*50)
    
    target_next = actual_next or header_results.get("nextjs_version") or "15.0.3" # Fallback for demo
    target_react = actual_react or static_results.get("react_version") or "19.0.0" # Fallback for demo
    
    print(f"{Colors.BOLD}Hedef:{Colors.RESET} {target_url}")
    print(f"{Colors.BOLD}Next.js Sürümü:{Colors.RESET} {target_next}")
    print(f"{Colors.BOLD}React Sürümü:{Colors.RESET} {target_react}")
    
    if rsc_endpoints:
        print(f"{Colors.BOLD}RSC Durumu:{Colors.RESET} Aktif ({len(rsc_endpoints)} endpoint)")
    else:
        print(f"{Colors.BOLD}RSC Durumu:{Colors.RESET} Belirsiz veya Pasif")
        
    # Savunmasızlık Kontrolü
    print("\n" + "="*50)
    if is_vulnerable(target_react, target_next):
        print(f"{Colors.BG_RED}{Colors.WHITE}[ VULNERABLE ]{Colors.RESET} "
              f"{Colors.RED}Hedef CVE-2025-55182'den etkileniyor!{Colors.RESET}")
        print(f"Savunmasız React: {target_react} | Savunmasız Next.js: {target_next}")
    else:
        print(f"{Colors.BG_GREEN}{Colors.WHITE}[ SECURE ]{Colors.RESET} "
              f"{Colors.GREEN}Hedef yamalanmış görünüyor.{Colors.RESET}")
        
    # Raporu Kaydet
    report = {
        "target": target_url,
        "timestamp": health_data.get("timestamp"),
        "versions": {"next": target_next, "react": target_react},
        "vulnerable": is_vulnerable(target_react, target_next),
        "rsc_endpoints": rsc_endpoints,
        "raw_headers": header_results
    }
    save_results("01_recon_report.json", report)

if __name__ == "__main__":
    args = parse_target_arg()
    run_recon(args.target)
