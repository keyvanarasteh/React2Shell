#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React2Shell — Faz 7: Web Kontrol Paneli (06_full_chain_panel.py)
Tam saldırı zincirini modern bir Flask arayüzü üzerinden yönetir.
"""

import os
import sys
import json
import time
import threading
import importlib.util
import queue
from flask import Flask, render_template_string, request, jsonify, Response

# utils'den yardımcıları al
from utils import (
    BANNER, Colors, timestamp, enable_tor
)

# Diğer scriptleri dinamik olarak yükle
def load_module(name, path):
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return None

recon = load_module("recon", "01_recon.py")
source_leak = load_module("source_leak", "02_source_leak.py")
dos = load_module("dos", "03_dos.py")
rce = load_module("rce", "04_rce.py")

app = Flask(__name__)

# Global log kuyruğu
log_queue = queue.Queue()

class WebLogger:
    """sys.stdout'u yakalayıp log kuyruğuna ve terminale gönderen sınıf"""
    def __init__(self, original_stdout):
        self.terminal = original_stdout
        
    def write(self, message):
        self.terminal.write(message)
        if message.strip():
            # ANSI renk kodlarını HTML renklerine dönüştürebiliriz veya ham bırakabiliriz
            # Basitlik için terminal renklerini destekleyen bir kütüphane veya basit temizleme
            log_queue.put(message)
            
    def flush(self):
        self.terminal.flush()

# Stdout'u yönlendir
sys.stdout = WebLogger(sys.stdout)

# HTML/CSS/JS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>React2Shell | C&C Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050608;
            --surface: rgba(255, 255, 255, 0.03);
            --surface-hover: rgba(255, 255, 255, 0.06);
            --accent: #00f2ff;
            --accent-glow: rgba(0, 242, 255, 0.3);
            --danger: #ff0055;
            --success: #00ff95;
            --text: #e0e0e0;
            --text-dim: #888888;
            --border: rgba(255, 255, 255, 0.1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% -20%, var(--accent-glow), transparent 40%),
                radial-gradient(circle at 0% 0%, rgba(255,0,85,0.05), transparent 30%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        header {
            text-align: center;
            margin-bottom: 50px;
            animation: fadeInDown 0.8s ease-out;
        }

        .logo {
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -2px;
            color: #fff;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .logo span {
            color: var(--accent);
            text-shadow: 0 0 20px var(--accent-glow);
        }

        .subtitle {
            color: var(--text-dim);
            font-size: 1.1rem;
            letter-spacing: 2px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }

        .card {
            background: var(--surface);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }

        h2 {
            font-size: 1.5rem;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        h2::before {
            content: '';
            display: block;
            width: 4px;
            height: 24px;
            background: var(--accent);
            border-radius: 2px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            color: var(--text-dim);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        input[type="text"] {
            width: 100%;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            padding: 15px 20px;
            border-radius: 12px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1rem;
            transition: all 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 15px var(--accent-glow);
        }

        .checkbox-group {
            display: grid;
            gap: 15px;
            margin-bottom: 30px;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 18px;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }

        .checkbox-item:hover {
            background: var(--surface-hover);
        }

        .checkbox-item.active {
            border-color: var(--accent);
            background: rgba(0, 242, 255, 0.05);
        }

        .checkbox-item input {
            display: none;
        }

        .checkbox-item .indicator {
            width: 20px;
            height: 20px;
            border: 2px solid var(--border);
            border-radius: 6px;
            position: relative;
        }

        .checkbox-item input:checked + .indicator {
            background: var(--accent);
            border-color: var(--accent);
        }

        .checkbox-item input:checked + .indicator::after {
            content: '✓';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #000;
            font-size: 12px;
            font-weight: bold;
        }

        .tor-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(160, 0, 255, 0.05);
            border: 1px solid rgba(160, 0, 255, 0.2);
            padding: 15px 20px;
            border-radius: 16px;
            margin-bottom: 30px;
        }

        .tor-toggle span {
            font-weight: 600;
            color: #d8a0ff;
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 26px;
        }

        .switch input { opacity: 0; width: 0; height: 0; }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(255,255,255,0.1);
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 18px; width: 18px;
            left: 4px; bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider { background-color: #a000ff; }
        input:checked + .slider:before { transform: translateX(24px); }

        .btn-launch {
            width: 100%;
            background: linear-gradient(135deg, var(--accent), #00a2ff);
            color: #000;
            border: none;
            padding: 20px;
            border-radius: 16px;
            font-size: 1.2rem;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 30px var(--accent-glow);
        }

        .btn-launch:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px var(--accent-glow);
        }

        .btn-launch:active {
            transform: translateY(1px);
        }

        .terminal {
            background: #000;
            border-radius: 16px;
            padding: 25px;
            font-family: 'JetBrains Mono', monospace;
            height: 600px;
            overflow-y: auto;
            position: relative;
            border: 1px solid var(--border);
        }

        .terminal-header {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
            position: sticky;
            top: 0;
            background: #000;
            padding-bottom: 10px;
        }

        .dot { width: 12px; height: 12px; border-radius: 50%; }
        .dot.red { background: #ff5f56; }
        .dot.yellow { background: #ffbd2e; }
        .dot.green { background: #27c93f; }

        .log-entry {
            margin-bottom: 6px;
            line-height: 1.5;
            font-size: 0.95rem;
            white-space: pre-wrap;
        }

        /* Terminal Colors */
        .log-entry.blue { color: #00d9ff; }
        .log-entry.green { color: #00ff95; }
        .log-entry.red { color: #ff0055; }
        .log-entry.yellow { color: #ffdd00; }
        .log-entry.magenta { color: #ff00ff; }
        .log-entry.dim { color: #555; }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .status-idle { background: rgba(255,255,255,0.1); color: #fff; }
        .status-running { background: var(--accent-glow); color: var(--accent); animation: pulse 2s infinite; }

        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">REACT<span>2</span>SHELL</div>
            <div class="subtitle">CVE-2025-55182 CONTROL CENTER</div>
        </header>

        <div class="grid">
            <div class="sidebar">
                <div class="card">
                    <h2>Konfigürasyon</h2>
                    
                    <div class="form-group">
                        <label>Hedef URL</label>
                        <input type="text" id="target" value="http://localhost:3000" placeholder="https://target.com">
                    </div>

                    <div class="tor-toggle">
                        <span>Tor Proxy (SOCKS5)</span>
                        <label class="switch">
                            <input type="checkbox" id="tor">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <label>Saldırı Fazları</label>
                    <div class="checkbox-group">
                        <label class="checkbox-item active">
                            <input type="checkbox" checked id="phase-recon">
                            <div class="indicator"></div>
                            <span>Phase 1: Reconnaissance</span>
                        </label>
                        <label class="checkbox-item active">
                            <input type="checkbox" checked id="phase-source">
                            <div class="indicator"></div>
                            <span>Phase 2: Source Leak</span>
                        </label>
                        <label class="checkbox-item active">
                            <input type="checkbox" id="phase-dos">
                            <div class="indicator"></div>
                            <span>Phase 3: Denial of Service</span>
                        </label>
                        <label class="checkbox-item active">
                            <input type="checkbox" checked id="phase-rce">
                            <div class="indicator"></div>
                            <span>Phase 4: Remote Code Execution</span>
                        </label>
                    </div>

                    <button class="btn-launch" id="launch-btn" onclick="startAttack()">Saldırıyı Başlat</button>
                    
                    <div id="status-container" style="margin-top: 20px; text-align: center;">
                        <span class="status-badge status-idle" id="status-text">HAZIR</span>
                    </div>
                </div>
            </div>

            <div class="main-panel">
                <div class="terminal" id="terminal">
                    <div class="terminal-header">
                        <div class="dot red"></div>
                        <div class="dot yellow"></div>
                        <div class="dot green"></div>
                        <span style="color: #555; font-size: 0.8rem; margin-left: 10px;">live_output.log</span>
                    </div>
                    <div id="logs">
                        <div class="log-entry dim">[*] Komuta hazır. Hedef belirleyin ve saldırıyı başlatın...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const logsDiv = document.getElementById('logs');
        const terminal = document.getElementById('terminal');
        const launchBtn = document.getElementById('launch-btn');
        const statusText = document.getElementById('status-text');

        function appendLog(text) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            
            // Basit ANSI -> CSS renk dönüşümü
            if (text.includes('[*]')) entry.classList.add('blue');
            if (text.includes('[+]')) entry.classList.add('green');
            if (text.includes('[!]')) entry.classList.add('yellow');
            if (text.includes('[-]')) entry.classList.add('red');
            if (text.includes('[!!]')) {
                entry.classList.add('red');
                entry.style.fontWeight = 'bold';
                entry.style.background = 'rgba(255,0,0,0.1)';
            }
            
            entry.textContent = text;
            logsDiv.appendChild(entry);
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function startAttack() {
            const target = document.getElementById('target').value;
            const tor = document.getElementById('tor').checked;
            
            const phases = [];
            if (document.getElementById('phase-recon').checked) phases.push('recon');
            if (document.getElementById('phase-source').checked) phases.push('source');
            if (document.getElementById('phase-dos').checked) phases.push('dos');
            if (document.getElementById('phase-rce').checked) phases.push('rce');

            if (!target) {
                alert('Lütfen bir hedef URL girin.');
                return;
            }

            launchBtn.disabled = true;
            launchBtn.style.opacity = '0.5';
            statusText.className = 'status-badge status-running';
            statusText.textContent = 'SALDIRI DEVAM EDİYOR';
            
            logsDiv.innerHTML = '<div class="log-entry dim">[*] Saldırı zinciri başlatılıyor...</div>';

            const response = await fetch('/api/attack', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target, tor, phases })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n');
                lines.forEach(line => {
                    if (line.trim()) appendLog(line);
                });
            }

            launchBtn.disabled = false;
            launchBtn.style.opacity = '1';
            statusText.className = 'status-badge status-idle';
            statusText.textContent = 'TAMAMLANDI';
        }

        // Checkbox styling
        document.querySelectorAll('.checkbox-item input').forEach(input => {
            input.addEventListener('change', (e) => {
                if (e.target.checked) {
                    e.target.closest('.checkbox-item').classList.add('active');
                } else {
                    e.target.closest('.checkbox-item').classList.remove('active');
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/attack', methods=['POST'])
def attack():
    data = request.json
    target = data.get('target')
    tor = data.get('tor')
    phases = data.get('phases', [])
    
    def run_chain():
        # Tor ayarı
        if tor:
            enable_tor()
            
        # 0. Hedef Doğrulama
        print(f"[*] Hedef: {target}")
        print(f"[*] Zaman: {timestamp()}")
        
        from utils import check_target
        health_data = check_target(target)
        if not health_data:
            print("[-] Hedef ulaşılamaz, zincir durduruldu.")
            return

        # Faz 1: Keşif
        if "recon" in phases and recon:
            try:
                recon.run_recon(target)
            except Exception as e:
                print(f"[-] Keşif hatası: {e}")
                
        # Faz 2: Kaynak Kod İfşası
        if "source" in phases and source_leak:
            try:
                source_leak.execute_source_leak(target)
            except Exception as e:
                print(f"[-] Source leak hatası: {e}")
                
        # Faz 3: DoS
        if "dos" in phases and dos:
            try:
                dos.execute_dos(target)
            except Exception as e:
                print(f"[-] DoS hatası: {e}")
                
        # Faz 4: RCE
        if "rce" in phases and rce:
            try:
                rce.execute_rce(target)
            except Exception as e:
                print(f"[-] RCE hatası: {e}")
        
        print("[+] Tam Saldırı Zinciri Operasyonu Tamamlandı.")

    def generate():
        # Saldırıyı ayrı bir thread'de başlat
        thread = threading.Thread(target=run_chain)
        thread.start()
        
        # Kuyruktan logları oku ve SSE olarak gönder
        while thread.is_alive() or not log_queue.empty():
            try:
                msg = log_queue.get(timeout=0.1)
                yield msg
            except queue.Empty:
                continue
                
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    # Banner yazdır
    print(BANNER)
    print(f"[*] React2Shell Kontrol Paneli başlatılıyor...")
    print(f"[*] Panel adresi: {Colors.CYAN}http://127.0.0.1:5005{Colors.RESET}")
    
    # Port 5005 (user setup ile uyumlu olması için veya boş bir port)
    app.run(host='0.0.0.0', port=5005, debug=False)
