#!/usr/bin/env python3
"""
Servidor web simples para o Frontend do Scoras AI Agent
Serve arquivos estáticos com suporte a CORS
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse
import webbrowser
import threading
import time

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP com suporte a CORS"""
    
    def end_headers(self):
        # Adicionar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        # Desabilitar cache para arquivos JS/CSS durante desenvolvimento
        if self.path.endswith(('.js', '.css')):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = self.log_date_time_string()
        print(f"[{timestamp}] {format % args}")

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            # Servir index.html com injeção da variável de ambiente
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                api_base_url = os.environ.get('API_BASE_URL', 'http://localhost:8003')
                injection = f'<script>window.API_BASE_URL = "{api_base_url}";</script>'
                # Inserir antes do </head>
                if '</head>' in html:
                    html = html.replace('</head>', injection + '\n</head>')
                else:
                    html = injection + html
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                self.send_error(500, f'Erro ao servir index.html: {e}')
        else:
            super().do_GET()

def open_browser(url, delay=2):
    """Abrir o navegador após um delay"""
    time.sleep(delay)
    print(f"🌐 Abrindo navegador: {url}")
    webbrowser.open(url)

def start_server(port=3000, auto_open=True):
    """Iniciar o servidor web"""
    
    # Mudar para o diretório do frontend
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    # Verificar se os arquivos necessários existem
    required_files = ['index.html', 'style.css', 'script.js']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Arquivos não encontrados: {missing_files}")
        print(f"📁 Diretório atual: {os.getcwd()}")
        return False
    
    # Configurar servidor
    handler = CORSHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            server_url = f"http://localhost:{port}"
            
            print("🚀 Scoras AI Agent Frontend Server")
            print("=" * 50)
            print(f"📁 Servindo arquivos de: {frontend_dir}")
            print(f"🌐 URL: {server_url}")
            print(f"🔗 API Backend: http://localhost:8003")
            print("=" * 50)
            print(f"✅ Servidor iniciado na porta {port}")
            print("💡 Pressione Ctrl+C para parar o servidor")
            print()
            
            # Abrir navegador automaticamente
            if auto_open:
                browser_thread = threading.Thread(
                    target=open_browser, 
                    args=(server_url,)
                )
                browser_thread.daemon = True
                browser_thread.start()
            
            # Iniciar servidor
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
        return True
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Porta {port} já está em uso!")
            print(f"💡 Tente usar uma porta diferente: python server.py --port {port + 1}")
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Servidor Frontend para Scoras AI Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python server.py                    # Porta padrão 3000
  python server.py --port 8080        # Porta personalizada
  python server.py --no-browser       # Não abrir navegador
  python server.py --port 5000 --no-browser
"""
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=3000,
        help='Porta do servidor (padrão: 3000)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Não abrir o navegador automaticamente'
    )
    
    args = parser.parse_args()
    
    # Verificar se a porta está disponível
    if args.port < 1024:
        print("⚠️  Aviso: Portas abaixo de 1024 podem precisar de privilégios administrativos")
    
    # Iniciar servidor
    success = start_server(
        port=args.port,
        auto_open=not args.no_browser
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()