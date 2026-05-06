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
try:
    from flask import Flask, request, jsonify, render_template
except ImportError:
    pass # Flask not installed, CLI only mode
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
            "dependencies": {},
            "exposed_files": [],
            "secrets": [],
            "details": []
        }
        
        # Bilinen savunmasız sürümler (React2Shell - CVE-2025-55182)
        self.vuln_react = ["19.0.0", "19.1.0", "19.1.1", "19.2.0", "18.3.0-canary"]
        self.vuln_next = [
            "14.3.0-canary",
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
                    self.results["nextjs_version"] = {
                        "version": m.group(1),
                        "source": "HTTP Headers",
                        "context": f"x-powered-by: {x_powered_by}"
                    }
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
            
            # HTML içerisinden meta tag ile Next.js tespiti
            generator_match = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Next\.js\s+(1[456]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)["\']', html, re.IGNORECASE)
            if generator_match and not self.results["nextjs_version"]:
                context = html[max(0, generator_match.start() - 30) : min(len(html), generator_match.end() + 30)]
                self.results["nextjs_version"] = {
                    "version": generator_match.group(1),
                    "source": urljoin(self.target, "/"),
                    "context": context
                }
                self.results["is_nextjs"] = True
                self.add_detail(f"HTML meta tag üzerinden Next.js sürümü tespit edildi: {generator_match.group(1)}")

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
            js_files = re.findall(r'(/_next/static/[a-zA-Z0-9_/\-\.]+\.js)', html)
            js_files = list(set(js_files)) # Deduplicate
            
            if js_files:
                self.add_detail(f"{len(js_files)} adet statik JS dosyası bulundu. Sürüm analizi yapılıyor...")
                self.extract_versions_from_js(js_files)
                
        except Exception as e:
            self.log(f"Statik bundle analizi hatası: {str(e)}", "error")

    def extract_versions_from_js(self, js_files):
        """İndirilen JS dosyalarının içinde React, Next.js ve diğer paketlerin sürümlerini arar"""
        scanned_files = set()
        to_scan = list(set(js_files))
        to_scan.sort(key=lambda x: 0 if any(k in x for k in ["framework", "main", "webpack", "app", "pages", "layout"]) else 1)
        max_scan_limit = 100 # Sonsuz döngüyü önlemek için sınır

        while to_scan and len(scanned_files) < max_scan_limit:
            js_path = to_scan.pop(0)
            if js_path in scanned_files:
                continue
            scanned_files.add(js_path)

            js_url = urljoin(self.target, js_path)
            try:
                js_resp = self.session.get(js_url, timeout=7)
                if js_resp.status_code != 200:
                    continue
                js_content = js_resp.text
                
                # Yeni js dosyalarını keşfet (iç içe chunk loading)
                new_js = re.findall(r'["\'](/[a-zA-Z0-9_/\-\.]+\.js)["\']', js_content)
                chunk_matches = re.findall(r'static/chunks/[a-zA-Z0-9_/\-\.]+\.js', js_content)
                for chunk in chunk_matches:
                    new_js.append("/_next/" + chunk)
                
                for nj in new_js:
                    if nj not in scanned_files and nj not in to_scan:
                        to_scan.append(nj)
                
                # Yeni eklenenleri tekrar sıralayalım
                to_scan.sort(key=lambda x: 0 if any(k in x for k in ["framework", "main", "webpack", "app", "pages", "layout"]) else 1)
                
                # Genel paket versiyonu tespiti
                # Örn: /*! framer-motion v10.16.4 */ veya /*! @radix-ui/react-dropdown-menu 2.0.6 */
                pkg_matches = re.finditer(r'/\*!\s*(?:[A-Za-z0-9_\-\.\@\/]+\s+)?([a-zA-Z0-9_\-\.\@\/]+)\s+[vV]?([0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9_\-\.]*)\s*\*/', js_content)
                for match in pkg_matches:
                    pkg_name = match.group(1)
                    pkg_version = match.group(2)
                    if pkg_name not in self.results["dependencies"]:
                        context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                        self.results["dependencies"][pkg_name] = {
                            "version": pkg_version,
                            "source": js_url,
                            "context": context
                        }
                        self.add_detail(f"Bağımlılık tespit edildi: {pkg_name} (v{pkg_version})")

                # json içerisine gömülü package.json kalıntıları (örn. name:"lucide-react",version:"0.263.1")
                embedded_pkg_matches = re.finditer(r'(?:name|pkg|package)\s*:\s*["\']([a-zA-Z0-9_\-\.\@\/]+)["\']\s*,\s*(?:version|ver)\s*:\s*["\']([0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9_\-\.]*)["\']', js_content)
                for match in embedded_pkg_matches:
                    pkg_name = match.group(1)
                    pkg_version = match.group(2)
                    if pkg_name not in self.results["dependencies"] and len(pkg_name) > 1 and len(pkg_version) > 1:
                        context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                        self.results["dependencies"][pkg_name] = {
                            "version": pkg_version,
                            "source": js_url,
                            "context": context
                        }
                        self.add_detail(f"Gömülü bağımlılık tespit edildi: {pkg_name} (v{pkg_version})")
                
                # React sürümü arama
                if not self.results["react_version"]:
                    react_patterns = [
                        r'react(?:@|[\s\-\_]*v?)(1[89]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)',
                        r'reconcilerVersion\s*[:=]\s*["\'](1[89]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)["\']',
                        r'(?:version|ReactVersion)\s*[:=]\s*["\'](1[89]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)["\']',
                        r'"react"\s*:\s*"[^"]*(1[89]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)[^"]*"',
                        r'react-dom(?:@|[\s\-\_]*v?)(1[89]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)'
                    ]
                    for pattern in react_patterns:
                        matches = list(re.finditer(pattern, js_content, re.IGNORECASE))
                        if matches:
                            match = matches[0]
                            version = match.group(1)
                            if "version" in pattern.lower() or "reactversion" in pattern.lower():
                                if "react" in js_content.lower() or "useLayoutEffect" in js_content or "useState" in js_content:
                                    context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                                    self.results["react_version"] = {
                                        "version": version,
                                        "source": js_url,
                                        "context": context
                                    }
                                    self.add_detail(f"JS Bundle'da React sürümü tespit edildi: {version}")
                                    break
                            else:
                                context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                                self.results["react_version"] = {
                                    "version": version,
                                    "source": js_url,
                                    "context": context
                                }
                                self.add_detail(f"JS Bundle'da React sürümü tespit edildi: {version}")
                                break

                # Next.js sürümü arama
                if not self.results["nextjs_version"]:
                    next_patterns = [
                        r'next(?:@|[\s\-\_]*v?)(1[456]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)',
                        r'window\.next\s*=\s*\{.*?version:\s*["\'](1[456]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)["\']',
                        r'(?:__NEXT_VERSION|nextVersion|version)\s*[:=]\s*["\'](1[456]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)["\']',
                        r'"next"\s*:\s*"[^"]*(1[456]\.[\d\.]+(?:-[a-zA-Z0-9.\-]+)?)[^"]*"'
                    ]
                    for pattern in next_patterns:
                        matches = list(re.finditer(pattern, js_content, re.IGNORECASE))
                        if matches:
                            match = matches[0]
                            version = match.group(1)
                            if "version" in pattern.lower() and "next" not in pattern.lower():
                                if "next" in js_content.lower() or "app-router" in js_content.lower() or "window.next" in js_content:
                                    context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                                    self.results["nextjs_version"] = {
                                        "version": version,
                                        "source": js_url,
                                        "context": context
                                    }
                                    self.add_detail(f"JS Bundle'da Next.js sürümü tespit edildi: {version}")
                                    break
                            else:
                                context = js_content[max(0, match.start() - 30) : min(len(js_content), match.end() + 30)]
                                self.results["nextjs_version"] = {
                                    "version": version,
                                    "source": js_url,
                                    "context": context
                                }
                                self.add_detail(f"JS Bundle'da Next.js sürümü tespit edildi: {version}")
                                break

                # Diğer paketleri taramaya devam etmek için erken çıkışı (break) kaldırıyoruz
                # if self.results["react_version"] and self.results["nextjs_version"]:
                #     break
                    
                # Secrets/API Keys arama
                self.detect_secrets(js_content, js_url)

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
                            self.results["react_version"] = {
                                "version": data["version"]["react"],
                                "source": f"{self.target}/api/health",
                                "context": json.dumps(data)
                            }
                            self.add_detail(f"/api/health üzerinden React sürümü tespit edildi: {self.results['react_version']['version']}")
                        if "next" in data["version"] and not self.results["nextjs_version"]:
                            self.results["nextjs_version"] = {
                                "version": data["version"]["next"],
                                "source": f"{self.target}/api/health",
                                "context": json.dumps(data)
                            }
                            self.add_detail(f"/api/health üzerinden Next.js sürümü tespit edildi: {self.results['nextjs_version']['version']}")
            except Exception:
                pass

    def detect_secrets(self, content, source_url):
        """JS içeriğinde hassas bilgileri (API Key, Token vb.) arar"""
        patterns = {
            "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
            "Firebase URL": r"https://[a-z0-9\-]+\.firebaseio\.com",
            "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "AWS Secret Key": r"secret_?key\s*[:=]\s*['\"][0-9a-zA-Z\/+]{40}['\"]",
            "JWT Token": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
            "GitHub Token": r"gh[oprs]_[a-zA-Z0-9]{36,}",
            "Discord Webhook": r"https://discord\.com/api/webhooks/[0-9]+/[a-zA-Z0-9\-]+",
            "Generic API Key": r"(?:api_?key|auth_?token|access_?token)\s*[:=]\s*['\"][0-9a-zA-Z\-_]{16,}['\"]"
        }
        
        for name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                secret_val = match.group(0)
                # Aynı secret'ı tekrar ekleme
                if not any(s["value"] == secret_val for s in self.results["secrets"]):
                    context = content[max(0, match.start() - 30) : min(len(content), match.end() + 30)]
                    self.results["secrets"].append({
                        "type": name,
                        "value": secret_val,
                        "source": source_url,
                        "context": context
                    })
                    self.add_detail(f"Hassas bilgi tespit edildi: {name} ({source_url})")

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
            ver = self.results["react_version"]["version"] if isinstance(self.results["react_version"], dict) else self.results["react_version"]
            if any(ver.startswith(v) for v in self.vuln_react):
                is_react_vuln = True
                self.add_detail(f"React {ver} savunmasız sürümler listesinde!")
        
        # Next.js sürümü kontrolü
        is_next_vuln = False
        if self.results["nextjs_version"]:
            ver = self.results["nextjs_version"]["version"] if isinstance(self.results["nextjs_version"], dict) else self.results["nextjs_version"]
            if any(ver.startswith(v) for v in self.vuln_next):
                is_next_vuln = True
                self.add_detail(f"Next.js {ver} savunmasız sürümler listesinde!")

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

    def fuzz_sensitive_files(self):
        """Hassas dosyalar için fuzzing yapar (.env, .git/config vs.)"""
        self.results["exposed_files"] = []
        sensitive_paths = [
            ".env", ".env.local", ".env.development", ".env.production", ".env.test",
            ".git/config", ".git/HEAD", "package.json", "package-lock.json",
            "docker-compose.yml", "Dockerfile", ".npmrc", "yarn.lock",
            "next.config.js", "tsconfig.json", ".vscode/settings.json",
            "web.config", "phpinfo.php", "config.php", "wp-config.php",
            ".htaccess", ".htpasswd", "server-status", "robots.txt"
        ]
        self.add_detail("Hassas dosyalar için fuzzing başlatılıyor...")
        
        def check_path(path):
            url = urljoin(self.target, f"/{path}")
            try:
                resp = self.session.get(url, timeout=5)
                if resp.status_code == 200:
                    # Basit bir false positive kontrolü (HTML sayfası dönmüş olabilir)
                    content_type = resp.headers.get("content-type", "")
                    if "text/html" not in content_type and "<html" not in resp.text[:100].lower():
                        # Dosya ifşa olmuş olabilir
                        context = resp.text[:200] + "..." if len(resp.text) > 200 else resp.text
                        self.results["exposed_files"].append({
                            "path": path,
                            "url": url,
                            "context": context
                        })
                        self.add_detail(f"Hassas dosya ifşası: {path} ({url})")
            except Exception:
                pass

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(check_path, sensitive_paths)

    def run(self):
        """Tüm tarama adımlarını yürütür"""
        self.log(f"Hedef taranıyor: {self.target}", "info")
        self.analyze_headers()
        self.fetch_static_bundles()
        self.check_flight_protocol()
        self.fuzz_sensitive_files()
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
        ver = res['nextjs_version']['version'] if isinstance(res['nextjs_version'], dict) else res['nextjs_version']
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] Next.js Sürümü: {Fore.CYAN}{ver}{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] Next.js Sürümü: Bulunamadı")
        
    if res['react_version']:
        ver = res['react_version']['version'] if isinstance(res['react_version'], dict) else res['react_version']
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] React Sürümü: {Fore.CYAN}{ver}{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] React Sürümü: Bulunamadı")
        
    if res['rsc_enabled']:
        print(f"[{Fore.GREEN}+{Style.RESET_ALL}] React Server Components (RSC): {Fore.GREEN}Aktif{Style.RESET_ALL}")
    else:
        print(f"[{Fore.YELLOW}-{Style.RESET_ALL}] React Server Components (RSC): Kapalı veya Bulunamadı")
        
    if res.get('dependencies'):
        print(f"\n[{Fore.CYAN}*{Style.RESET_ALL}] Tespit Edilen Diğer Bağımlılıklar:")
        for pkg, data in res['dependencies'].items():
            ver = data['version'] if isinstance(data, dict) else data
            print(f"  - {Fore.CYAN}{pkg}{Style.RESET_ALL}: {ver}")

    if res.get('exposed_files'):
        print(f"\n[{Fore.RED}!{Style.RESET_ALL}] İfşa Olan Hassas Dosyalar:")
        for f in res['exposed_files']:
            print(f"  - {Fore.RED}{f['path']}{Style.RESET_ALL} -> {f['url']}")

    if res.get('secrets'):
        print(f"\n[{Fore.RED}!{Style.RESET_ALL}] Tespit Edilen Hassas Bilgiler (Secrets):")
        for s in res['secrets']:
            print(f"  - {Fore.RED}{s['type']}{Style.RESET_ALL}: {s['value']} ({s['source']})")

    print("\nSonuç:")
    if res['vulnerable']:
        print(f"{Fore.WHITE}{Style.BRIGHT}[!] ZAFİYETLİ (CVE-2025-55182) {Style.RESET_ALL}")
        print(f"{Fore.RED}Hedef sunucunun savunmasız bileşenler kullandığı tespit edildi.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}[✓] GÜVENLİ GÖRÜNÜYOR{Style.RESET_ALL}")
        print("Hedefte savunmasız sürüm veya aktif bir RSC saldırı yüzeyi bulunamadı.")
    print("="*50)

def start_web_server(port=5000):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/scan", methods=["POST"])
    def api_scan():
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL belirtilmedi"}), 400
        
        target = data["url"]
        if not target.startswith("http"):
            target = "https://" + target
            
        scanner = Scanner(target, verbose=False)
        res = scanner.run()
        return jsonify(res)

    print(f"{Fore.GREEN}[*] Starting React2Shell Web Panel on http://127.0.0.1:{port}{Style.RESET_ALL}")
    app.run(host="127.0.0.1", port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description="React2Shell (CVE-2025-55182) Pentest Scanner")
    parser.add_argument("-u", "--url", help="Tek bir hedef URL (örn: https://example.com)")
    parser.add_argument("-l", "--list", help="Hedef URL'lerin bulunduğu dosya listesi")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detaylı log çıktıları")
    parser.add_argument("-o", "--output", help="Sonuçları JSON olarak kaydet")
    parser.add_argument("--web", type=int, nargs="?", const=5000, help="Web panel'i başlatır. Opsiyonel olarak port belirtebilirsiniz (varsayılan: 5000).")
    
    args = parser.parse_args()

    if args.web:
        start_web_server(args.web)
        return

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
