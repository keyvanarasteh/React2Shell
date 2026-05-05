# ⚡ React2Shell — CVE-2025-55182

## Eğitim Amaçlı Saldırı Laboratuvarı

> **Pre-Auth RCE via React Server Components Flight Protocol**
> CVSS 10.0 — Critical

```
┌─────────────────────────────────────────────────────────────────┐
│  Crafted HTTP POST → Flight Deserialization → Object Injection │
│  → Dynamic Dispatch → Blob Handler → child_process.exec()     │
│  → FULL SERVER COMPROMISE                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ YASAL UYARI / DISCLAIMER

> **🔴 Bu proje yalnızca EĞİTİM ve ARAŞTIRMA amaçlıdır.**
>
> - Buradaki araçlar **yalnızca kendi kontrol ettiğiniz sistemlerde** kullanılmalıdır
> - Yetkisiz sistemlere saldırı **Türk Ceza Kanunu madde 243-245** kapsamında suçtur
> - Proje sahipleri araçların kötüye kullanımından **sorumluluk kabul etmez**
> - Tüm testler **localhost** üzerinde, izole ortamda yapılmalıdır

---

## 📋 CVE Bilgileri

| Alan | Detay |
|------|-------|
| **CVE** | CVE-2025-55182 |
| **CVSS** | 10.0 / Critical |
| **Tür** | Insecure Deserialization → RCE |
| **Kimlik Doğrulama** | Gerekmez (Pre-Auth) |
| **Etkilenen** | React 19.0.0, 19.1.0, 19.1.1, 19.2.0 |
| **Yamalı** | React 19.0.1, 19.1.2, 19.2.1+ |
| **Framework'ler** | Next.js, Waku, RedwoodSDK, React Router |
| **Keşfeden** | Northwave Cybersecurity |
| **Açıklama Tarihi** | 3 Aralık 2025 |

### İlişkili CVE'ler

| CVE | CVSS | Tür |
|-----|------|-----|
| CVE-2025-55183 | 5.3 | Kaynak Kod İfşası (Information Disclosure) |
| CVE-2025-55184 | 7.5 | Hizmet Reddi (Denial of Service) |

---

## 📁 Proje Yapısı

```
React2Shell/
│
├── 📄 Saldiri.md              # Orijinal CVE araştırma dokümanı
├── 📄 readme.md               # Bu dosya
├── 📄 roadmap.md              # 8 fazlı uygulama yol haritası
│
├── 📂 website/                # 🎯 Savunmasız Hedef Website
│   ├── package.json           #    next@15.0.3 + react@19.0.0
│   ├── next.config.js
│   └── src/app/
│       ├── layout.tsx         #    Root layout
│       ├── page.tsx           #    İletişim formu (Server Action)
│       ├── actions.ts         #    "use server" — SALDIRI YÜZEYİ
│       ├── globals.css
│       └── api/health/
│           └── route.ts       #    Health check endpoint
│
├── 📂 saldiri/                # 🗡️ Saldırı Araçları (Python)
│   ├── requirements.txt       #    Bağımlılıklar
│   ├── utils.py               #    Yardımcı fonksiyonlar
│   ├── 01_recon.py            #    Keşif & parmak izi
│   ├── 02_source_leak.py      #    Kaynak kod ifşası
│   ├── 03_dos.py              #    DoS saldırısı
│   ├── 04_rce.py              #    Uzaktan kod yürütme
│   ├── 05_full_chain.py       #    Tam saldırı zinciri
│   └── payloads/              #    Payload şablonları
│       ├── flight_rce.json
│       ├── flight_dos.json
│       └── flight_source.json
│
└── 📂 savunma/                # 🛡️ Savunma & Yama (Faz 7)
    └── patch_guide.md
```

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

| Araç | Sürüm | Amaç |
|------|-------|------|
| Node.js | 18+ | Website çalıştırma |
| npm | 9+ | Paket yönetimi |
| Python | 3.10+ | Saldırı scriptleri |
| pip | 22+ | Python paket yönetimi |

### 1. Savunmasız Website'i Kur ve Çalıştır

```bash
# Website bağımlılıklarını yükle
cd website
npm install

# Geliştirme sunucusunu başlat
npm run dev
# → http://localhost:3000
```

### 2. Saldırı Araçlarını Hazırla

```bash
# Python bağımlılıklarını yükle
cd saldiri
pip install -r requirements.txt
```

### 3. Saldırı Zincirini Çalıştır

```bash
# Adım adım çalıştır
python3 01_recon.py --target http://localhost:3000
python3 02_source_leak.py --target http://localhost:3000
python3 03_dos.py --target http://localhost:3000
python3 04_rce.py --target http://localhost:3000

# Veya tam otomatik
python3 05_full_chain.py --target http://localhost:3000
```

---

## 🗡️ Saldırı Zinciri

### Aşama 1: Keşif (Reconnaissance)
```
01_recon.py
├── HTTP Header analizi (X-Powered-By, Server)
├── Framework parmak izi (/_next/static/)
├── React/Next.js sürüm tespiti
└── RSC endpoint keşfi (next-action headers)
```

### Aşama 2: Kaynak Kod İfşası (CVE-2025-55183)
```
02_source_leak.py
├── Flight protokolü ile kaynak kod isteme
├── Server Function derlenmiş kod çekme
└── Hassas bilgi arama (API keys, DB creds, env vars)
```

### Aşama 3: Hizmet Reddi (CVE-2025-55184)
```
03_dos.py
├── Memory exhaustion payload
├── Self-referencing loop payload
├── Yanıt süresi ölçümü (baseline vs DoS)
└── Kurtarma süresi testi
```

### Aşama 4: Uzaktan Kod Yürütme (CVE-2025-55182)
```
04_rce.py
├── Malicious Flight Protocol payload
├── JavaScript dynamic dispatch exploit
├── Blob Handler manipülasyonu
├── PoC komut yürütme (id, whoami, hostname)
└── Reverse shell (localhost only)
```

---

## 🛡️ Savunma Rehberi

### Acil Eylemler
```bash
# React güncelle
npm install react@19.0.1 react-dom@19.0.1

# Next.js güncelle
npm install next@15.0.5

# Audit çalıştır
npm audit fix
```

### Uzun Vadeli Sertleştirme
- ✅ CSP header'ları uygula
- ✅ Node.js'i minimum ayrıcalıklarla çalıştır (asla root değil)
- ✅ Docker'da `--cap-drop=ALL` ve read-only filesystem kullan
- ✅ WAF kuralları ile anomalous POST isteklerini engelle
- ✅ Otomatik bağımlılık taraması (Snyk, npm audit, Dependabot)
- ✅ RASP (Runtime Application Self-Protection) uygula

### Tespit İndikatörleri
```bash
# Şüpheli RSC isteklerini izle
tail -f /var/log/nginx/access.log | grep -E "POST.*(x-component|next-action)"

# Beklenmedik child process'leri kontrol et
ps aux | grep -E "(node|next)" | grep -v grep
lsof -p $(pgrep -f next-server) | grep -E "(ESTABLISHED|sh|bash)"
```

---

## 📚 Referanslar

| Kaynak | Link |
|--------|------|
| React Official Security Advisory | react.dev |
| NVD — CVE-2025-55182 | nvd.nist.gov |
| Northwave Research — React2Shell | northwave-cybersecurity.com |
| CISA KEV Catalog Entry | cisa.gov |
| Cloudflare Threat Analysis | blog.cloudflare.com |
| Palo Alto Unit 42 Report | unit42.paloaltonetworks.com |
| Next.js Security Bulletin | nextjs.org |

---

## 🗺️ Yol Haritası

Detaylı uygulama planı için: [`roadmap.md`](roadmap.md)

```
Hafta 1: Website Kurulumu + Keşif Scriptleri
Hafta 2: Source Leak + DoS Scriptleri
Hafta 3: RCE Exploit + Full Chain Otomasyonu
Hafta 4: Savunma & Yama + Dokümantasyon
```

---

## 📄 Lisans

Bu proje eğitim amaçlıdır. Kötü amaçlı kullanım kesinlikle yasaktır.

---

*React2Shell Lab — CVE-2025-55182 Eğitim Ortamı — 2026*
