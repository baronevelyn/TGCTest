"""
Test Script - Verifica que el servidor esté listo para Render
"""

import sys
import os

def check_file_exists(filepath, description):
    """Verifica que un archivo exista"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} no encontrado: {filepath}")
        return False

def check_requirements():
    """Verifica que requirements.txt tenga las dependencias necesarias"""
    required_packages = [
        'Flask',
        'Flask-SocketIO',
        'gevent',
        'python-socketio',
        'gunicorn'
    ]
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    missing = []
    for package in required_packages:
        if package.lower() not in content:
            missing.append(package)
    
    if missing:
        print(f"❌ Faltan dependencias en requirements.txt: {', '.join(missing)}")
        return False
    else:
        print(f"✅ Todas las dependencias necesarias están en requirements.txt")
        return True

def check_server_code():
    """Verifica que el servidor use PORT del entorno"""
    with open('server/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'os.environ.get(\'PORT\'' in content or 'os.environ.get("PORT"' in content:
        print("✅ Servidor configurado para usar PORT del entorno")
        return True
    else:
        print("❌ Servidor no usa PORT del entorno (necesario para Render)")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 VERIFICACIÓN PRE-DEPLOY PARA RENDER.COM")
    print("="*60 + "\n")
    
    checks = []
    
    # Verificar archivos necesarios
    print("📁 Verificando archivos de configuración...\n")
    checks.append(check_file_exists('render.yaml', 'Configuración de Render'))
    checks.append(check_file_exists('server.py', 'Punto de entrada WSGI'))
    checks.append(check_file_exists('requirements.txt', 'Dependencias'))
    checks.append(check_file_exists('runtime.txt', 'Versión de Python'))
    checks.append(check_file_exists('server/app.py', 'Servidor Socket.IO'))
    
    print("\n📦 Verificando dependencias...\n")
    checks.append(check_requirements())
    
    print("\n⚙️  Verificando código del servidor...\n")
    checks.append(check_server_code())
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ ¡TODO LISTO PARA DEPLOY!")
        print("="*60)
        print("\n📋 Próximos pasos:")
        print("1. Sube el código a GitHub:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Ready for Render'")
        print("   git remote add origin https://github.com/TU_USUARIO/TGCTest.git")
        print("   git push -u origin main")
        print("\n2. Ve a render.com y crea un Web Service")
        print("3. Conecta tu repositorio de GitHub")
        print("4. Render detectará automáticamente la configuración")
        print("5. Haz clic en 'Create Web Service'")
        print("\n📖 Guía completa: DEPLOY_RENDER.md")
        print("🚀 Quick Start: QUICK_START_RENDER.md")
    else:
        print("❌ HAY PROBLEMAS - Revisa los errores arriba")
        print("="*60)
        return 1
    
    print("\n" + "="*60)
    return 0

if __name__ == '__main__':
    sys.exit(main())
