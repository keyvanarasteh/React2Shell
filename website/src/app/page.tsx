import { submitForm, getServerInfo } from "./actions";

export default async function HomePage() {
  // Server Component — sunucuda render edilir
  const serverInfo = await getServerInfo();

  return (
    <>
      {/* Header */}
      <header className="header">
        <a href="/" className="logo">
          <span className="logo-icon">⚡</span>
          TechCorp
        </a>
        <nav>
          <ul className="nav">
            <li><a href="/">Ana Sayfa</a></li>
            <li><a href="#contact">İletişim</a></li>
            <li><a href="#info">Sunucu Bilgisi</a></li>
            <li>
              <a href="#api">API <span className="nav-badge">v2</span></a>
            </li>
          </ul>
        </nav>
      </header>

      {/* Hero */}
      <section className="hero">
        <h1>🏢 TechCorp İletişim Portalı</h1>
        <p>Kurumsal destek ve iletişim platformu — React Server Components ile güçlendirilmiştir</p>
      </section>

      {/* Main Content */}
      <main className="main">
        {/* İletişim Formu — Server Action */}
        <section className="card" id="contact">
          <h2>
            <span className="card-icon">📨</span>
            Bize Ulaşın
          </h2>
          <form action={submitForm}>
            <div className="form-group">
              <label htmlFor="name">Ad Soyad</label>
              <input
                type="text"
                id="name"
                name="name"
                placeholder="Adınızı girin..."
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">E-posta</label>
              <input
                type="email"
                id="email"
                name="email"
                placeholder="ornek@email.com"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="subject">Konu</label>
              <select id="subject" name="subject">
                <option value="destek">Teknik Destek</option>
                <option value="satis">Satış</option>
                <option value="ortaklik">Ortaklık</option>
                <option value="diger">Diğer</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="message">Mesajınız</label>
              <textarea
                id="message"
                name="message"
                placeholder="Mesajınızı yazın..."
                rows={4}
                required
              />
            </div>
            <button type="submit" className="btn">
              🚀 Gönder
            </button>
          </form>
        </section>

        {/* Sunucu Bilgisi — Server Component */}
        <section className="card" id="info">
          <h2>
            <span className="card-icon">🖥️</span>
            Sunucu Bilgisi
          </h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Node.js</span>
              <span className="info-value">{serverInfo.nodeVersion}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Platform</span>
              <span className="info-value">{serverInfo.platform}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Mimari</span>
              <span className="info-value">{serverInfo.arch}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Ortam</span>
              <span className="info-value">{serverInfo.env}</span>
            </div>
            <div className="info-item">
              <span className="info-label">PID</span>
              <span className="info-value">{serverInfo.pid}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Bellek (RSS)</span>
              <span className="info-value">{serverInfo.memoryUsage.rss}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Heap Kullanımı</span>
              <span className="info-value">{serverInfo.memoryUsage.heapUsed}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Çalışma Süresi</span>
              <span className="info-value">{serverInfo.uptime}s</span>
            </div>
            <div className="info-item">
              <span className="info-label">Çalışma Dizini</span>
              <span className="info-value" style={{ fontSize: "0.75rem" }}>{serverInfo.cwd}</span>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          © 2026 TechCorp Technology Solutions — React Server Components ile güçlendirilmiştir
        </p>
        <p>
          Sürüm: <span className="version">Next.js 15.0.3 | React 19.0.0</span>
        </p>
      </footer>
    </>
  );
}
