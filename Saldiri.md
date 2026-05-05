QLine.
Ana Sayfa
Hakkında
Products
Enstitü
Paketler
Manifesto
Mühendisler
İletişim

EN
U
Back to Case Studies
React2Shell — CVE-2025-55182
CRITICAL
December 2025 – April 2026
Impact: 99/100
React2Shell — CVE-2025-55182
Pre-Auth RCE via React Server Components Flight Protocol

React Server Components Flight Protokolü Üzerinden Kimlik Doğrulamasız RCE

FULL ATTACK CHAIN
Crafted HTTP POST → RSC Flight Protocol Deserialization → Malicious Object Injection → JavaScript Dynamic Dispatch → Blob Handler Exploit → Arbitrary Code Execution → Full Server Compromise (CVSS 10.0)

Key Facts
🤯 What?? / Neee?
Attack Type
Insecure Deser.
Saldırı Türü
CVE
CVE-2025-55182
CVE
CVSS Score
10.0 / Critical
CVSS Puanı
Auth Required
None (Pre-Auth)
Kimlik Doğrulama
Detailed Attack Timeline
🤯 What?? / Neee?
Detaylı Saldırı Zaman Çizelgesi

Oct 2025
October 2025 (Responsible Disclosure)
critical
Vulnerability Discovered in React Flight Protocol
React Flight Protokolünde Güvenlik Açığı Keşfedildi

Security researchers at Northwave Cybersecurity discover a critical insecure deserialization flaw in the React Server Components (RSC) "Flight" protocol. The vulnerability allows unauthenticated Remote Code Execution (RCE) on any server implementing RSC. Responsible disclosure begins with the React team.

Northwave Cybersecurity güvenlik araştırmacıları, React Server Components (RSC) "Flight" protokolünde kritik bir güvensiz serileştirme (deserialization) açığı keşfeder. Güvenlik açığı, RSC uygulayan herhangi bir sunucuda kimlik doğrulaması gerektirmeden Uzaktan Kod Yürütmeye (RCE) izin verir.

Dec 3, 2025
December 3, 2025
critical
CVE-2025-55182 Publicly Disclosed — "React2Shell"
CVE-2025-55182 Kamuya Açıklandı — "React2Shell"

The React team officially discloses CVE-2025-55182 (CVSS 10.0) alongside patched versions React 19.0.1, 19.1.2, and 19.2.1. Companion CVEs are also published: CVE-2025-55183 (source code exposure, CVSS 5.3) and CVE-2025-55184 (DoS, CVSS 7.5). Within hours, automated mass-scanning begins across the internet.

React ekibi CVE-2025-55182'yi (CVSS 10.0) yamalı sürümler React 19.0.1, 19.1.2 ve 19.2.1 ile birlikte resmi olarak açıklar. Eşlik eden CVE'ler de yayınlanır: CVE-2025-55183 (kaynak kod ifşası) ve CVE-2025-55184 (DoS). Saatler içinde internet genelinde otomatik toplu tarama başlar.

Dec 5, 2025
December 5, 2025
critical
CISA Adds to Known Exploited Vulnerabilities (KEV)
CISA Bilinen İstismar Edilen Güvenlik Açıkları (KEV) Kataloğuna Ekledi

CISA adds CVE-2025-55182 to the KEV catalog confirming active in-the-wild exploitation. Nation-state threat groups integrate the exploit into their reconnaissance and attack routines. Federal agencies are mandated to patch within 72 hours.

CISA, CVE-2025-55182'yi KEV kataloğuna ekleyerek aktif istismarı doğrular. Ulus-devlet tehdit grupları, exploit'i keşif ve saldırı rutinlerine entegre eder. Federal kurumlara 72 saat içinde yamalama zorunluluğu getirilir.

Dec 5–10, 2025
December 5–10, 2025
critical
Mass Exploitation Campaigns Emerge
Toplu İstismar Kampanyaları Ortaya Çıkıyor

Multiple malware campaigns ("emerald" and "nuts") are observed deploying Cobalt Strike beacons, Sliver C2 payloads, reverse shells, and cryptominers on compromised servers. Both Windows and Linux targets are affected. Cloudflare, AWS, and Azure deploy WAF rules to block exploitation attempts.

Birden fazla zararlı yazılım kampanyası ("emerald" ve "nuts") ele geçirilen sunucularda Cobalt Strike beacon'ları, Sliver C2 payload'ları, ters kabuk (reverse shell) ve kripto madencileri dağıtır. Hem Windows hem Linux hedefler etkilenir.

Dec 15, 2025
December 15, 2025
high
Next.js & Framework Patches Finalized
Next.js ve Framework Yamaları Tamamlandı

Next.js releases comprehensive patches across all active version lines (15.0.5 through 16.0.7). Other affected frameworks — Waku, RedwoodSDK, React Router — publish their own fixes. Security researchers confirm the patch effectively closes the deserialization vector.

Next.js tüm aktif sürüm hatlarında (15.0.5 ila 16.0.7) kapsamlı yamalar yayınlar. Etkilenen diğer framework'ler — Waku, RedwoodSDK, React Router — kendi düzeltmelerini yayınlar.

Jan–Apr 2026
January – April 2026 (Ongoing)
high
Continued Scanning & Unpatched Exposure
Devam Eden Tarama ve Yamalanmamış Sistemlerin İfşası

Despite available patches, Shodan/Censys surveys reveal thousands of unpatched React RSC deployments remain online. Secondary CVEs (CVE-2026-23864, CVE-2026-23869) are disclosed for additional DoS vectors. OWASP adds insecure deserialization guidance specific to RSC/Flight protocol.

Mevcut yamalara rağmen Shodan/Censys araştırmaları binlerce yamalanmamış React RSC dağıtımının çevrimiçi kaldığını ortaya koyar. İkincil CVE'ler (CVE-2026-23864, CVE-2026-23869) ek DoS vektörleri için açıklanır.

What Was Hacked & How?
🤯 What?? / Neee?
Ne Hacklendi ve Nasıl?

critical
Flight Protocol Deserialization (Root Cause)
Flight Protokolü Serileştirmesi (Kök Neden)

The React "Flight" protocol handles server-client communication for RSC. It deserializes incoming HTTP POST payloads into executable JavaScript objects on the server. The flaw lies in insufficient validation of these payloads — attackers can inject self-referencing object structures that exploit JavaScript's dynamic dispatch, achieving arbitrary code execution with the full privileges of the Node.js process.

React "Flight" protokolü, RSC için sunucu-istemci iletişimini yönetir. Gelen HTTP POST payload'larını sunucuda çalıştırılabilir JavaScript nesnelerine serileştirir. Açık, bu payload'ların yetersiz doğrulanmasında yatar — saldırganlar, JavaScript'in dinamik dispatch'ini istismar eden kendine referans veren nesne yapıları enjekte ederek Node.js sürecinin tam ayrıcalıklarıyla rastgele kod yürütme elde edebilir.

critical
Server Functions as Attack Surface
Saldırı Yüzeyi Olarak Server Function'lar

Any endpoint handling Server Functions (marked with "use server") is exploitable. In Next.js, this includes Server Actions in forms, route handlers, and middleware. The attacker sends a single crafted POST request — no authentication, no session, no prior knowledge of the application is required. The payload bypasses all existing sanitization because it exploits the protocol layer, not the application layer.

"use server" ile işaretlenmiş Server Function'ları işleyen herhangi bir uç nokta istismar edilebilir. Next.js'te bu, form'lardaki Server Action'ları, rota işleyicileri ve middleware'i içerir. Saldırgan tek bir oluşturulmuş POST isteği gönderir — kimlik doğrulaması, oturum veya uygulama hakkında önceden bilgi gerekmez.

high
Source Code Exposure (CVE-2025-55183)
Kaynak Kod İfşası (CVE-2025-55183)

A companion vulnerability allows attackers to force the server to return compiled source code of Server Functions. This can reveal API keys, database credentials, environment variables, and proprietary business logic embedded in server-side code. Even without achieving full RCE, this information disclosure enables further targeted attacks.

Eşlik eden bir güvenlik açığı, saldırganların sunucuyu Server Function'ların derlenmiş kaynak kodunu döndürmeye zorlamasına olanak tanır. Bu, sunucu tarafı koduna gömülü API anahtarlarını, veritabanı kimlik bilgilerini, ortam değişkenlerini ve özel iş mantığını ortaya çıkarabilir.

high
Denial of Service Vectors (CVE-2025-55184)
Hizmet Reddi Vektörleri (CVE-2025-55184)

Additional DoS vulnerabilities in the same deserialization code path allow attackers to trigger memory exhaustion or excessive CPU consumption via specially crafted requests. This can crash the server or degrade performance to the point of unavailability, affecting all users of the application.

Aynı serileştirme kod yolundaki ek DoS güvenlik açıkları, saldırganların özel olarak hazırlanmış istekler aracılığıyla bellek tükenmesi veya aşırı CPU tüketimi tetiklemesine olanak tanır. Bu, sunucuyu çökertebilir veya performansı kullanılamaz noktaya düşürebilir.

Is My React/Next.js Project Affected?
React/Next.js Projem Etkilendi mi?

1
Check if your project uses React Server Components — look for "use server" directives in your codebase

Projenizin React Server Components kullanıp kullanmadığını kontrol edin — kod tabanınızda "use server" direktiflerini arayın

# Search for server directives:

grep -r "use server" src/ --include="_.ts" --include="_.tsx" --include="_.js" --include="_.jsx"
2
Verify your React version — versions 19.0.0, 19.1.0, 19.1.1, and 19.2.0 are VULNERABLE

React sürümünüzü doğrulayın — 19.0.0, 19.1.0, 19.1.1 ve 19.2.0 sürümleri SAVUNMASIZDIR

# Check installed React version:

npm ls react react-dom react-server-dom-webpack

# Or check package.json:

cat package.json | grep -E "react|next"
3
Check for vulnerable react-server-dom-\* packages in your dependency tree

Bağımlılık ağacınızda savunmasız react-server-dom-\* paketlerini kontrol edin

# Audit for known vulnerabilities:

npm audit --json | jq '.vulnerabilities | keys[]'

# Check specific RSC packages:

npm ls react-server-dom-webpack react-server-dom-turbopack react-server-dom-parcel
4
For Next.js: check your version against the patched releases — 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7+

Next.js için: sürümünüzü yamalı sürümlerle karşılaştırın — 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7+

# Check Next.js version:

npx next --version

# Update to latest patched version:

npm install next@latest react@latest react-dom@latest
5
Client-side-only React apps (Create React App, Vite without RSC) are NOT affected

Yalnızca istemci taraflı React uygulamaları (Create React App, RSC olmadan Vite) ETKİLENMEZ

6
Verify your lock file (package-lock.json / yarn.lock) reflects patched versions after updating

Güncelleme sonrasında kilit dosyanızın (package-lock.json / yarn.lock) yamalı sürümleri yansıttığını doğrulayın

# Verify lock file has correct versions:

npm install --package-lock-only
npm audit fix
Multi-Dimensional Analysis
Çok Boyutlu Analiz

Insecure Deserialization
Güvensiz Serileştirme

1
The React "Flight" protocol deserializes client-sent payloads without adequate validation on the server

React "Flight" protokolü, istemciden gönderilen payload'ları sunucuda yeterli doğrulama olmadan serileştirir

2
Attackers craft malicious objects exploiting JavaScript's dynamic dispatch to achieve arbitrary code execution

Saldırganlar, rastgele kod yürütme elde etmek için JavaScript'in dinamik dispatch'ini kullanan kötü amaçlı nesneler oluşturur

3
Self-referencing loops and Blob Handler manipulation bypass all existing sanitization layers

Kendine referans veren döngüler ve Blob Handler manipülasyonu mevcut tüm temizleme katmanlarını atlar

4
A single crafted HTTP POST to any Server Function endpoint triggers full RCE — no auth required

Herhangi bir Server Function uç noktasına gönderilen tek bir oluşturulmuş HTTP POST, tam RCE tetikler — kimlik doğrulaması gerekmez

Server-Side Attack Surface
Sunucu Tarafı Saldırı Yüzeyi

1
Any file with "use server" directive exposes Server Functions as attack endpoints

"use server" direktifi olan herhangi bir dosya, Server Function'ları saldırı uç noktaları olarak ifşa eder

2
Server Actions in forms, API routes, and middleware all serve as entry points

Form'lardaki Server Action'lar, API rotaları ve middleware hepsi giriş noktası olarak hizmet eder

3
RSC renders on the server with full Node.js privileges — compromise means full system access

RSC sunucuda tam Node.js ayrıcalıklarıyla render olur — ele geçirilmesi tam sistem erişimi anlamına gelir

4
Docker containers without restricted capabilities amplify blast radius significantly

Kısıtlı capability'ler olmadan çalışan Docker container'ları patlama yarıçapını önemli ölçüde artırır

Supply Chain & Ecosystem Impact
Tedarik Zinciri ve Ekosistem Etkisi

1
React powers ~43% of all web applications — the blast radius is unprecedented

React tüm web uygulamalarının ~%43'ünü destekler — patlama yarıçapı benzeri görülmemiştir

2
All frameworks implementing RSC are affected: Next.js, Waku, RedwoodSDK, React Router

RSC uygulayan tüm framework'ler etkilenir: Next.js, Waku, RedwoodSDK, React Router

3
Transitive dependency chains mean many teams don't realize they bundle vulnerable RSC packages

Geçişli bağımlılık zincirleri, birçok ekibin savunmasız RSC paketlerini paketlediğinin farkında olmadığı anlamına gelir

4
Enterprise monorepos with pinned versions delayed patching for weeks after disclosure

Sabitlenmiş sürümlere sahip kurumsal monorepo'lar, açıklamadan sonra haftalarca yamayı geciktirdi

Post-Exploitation Techniques
İstismar Sonrası Teknikler

1
Cobalt Strike and Sliver C2 beacons deployed for persistent access and lateral movement

Kalıcı erişim ve yanal hareket için Cobalt Strike ve Sliver C2 beacon'ları dağıtıldı

2
Cryptominer payloads (XMRig) installed on cloud VMs consuming compute resources

Bulut VM'lerde hesaplama kaynaklarını tüketen kripto madenci payload'ları (XMRig) yüklendi

3
Reverse shells established through Node.js child_process.exec() for interactive access

Etkileşimli erişim için Node.js child_process.exec() aracılığıyla ters kabuklar (reverse shell) kuruldu

4
RMM tools and SSH backdoors installed for persistence beyond initial exploit

İlk exploit'in ötesinde kalıcılık için RMM araçları ve SSH arka kapıları yüklendi

Defense & Detection
Savunma ve Tespit

1
WAF rules from Cloudflare, AWS, and Azure can detect and block crafted Flight protocol payloads

Cloudflare, AWS ve Azure'dan WAF kuralları, oluşturulmuş Flight protokolü payload'larını tespit edip engelleyebilir

2
Monitor for unusual POST requests to RSC endpoints and "next-action" headers

RSC uç noktalarına yapılan olağandışı POST isteklerini ve "next-action" başlıklarını izleyin

3
EDR/XDR should alert on unexpected child processes spawned by Node.js/next-server

EDR/XDR, Node.js/next-server tarafından oluşturulan beklenmedik alt süreçler konusunda uyarı vermelidir

4
Implement runtime application self-protection (RASP) for deserialization monitoring

Serileştirme izlemesi için çalışma zamanı uygulama kendini koruma (RASP) uygulayın

How to Patch & Protect
🤯 What?? / Neee?
Nasıl Yamalanır ve Korunur

Immediate Actions
Acil Eylemler

→
Upgrade React to 19.0.1, 19.1.2, or 19.2.1+ immediately — these versions fix all three CVEs

React'i hemen 19.0.1, 19.1.2 veya 19.2.1+ sürümüne yükseltin — bu sürümler üç CVE'nin hepsini düzeltir

→
For Next.js: upgrade to 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, or 16.0.7+

Next.js için: 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7 veya 16.0.7+ sürümüne yükseltin

→
Run npm audit and verify lock files reflect patched versions of react-server-dom-\* packages

npm audit çalıştırın ve kilit dosyalarının react-server-dom-\* paketlerinin yamalı sürümlerini yansıttığını doğrulayın

→
Deploy WAF rules to block anomalous POST requests targeting RSC/Server Action endpoints

RSC/Server Action uç noktalarını hedefleyen anormal POST isteklerini engellemek için WAF kuralları dağıtın

Long-Term Hardening
Uzun Vadeli Sertleştirme

→
Implement Content Security Policy (CSP) headers to limit script execution scope

Betik yürütme kapsamını sınırlamak için Content Security Policy (CSP) başlıkları uygulayın

→
Run Node.js processes with minimal OS privileges — never as root in production

Node.js süreçlerini minimum OS ayrıcalıklarıyla çalıştırın — üretimde asla root olarak çalıştırmayın

→
Use Docker with restricted capabilities (--cap-drop=ALL) and read-only filesystems

Kısıtlı capability'ler (--cap-drop=ALL) ve salt okunur dosya sistemleri ile Docker kullanın

→
Enable automated dependency scanning (Snyk, npm audit, Dependabot) with CI/CD integration

CI/CD entegrasyonu ile otomatik bağımlılık taramasını (Snyk, npm audit, Dependabot) etkinleştirin

→
Implement RASP (Runtime Application Self-Protection) for deserialization monitoring

Serileştirme izlemesi için RASP (Çalışma Zamanı Uygulama Kendini Koruma) uygulayın

Reconnaissance & Scanning Techniques
Keşif ve Tarama Teknikleri

Version Fingerprinting
Sürüm Parmak İzi

Identify vulnerable React/Next.js versions by analyzing response headers, JavaScript bundle metadata, and build manifests. The X-Powered-By header and /\_next/static/ paths reveal framework details.

Yanıt başlıklarını, JavaScript paket meta verilerini ve derleme manifest'lerini analiz ederek savunmasız React/Next.js sürümlerini belirleyin.

# Check response headers for framework fingerprints:

curl -sI https://target.com | grep -iE "(x-powered-by|server|x-nextjs)"

# Analyze build manifest for version info:

curl -s https://target.com/_next/static/buildManifest.js 2>/dev/null
curl -s https://target.com/__nextjs_original-stack-frame 2>/dev/null
RSC Endpoint Discovery
RSC Uç Noktası Keşfi

Discover Server Action endpoints by scanning for the "next-action" header in form submissions and AJAX requests. Server Functions expose predictable URL patterns that can be enumerated.

Form gönderimleri ve AJAX isteklerinde "next-action" başlığını tarayarak Server Action uç noktalarını keşfedin.

# Discover RSC endpoints via common patterns:

curl -X POST https://target.com/ -H "Content-Type: text/x-component" -d ""

# Check for next-action header patterns:

curl -X POST https://target.com/api/ -H "next-action: test" -v 2>&1 | grep -i "next"
Dependency Tree Auditing
Bağımlılık Ağacı Denetimi

Use SCA (Software Composition Analysis) tools to scan your entire dependency tree for vulnerable react-server-dom-\* packages. Transitive dependencies may bundle vulnerable versions even if your direct React version appears safe.

Savunmasız react-server-dom-\* paketleri için tüm bağımlılık ağacınızı taramak üzere SCA araçlarını kullanın.

# Full dependency audit:

npm audit --json | jq '[.vulnerabilities[] | select(.name | test("react"))]'

# Check transitive deps:

npm ls react-server-dom-webpack --all
npm ls react-server-dom-turbopack --all
Exploit Attempt Detection
İstismar Girişimi Tespiti

Monitor server logs for malicious POST payloads targeting RSC endpoints. Look for anomalous request bodies containing self-referencing structures, unexpected Blob handlers, or encoded JavaScript execution primitives.

RSC uç noktalarını hedefleyen kötü amaçlı POST payload'ları için sunucu günlüklerini izleyin.

# Monitor access logs for suspicious RSC requests:

tail -f /var/log/nginx/access.log | grep -E "POST.\*(x-component|next-action)"

# Check for exploitation indicators in Node.js process:

ps aux | grep -E "(node|next)" | grep -v grep
lsof -p $(pgrep -f next-server) | grep -E "(ESTABLISHED|sh|bash)"
References & Sources
React Official Security Advisory
NVD — CVE-2025-55182
Northwave Research — React2Shell
CISA KEV Catalog Entry
Cloudflare Threat Analysis
Palo Alto Unit 42 Report
Trend Micro Deep Analysis
Next.js Security Bulletin
Checkmarx Technical Writeup
Microsoft Defender Advisory
QLine
Bilgi, altyapının kendisidir.

Platform
Ana Sayfa
Paketler
About
Hakkında
Manifesto
Mühendisler
Connect
QLine Technology Solutions · Vadi İstanbul © 2026

Tüm hakları saklıdır.

Profile — QLineTech
