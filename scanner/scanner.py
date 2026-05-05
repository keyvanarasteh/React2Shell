#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell (CVE-2025-55182) - Pentest Scanner
Bu araç, verilen hedeflerin React Server Components (RSC) Flight
Protokolü açığına karşı gerçek dünyada zafiyet barındırıp barındırmadığını
tespit etmek için tasarlanmıştır.

Özellikler:
- Statik Bundle Analizi (React ve Next.js tam sürüm tespiti)
- RSC/Server Action Endpoint Keşfi
- Header Analizi
"""

import sys
import argparse
import requests
import urllib3
import re
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from colorama import init, Fore, Style

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class Scanner:
    def __init__(self, target, verbose=False):
        self.target = target.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": "React2Shell-Scanner/1.0 (Pentest)",
            "Accept": "*/*"
        })
        self.results = {
            "url": self.target,
            "is_nextjs": False,
            "nextjs_version": None,
            "react_version": None,
            "rsc_enabled": False,
            "vulnerable": False,
            "details": []
        }
        
        # Bilinen savunmasız sürümler
        self.vuln_react = ["19.0.0", "19.1.0", "19.1.1", "19.2.0"]
        self.vuln_next = [
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

    def log(self, msg, level="info"):
        if level == "info" and self.verbose:
            print(f"[*] {msg}")
        elif level == "success":
            print(f"{Fore.GREEN}[+] {msg}")
        elif level == "warning":
            print(f"{Fore.YELLOW}[!] {msg}")
        elif level == "error":
            print(f"{Fore.RED}[-] {msg}")

    def add_detail(self, detail):
        self.results["details"].append(detail)
        self.log(detail, "info")

    def analyze_headers(self):
        """Header'lardan Next.js/React izlerini arar"""
        try:
            resp = self.session.head(self.target, timeout=10)
            headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
            
            x_powered_by = headers.get("x-powered-by", "")
            if "next.js" in x_powered_by:
                self.results["is_nextjs"] = True
                self.add_detail("Header 'X-Powered-By' Next.js işaret ediyor.")
                
                # Sürüm var mı kontrol et (Bazen X-Powered-By: Next.js 15.0.3 yazar)
                m = re.search(r'next\.js\s*([\d\.]+)', x_powered_by)
                if m:
                    self.results["nextjs_version"] = m.group(1)
                    self.add_detail(f"Header üzerinden Next.js sürümü tespit edildi: {m.group(1)}")

            if any(k.startswith("x-nextjs") for k in headers):
                self.results["is_nextjs"] = True
                self.add_detail("Özel 'X-NextJS-*' header'ları tespit edildi.")
                
            # Cookie kontrolü (Next.js spesifik cookie'ler)
            set_cookie = headers.get("set-cookie", "")
            if "__prerender_bypass" in set_cookie or "x-invoke-path" in headers:
                self.results["is_nextjs"] = True
                self.add_detail("Next.js özel cookie/header izleri bulundu.")
                
        except Exception as e:
            self.log(f"Header analizi hatası: {str(e)}", "error")

    def fetch_static_bundles(self):
        """HTML'i indirip statik JS bundle'larını analiz eder"""
        try:
            resp = self.session.get(self.target, timeout=10)
            html = resp.text
            
            # Next.js App Router kontrolü
            if "_next/static/chunks/app/" in html or "app-pages-internals" in html or "self.__next_f" in html:
                self.results["is_nextjs"] = True
                self.results["rsc_enabled"] = True
                self.add_detail("Next.js App Router izleri bulundu (RSC Aktif).")
            # Next.js Pages Router (Standart) kontrolü
            elif 'id="__NEXT_DATA__"' in html or "_next/static" in html:
                self.results["is_nextjs"] = True
                self.add_detail("Next.js Pages Router veya statik dosya yapısı tespit edildi.")

            # build-manifest.json gibi Next.js spesifik dosyaları kontrol et (Kesin kanıt)
            if not self.results["is_nextjs"]:
                try:
                    manifest_resp = self.session.get(urljoin(self.target, "/_next/build-manifest.json"), timeout=5)
                    if manifest_resp.status_code == 200 and "pages" in manifest_resp.text:
                        self.results["is_nextjs"] = True
                        self.add_detail("/_next/build-manifest.json dosyasına ulaşıldı. Framework kesinlikle Next.js.")
                except Exception:
                    pass

            # JS bundle yollarını çıkar
            js_files = re.findall(r'src="(/_next/static/[^"]+\.js)"', html)
            js_files = list(set(js_files)) # Deduplicate
            
            if js_files:
                self.add_detail(f"{len(js_files)} adet statik JS dosyası bulundu. Sürüm analizi yapılıyor...")
                self.extract_versions_from_js(js_files)
                
        except Exception as e:
            self.log(f"Statik bundle analizi hatası: {str(e)}", "error")

    def extract_versions_from_js(self, js_files):
        """İndirilen JS dosyalarının içinde React ve Next.js sürümlerini arar"""
        # Sadece framework ile ilgili olabilecek dosyaları tara
        target_files = [f for f in js_files if "framework" in f or "main" in f or "webpack" in f]
        if not target_files:
            target_files = js_files[:3] # İlk 3 dosyayı tara

        for js_path in target_files:
            js_url = urljoin(self.target, js_path)
            try:
                js_resp = self.session.get(js_url, timeout=10)
                js_content = js_resp.text
                
                # React sürümü arama (Örn: react@19.0.0, "React v19.0.0")
                if not self.results["react_version"]:
                    react_matches = re.findall(r'react(?:@|[\s\-\_]*v?)(1[89]\.[\d\.]+)', js_content, re.IGNORECASE)
                    if react_matches:
                        self.results["react_version"] = react_matches[0]
                        self.add_detail(f"JS Bundle'da React sürümü tespit edildi: {react_matches[0]}")

                # Next.js sürümü arama
                if not self.results["nextjs_version"]:
                    next_matches = re.findall(r'next(?:@|[\s\-\_]*v?)(1[456]\.[\d\.]+)', js_content, re.IGNORECASE)
                    if next_matches:
                        self.results["nextjs_version"] = next_matches[0]
                        self.add_detail(f"JS Bundle'da Next.js sürümü tespit edildi: {next_matches[0]}")

                # İkisi de bulunduysa erken çık
                if self.results["react_version"] and self.results["nextjs_version"]:
                    break
                    
            except Exception as e:
                continue

        # Eğer JS bundle'larında bulamadıysa ve hedefte /api/health varsa oradan şansımızı deneyelim (Eğitim ortamımız için)
        if not self.results["react_version"] or not self.results["nextjs_version"]:
            try:
                health_resp = self.session.get(f"{self.target}/api/health", timeout=5)
                if health_resp.status_code == 200:
                    data = health_resp.json()
                    if "version" in data:
                        if "react" in data["version"] and not self.results["react_version"]:
                            self.results["react_version"] = data["version"]["react"]
                            self.add_detail(f"/api/health üzerinden React sürümü tespit edildi: {self.results['react_version']}")
                        if "next" in data["version"] and not self.results["nextjs_version"]:
                            self.results["nextjs_version"] = data["version"]["next"]
                            self.add_detail(f"/api/health üzerinden Next.js sürümü tespit edildi: {self.results['nextjs_version']}")
            except Exception:
                pass

    def check_flight_protocol(self):
        """RSC Flight protokolünün aktif olup olmadığını test eder"""
        # Next.js'e RSC requesti taklidi yapalım
        headers = {
            "RSC": "1",
            "Content-Type": "text/x-component",
            "Next-Action": "test-action", # Dummy action
            "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D"
        }
        
        try:
            # POST ile Server Action tetikleme denemesi
            resp = self.session.post(self.target, headers=headers, data="[]", timeout=10)
            
            # Yanıt x-component ise veya Next-Action header'ı döndürdüyse
            resp_headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
            content_type = resp_headers.get("content-type", "")
            
            if "text/x-component" in content_type or "next-action" in resp_headers:
                self.results["rsc_enabled"] = True
                self.add_detail("Flight Protokolü aktif! Sunucu RSC ve Server Actions destekliyor.")
            # 500 dönüyorsa ve içinde RSC/Action ile ilgili bir hata varsa
            elif resp.status_code in [400, 500] and ("action" in resp.text.lower() or "flight" in resp.text.lower()):
                 self.results["rsc_enabled"] = True
                 self.add_detail("Flight Protokolü hatası alındı. RSC aktif ancak payload reddedildi.")
                 
        except Exception as e:
            self.log(f"Flight protokol test hatası: {str(e)}", "error")

    def evaluate_vulnerability(self):
        """Toplanan verilere göre CVE-2025-55182 zafiyet durumunu değerlendirir"""
        vulnerable = False
        
        # Eğer sürümler bilinmiyorsa ama RSC aktifse "Potansiyel" olarak işaretle
        if self.results["rsc_enabled"] and (not self.results["react_version"] and not self.results["nextjs_version"]):
            self.add_detail("Sürümler kesin tespit edilemedi ancak RSC aktif. Manuel kontrol önerilir.")
            
        # React sürümü kontrolü
        is_react_vuln = False
        if self.results["react_version"]:
            if any(self.results["react_version"].startswith(v) for v in self.vuln_react):
                is_react_vuln = True
                self.add_detail(f"React {self.results['react_version']} savunmasız sürümler listesinde!")
        
        # Next.js sürümü kontrolü
        is_next_vuln = False
        if self.results["nextjs_version"]:
            if any(self.results["nextjs_version"].startswith(v) for v in self.vuln_next):
                is_next_vuln = True
                self.add_detail(f"Next.js {self.results['nextjs_version']} savunmasız sürümler listesinde!")

        # Eğer herhangi biri savunmasızsa ve RSC aktifse KESİN SAVUNMASIZ
        if (is_react_vuln or is_next_vuln) and self.results["rsc_enabled"]:
            vulnerable = True
            
        # Sadece React 19.0.0 veya Next.js 15.0.x tespit edildiyse bile uyarı ver
        elif is_react_vuln or is_next_vuln:
            self.add_detail("Savunmasız framework sürümü kullanılıyor. RSC endpoint keşfi başarısız olsa da zafiyet barındırma ihtimali yüksek.")
            vulnerable = True
            
        # Eğer Next.js olduğu kesinse ve RSC açıksa ama sürüm bulamadıysak "POTANSİYEL ZAFİYETLİ" kabul edelim
        elif self.results["is_nextjs"] and self.results["rsc_enabled"] and not self.results["react_version"]:
            self.add_detail("Sürümler bulunamadı ancak RSC aktif. Next.js 15+ olma ihtimaline karşı POTANSİYEL ZAFİYETLİ!")
            vulnerable = True

        self.results["vulnerable"] = vulnerable

    def run(self):
        """Tüm tarama adımlarını yürütür"""
        self.log(f"Hedef taranıyor: {self.target}", "info")
        self.analyze_headers()
        self.fetch_static_bundles()
        self.check_flight_protocol()
        self.evaluate_vulnerability()
        return self.results

def print_result(res):
    print("\n" + "="*50)
    print(f"🎯 Hedef: {Fore.CYAN}{res['url']}{Style.RESET_ALL}")
    
    if not res['is_nextjs']:
        print(f"[{Fore.YELLOW}?{Style.RESET_ALL}] Next.js altyapısı tespit edilemedi.")
        return
        
    print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Framework: Next.js")
    
    if res['nextjs_version']:
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Next.js Sürümü: {Fore.CYAN}{res['nextjs_version']}{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] Next.js Sürümü: Bulunamadı")
        
    if res['react_version']:
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] React Sürümü: {Fore.CYAN}{res['react_version']}{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] React Sürümü: Bulunamadı")
        
    if res['rsc_enabled']:
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] React Server Components (RSC): {Fore.GREEN}Aktif{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] React Server Components (RSC): Kapalı veya Bulunamadı")

    print("\nSonuç:")
    if res['vulnerable']:
        print(f"{Fore.WHITE}{Style.BRIGHT}[!] ZAFİYETLİ (CVE-2025-55182) {Style.RESET_ALL}")
        print(f"{Fore.RED}Hedef sunucunun savunmasız bileşenler kullandığı tespit edildi.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[✓] GÜVENLİ GÖRÜNÜYOR{Style.RESET_ALL}")
        print("Hedefte savunmasız sürüm veya aktif bir RSC saldırı yüzeyi bulunamadı.")
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="React2Shell (CVE-2025-55182) Pentest Scanner")
    parser.add_argument("-u", "--url", help="Tek bir hedef URL (örn: https://example.com)")
    parser.add_argument("-l", "--list", help="Hedef URL'lerin bulunduğu dosya listesi")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detaylı log çıktıları")
    parser.add_argument("-o", "--output", help="Sonuçları JSON olarak kaydet")
    
    args = parser.parse_args()

    print(rf"""{Fore.RED}
    ____                  __  ___ _____ __         ____ 
   / __ \___  ____  _____/ /_|__ \/ ___// /_  ___  / / / 
  / /_/ / _ \/ __ `/ ___/ __/__/ / __ \/ __ \/ _ \/ / /  
 / _, _/  __/ /_/ / /__/ /_ / __/ /_/ / / / /  __/ / /   
/_/ |_|\___/\__,_/\___/\__//____|____/_/ /_/\___/_/_/    Scanner
                                                        
{Fore.YELLOW}CVE-2025-55182 Detection Tool for Pentesters
{Style.RESET_ALL}""")

    targets = []
    if args.url:
        targets.append(args.url)
    if args.list:
        try:
            with open(args.list, 'r') as f:
                targets.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"{Fore.RED}[-] Dosya okuma hatası: {e}")
            sys.exit(1)

    if not targets:
        parser.print_help()
        sys.exit(1)

    all_results = []
    
    print(f"[*] Toplam {len(targets)} hedef taranacak.")
    
    # Çoklu hedefleri thread ile tara
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for target in targets:
            if not target.startswith("http"):
                target = "https://" + target
            scanner = Scanner(target, args.verbose)
            futures.append(executor.submit(scanner.run))
            
        for future in futures:
            res = future.result()
            all_results.append(res)
            print_result(res)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"{Fore.GREEN}[+] Sonuçlar {args.output} dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
