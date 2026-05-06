#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Yardımcı Fonksiyonlar (utils.py)
CVE-2025-55182 Eğitim Laboratuvarı

Tüm saldırı scriptleri tarafından kullanılan
ortak fonksiyonlar ve sabitler.
"""

import sys
import time
import json
import requests
import urllib3
import os
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# Renkli Çıktı (ANSI renk kodları)
# ============================================

class Colors:
    """ANSI renk kodları"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"

def info(msg):
    """Bilgi mesajı [*]"""
    print(f"{Colors.BLUE}[*]{Colors.RESET} {msg}")

def success(msg):
    """Başarı mesajı [+]"""
    print(f"{Colors.GREEN}[+]{Colors.RESET} {msg}")

def warning(msg):
    """Uyarı mesajı [!]"""
    print(f"{Colors.YELLOW}[!]{Colors.RESET} {msg}")

def error(msg):
    """Hata mesajı [-]"""
    print(f"{Colors.RED}[-]{Colors.RESET} {msg}")

def critical(msg):
    """Kritik mesaj [!!]"""
    print(f"{Colors.BG_RED}{Colors.WHITE}[!!]{Colors.RESET} {Colors.RED}{Colors.BOLD}{msg}{Colors.RESET}")

def section(title):
    """Bölüm başlığı"""
    width = 60
    print()
    print(f"{Colors.CYAN}{'═' * width}{Colors.RESET}")
    print(f"{Colors.CYAN}  {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * width}{Colors.RESET}")
    print()

# ============================================
# Banner
# ============================================

BANNER = f"""
{Colors.RED}
██████╗ ███████╗ █████╗  ██████╗████████╗██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗     
██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚════██╗██╔════╝██║  ██║██╔════╝██║     ██║     
██████╔╝█████╗  ███████║██║        ██║    █████╔╝███████╗███████║█████╗  ██║     ██║     
██╔══██╗██╔══╝  ██╔══██║██║        ██║   ██╔═══╝ ╚════██║██╔══██║██╔══╝  ██║     ██║     
██║  ██║███████╗██║  ██║╚██████╗   ██║   ███████╗███████║██║  ██║███████╗███████╗███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
{Colors.RESET}
{Colors.YELLOW}  CVE-2025-55182 | Pre-Auth RCE via React Server Components Flight Protocol
  CVSS 10.0 — Critical | Eğitim Amaçlı Laboratuvar{Colors.RESET}
{Colors.DIM}  ⚠️  Yalnızca eğitim ve araştırma amaçlıdır — yetkisiz kullanım yasaktır{Colors.RESET}
"""

def print_banner():
    """Ana banner'ı yazdır"""
    print(BANNER)

def print_phase_banner(phase_num, title, cve=None):
    """Faz banner'ı yazdır"""
    cve_str = f" | {cve}" if cve else ""
    print(f"""
{Colors.MAGENTA}┌──────────────────────────────────────────────────────────┐
│  Faz {phase_num}: {title}{cve_str:<{40 - len(title)}}│
└──────────────────────────────────────────────────────────┘{Colors.RESET}
""")

# ============================================
# HTTP Yardımcıları
# ============================================

PROXIES = {}

def is_tor_active():
    """Tor bağlantısını kontrol eder"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', 9050))
        s.close()
        return True
    except:
        return False

def enable_tor(strict=True):
    """Tor proxy'sini etkinleştir (SOCKS5)"""
    global PROXIES
    tor_proxy = "socks5h://127.0.0.1:9050"
    
    if not is_tor_active():
        if strict:
            error("Tor bağlantısı sağlanamadı (127.0.0.1:9050). Tor'un kurulu ve çalışır olduğundan emin olun.")
            import sys
            sys.exit(1)
        else:
            return False

    PROXIES = {
        "http": tor_proxy,
        "https": tor_proxy
    }
    # Environment variables for direct requests calls in other modules
    os.environ['HTTP_PROXY'] = tor_proxy
    os.environ['HTTPS_PROXY'] = tor_proxy
    info(f"Tor Proxy etkinleştirildi: {tor_proxy}")
    return True

def disable_tor():
    """Tor proxy'sini devre dışı bırakır"""
    global PROXIES
    PROXIES = {}
    if 'HTTP_PROXY' in os.environ:
        del os.environ['HTTP_PROXY']
    if 'HTTPS_PROXY' in os.environ:
        del os.environ['HTTPS_PROXY']
    info("Tor Proxy devre dışı bırakıldı (Doğrudan bağlantı).")

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def check_target(target_url, timeout=5):
    """
    Hedefin erişilebilir olup olmadığını kontrol et.
    Önce /api/health dener, JSON değilse veya yoksa ana sayfaya (/) bakar.
    """
    health_url = f"{target_url.rstrip('/')}/api/health"
    try:
        # Önce health endpoint'i dene
        resp = requests.get(health_url, headers=DEFAULT_HEADERS, timeout=timeout, verify=False, proxies=PROXIES)
        if resp.status_code == 200:
            try:
                data = resp.json()
                success(f"Hedef erişilebilir: {target_url}")
                success(f"Servis: {data.get('service', 'unknown')}")
                success(f"Next.js: {data.get('version', {}).get('next', '?')}")
                success(f"React: {data.get('version', {}).get('react', '?')}")
                success(f"RSC: {'Aktif' if data.get('rsc') else 'Pasif'}")
                return data
            except json.JSONDecodeError:
                pass # JSON değilse ana sayfayı denemeye geç
                
    except Exception as e:
        pass # Hata olursa ana sayfayı denemeye geç
        
    # Health endpoint başarısız olduysa ana sayfaya bak
    try:
        resp = requests.get(target_url, headers=DEFAULT_HEADERS, timeout=timeout, verify=False, proxies=PROXIES)
        if resp.status_code == 200:
            success(f"Hedef erişilebilir (Ana sayfa): {target_url}")
            return {"status": "ok", "service": "unknown", "version": {}}
        else:
            error(f"Hedef yanıt verdi ama beklenmeyen kod: {resp.status_code}")
            return None
    except requests.ConnectionError:
        error(f"Hedefe bağlanılamıyor: {target_url}")
        return None
    except requests.Timeout:
        error(f"Hedef yanıt vermedi (timeout: {timeout}s)")
        return None
    except Exception as e:
        error(f"Beklenmeyen hata: {e}")
        return None

def timed_request(method, url, **kwargs):
    """
    Zamanlı HTTP isteği gönder.
    Yanıt süresini milisaniye olarak döndürür.
    """
    kwargs.setdefault("headers", DEFAULT_HEADERS)
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("proxies", PROXIES)

    start = time.time()
    try:
        kwargs.setdefault("verify", False)
        resp = requests.request(method, url, **kwargs)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return resp, elapsed_ms
    except Exception as e:
        elapsed_ms = round((time.time() - start) * 1000, 2)
        return None, elapsed_ms

def save_results(filename, data):
    """Sonuçları JSON dosyasına kaydet"""
    filepath = f"results/{filename}"
    import os
    os.makedirs("results", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    success(f"Sonuçlar kaydedildi: {filepath}")
    return filepath

# ============================================
# Savunmasız Sürüm Kontrolü
# ============================================

VULNERABLE_REACT = ["19.0.0", "19.1.0", "19.1.1", "19.2.0"]
VULNERABLE_NEXT = [
    "15.0.0", "15.0.1", "15.0.2", "15.0.3", "15.0.4",
    "15.1.0", "15.1.1", "15.1.2", "15.1.3", "15.1.4",
    "15.1.5", "15.1.6", "15.1.7", "15.1.8",
    "15.2.0", "15.2.1", "15.2.2", "15.2.3", "15.2.4", "15.2.5",
    "15.3.0", "15.3.1", "15.3.2", "15.3.3", "15.3.4", "15.3.5",
    "15.4.0", "15.4.1", "15.4.2", "15.4.3", "15.4.4",
    "15.4.5", "15.4.6", "15.4.7",
    "15.5.0", "15.5.1", "15.5.2", "15.5.3", "15.5.4",
    "15.5.5", "15.5.6",
    "16.0.0", "16.0.1", "16.0.2", "16.0.3", "16.0.4",
    "16.0.5", "16.0.6",
]

def is_vulnerable(react_version=None, next_version=None):
    """Sürümün savunmasız olup olmadığını kontrol et"""
    vuln = False
    if react_version and react_version in VULNERABLE_REACT:
        vuln = True
    if next_version and next_version in VULNERABLE_NEXT:
        vuln = True
    return vuln

# ============================================
# Argüman Ayrıştırma
# ============================================

def parse_target_arg():
    """Komut satırından --target argümanını ayrıştır"""
    import argparse
    parser = argparse.ArgumentParser(
        description="React2Shell — CVE-2025-55182 Eğitim Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--target", "-t",
        default="http://localhost:3000",
        help="Hedef URL (varsayılan: http://localhost:3000)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Sonuç dosyası adı (varsayılan: otomatik)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaylı çıktı"
    )
    parser.add_argument(
        "--tor",
        action="store_true",
        help="Tor proxy kullan (SOCKS5: 127.0.0.1:9050)"
    )
    args = parser.parse_args()
    if args.tor:
        enable_tor()
    return args

def timestamp():
    """Şu anki zaman damgası"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
