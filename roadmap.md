# 🗺️ React2Shell — Yol Haritası (Roadmap)

## CVE-2025-55182 | Eğitim Amaçlı Saldırı Laboratuvarı

> **Amaç:** React Server Components Flight Protokolü üzerindeki kritik insecure deserialization açığını kontrollü bir ortamda öğrenmek ve uygulamak.

---

## 📋 Genel Bakış

| Faz | Başlık | Klasör | Süre |
|-----|--------|--------|------|
| 1 | Savunmasız Website Kurulumu | `website/` | ~30 dk |
| 2 | Keşif & Parmak İzi | `saldiri/01_recon.py` | ~20 dk |
| 3 | Kaynak Kod İfşası | `saldiri/02_source_leak.py` | ~20 dk |
| 4 | Hizmet Reddi Testi (DoS) | `saldiri/03_dos.py` | ~15 dk |
| 5 | Uzaktan Kod Yürütme (RCE) | `saldiri/04_rce.py` | ~30 dk |
| 6 | Tam Saldırı Zinciri | `saldiri/05_full_chain.py` | ~20 dk |
| 7 | Savunma & Yama Uygulama | `website/` | ~20 dk |
| 8 | Dokümantasyon & Raporlama | `./` | ~15 dk |

**Toplam Tahmini Süre:** ~2.5–3 saat

---

## 🔴 Faz 1 — Savunmasız Website Kurulumu

### Hedef
Bilinen savunmasız Next.js + React sürümleri ile RSC kullanan bir hedef web uygulaması oluşturmak.

### Teknik Detaylar
- **Framework:** Next.js `15.0.3` (yamalanmamış)
- **React:** `19.0.0` (savunmasız)
- **Paket:** `react-server-dom-webpack` (savunmasız)

### Adımlar
1. `website/` dizininde Next.js projesi oluştur
2. `package.json` — savunmasız bağımlılıkları tanımla
3. `next.config.js` — Server Actions etkinleştir
4. `src/app/page.tsx` — Server Action kullanan iletişim formu
5. `src/app/actions.ts` — `"use server"` ile işaretlenmiş fonksiyonlar
6. `src/app/api/health/route.ts` — Sağlık kontrolü endpoint'i
7. `npm install && npm run dev` ile çalıştır
8. `http://localhost:3000` adresinde doğrula

### Saldırı Yüzeyi
```
"use server" direktifli fonksiyonlar:
├── submitForm()        → Form verisi işleme
├── getServerInfo()     → Sunucu bilgisi döndürme
└── processData()       → Veri işleme fonksiyonu
```

### Başarı Kriteri
- [ ] Website `localhost:3000`'de çalışıyor
- [ ] Server Actions form üzerinden tetiklenebiliyor
- [ ] RSC Flight protokolü aktif

---

## 🟡 Faz 2 — Keşif & Parmak İzi (Reconnaissance)

### Script: `saldiri/01_recon.py`

### Yapılacaklar
1. **HTTP Header Analizi** — `X-Powered-By`, `Server`, `X-NextJS-*`
2. **Framework Parmak İzi** — `/_next/static/`, `buildManifest.js`
3. **RSC Endpoint Keşfi** — `text/x-component` POST denemeleri, `next-action` header taraması
4. **Sürüm Tespiti** — React/Next.js sürüm eşleştirmesi

### Beklenen Çıktı
```
[*] Hedef: http://localhost:3000
[+] Framework: Next.js 15.0.3
[+] React: 19.0.0
[!] SAVUNMASIZ — CVE-2025-55182 etkileniyor
```

---

## 🟠 Faz 3 — Kaynak Kod İfşası (CVE-2025-55183)

### Script: `saldiri/02_source_leak.py`
- **CVE:** CVE-2025-55183 (CVSS 5.3) — Information Disclosure

### Yapılacaklar
1. Flight protokolü üzerinden kaynak kod isteme payload'ı oluştur
2. Server Function'ların derlenmiş kodunu çek
3. Hassas bilgi arama (API anahtarları, DB bağlantıları, env variables)
4. Sonuçları raporla ve dosyaya kaydet

---

## 🟠 Faz 4 — Hizmet Reddi Testi (CVE-2025-55184)

### Script: `saldiri/03_dos.py`
- **CVE:** CVE-2025-55184 (CVSS 7.5) — Denial of Service

### Yapılacaklar
1. **Memory Exhaustion** — büyük iç içe nesne yapıları, sonsuz döngü referansları
2. **CPU Exhaustion** — karmaşık regex, recursive deserialization
3. **Yanıt Süresi Ölçümü** — baseline vs DoS sonrası karşılaştırma
4. **Kurtarma Testi** — sunucunun DoS sonrası toparlanma süresi

---

## 🔴 Faz 5 — Uzaktan Kod Yürütme (CVE-2025-55182)

### Script: `saldiri/04_rce.py`
- **CVE:** CVE-2025-55182 (CVSS 10.0) — Pre-Auth RCE

### Saldırı Zinciri
```
Crafted HTTP POST
  → RSC Flight Protocol Deserialization
    → Malicious Object Injection
      → JavaScript Dynamic Dispatch
        → Blob Handler Exploit
          → child_process.exec()
            → Full Server Compromise
```

### Yapılacaklar
1. **Payload Oluşturma** — Self-referencing nesne, Blob Handler manipülasyonu
2. **PoC Komutları** — `id`, `whoami`, `hostname`, `cat /etc/passwd`
3. **Reverse Shell** — Node.js `child_process.exec()` (yalnızca localhost)
4. **Dosya Yazma Kanıtı** — `/tmp/react2shell_pwned.txt`

---

## 🟣 Faz 6 — Tam Saldırı Zinciri Otomasyonu

### Script: `saldiri/05_full_chain.py`

### Kullanım
```bash
python3 05_full_chain.py --target http://localhost:3000
python3 05_full_chain.py --target http://localhost:3000 --include-dos
python3 05_full_chain.py --target http://localhost:3000 --phases recon,source
```

Tüm fazları sıralı çalıştırır, kapsamlı rapor oluşturur.

---

## 🟢 Faz 7 — Savunma & Yama Uygulama

### Yapılacaklar
1. **Güncelleme** — `react@19.0.1+`, `next@15.0.5+`
2. **WAF Kuralları** — anomalous POST filtreleme
3. **Sertleştirme** — CSP header, kısıtlı Node.js ayrıcalıkları
4. **Doğrulama** — tüm saldırı scriptlerini yamalı sürüme çalıştır, başarısız olduğunu doğrula

---

## 🔵 Faz 8 — Dokümantasyon & Raporlama

1. README.md — proje açıklaması, kurulum, kullanım
2. Saldırı raporu — bulgular, zaman çizelgesi
3. Savunma rehberi — yama adımları, sertleştirme kontrol listesi

---

## 📁 Proje Yapısı

```
React2Shell/
├── Saldiri.md              # CVE araştırma dokümanı
├── readme.md               # Proje README
├── roadmap.md              # Yol haritası (bu dosya)
├── website/                # Savunmasız hedef website
│   ├── package.json
│   ├── next.config.js
│   └── src/app/
│       ├── layout.tsx
│       ├── page.tsx
│       ├── actions.ts      # "use server" — saldırı yüzeyi
│       ├── globals.css
│       └── api/health/route.ts
└── saldiri/                # Saldırı araçları
    ├── requirements.txt
    ├── utils.py
    ├── 01_recon.py
    ├── 02_source_leak.py
    ├── 03_dos.py
    ├── 04_rce.py
    ├── 05_full_chain.py
    └── payloads/
        ├── flight_rce.json
        ├── flight_dos.json
        └── flight_source.json
```

---

## ⚠️ Yasal Uyarı

> **Bu proje yalnızca eğitim ve araştırma amaçlıdır.**
> Araçlar yalnızca kendi kontrol ettiğiniz sistemlerde kullanılmalıdır.
> Yetkisiz sistemlere saldırı, TCK madde 243-245 kapsamında cezai yaptırıma tabidir.

---

## 📅 Zaman Çizelgesi

```
Hafta 1: Faz 1–2 (Website + Keşif)
Hafta 2: Faz 3–4 (Source Leak + DoS)
Hafta 3: Faz 5–6 (RCE + Full Chain)
Hafta 4: Faz 7–8 (Savunma + Dokümantasyon)
```

*Son güncelleme: 2026-05-05*
