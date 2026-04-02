#!/usr/bin/env python3
"""
Script para inicializar o Scoras AI Agent com Dashboard Administrativo
"""

import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process

def run_chat_api():
    """Rodar o chat API principal na porta 8000"""
    print("🚀 Iniciando Chat API na porta 8000...")
    os.system("python chat_api_rag_fixed.py")

def run_admin_dashboard():
    """Rodar o dashboard administrativo na porta 8001"""
    print("📊 Iniciando Admin Dashboard na porta 8001...")
    os.system("python admin_dashboard.py")

def signal_handler(sig, frame):
    """Handler para encerrar processos graciosamente"""
    print("\n\n🛑 Encerrando serviços...")
    sys.exit(0)

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 SCORAS AI AGENT                        ║
║                  Admin Dashboard Startup                     ║
╚══════════════════════════════════════════════════════════════╝

Iniciando serviços:
  • Chat API: http://localhost:8000
  • Admin Dashboard: http://localhost:8001/admin

Pressione Ctrl+C para parar todos os serviços.
    """)

    # Registrar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Verificar se as dependências estão instaladas
        required_packages = [
            'fastapi', 'uvicorn', 'redis', 'azure-ai-inference', 'pydantic'
        ]
        
        print("🔍 Verificando dependências...")
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} - Execute: pip install {package}")
                return

        # Verificar se os arquivos necessários existem
        required_files = [
            'chat_api_rag_fixed.py',
            'admin_dashboard.py', 
            'admin_dashboard.html'
        ]
        
        print("\n📁 Verificando arquivos...")
        for file in required_files:
            if os.path.exists(file):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - Arquivo não encontrado!")
                return

        # Verificar variáveis de ambiente
        print("\n🔧 Verificando configuração...")
        env_vars = ['AZURE_API_KEY', 'AZURE_ENDPOINT', 'REDIS_URL']
        for var in env_vars:
            if os.getenv(var):
                print(f"  ✅ {var}")
            else:
                print(f"  ⚠️  {var} - Não configurado (usando padrão)")

        print("\n" + "="*60)
        
        # Iniciar processos
        chat_process = Process(target=run_chat_api)
        admin_process = Process(target=run_admin_dashboard)
        
        chat_process.start()
        time.sleep(3)  # Aguardar chat API inicializar
        admin_process.start()
        
        print("\n🎉 Serviços iniciados com sucesso!")
        print("\n📱 URLs disponíveis:")
        print("  • Chat Interface: http://localhost:8000")
        print("  • API Docs: http://localhost:8000/docs")
        print("  • Admin Dashboard: http://localhost:8001/admin")
        print("  • Health Check: http://localhost:8000/health")
        
        print("\n💡 Dicas:")
        print("  • Use o Admin Dashboard para monitorar conversas")
        print("  • Execute queries Redis diretamente no dashboard")
        print("  • Visualize métricas e analytics em tempo real")
        
        # Aguardar processos
        chat_process.join()
        admin_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Encerrando serviços...")
        if 'chat_process' in locals():
            chat_process.terminate()
        if 'admin_process' in locals():
            admin_process.terminate()
    except Exception as e:
        print(f"\n❌ Erro ao iniciar serviços: {e}")
        
if __name__ == "__main__":
    main() 