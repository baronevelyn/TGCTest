"""
Script de configuración rápida para el servidor multiplayer.
Configura automáticamente el firewall y muestra la IP local.
"""

import subprocess
import socket

def get_local_ip():
    """Obtener la IP local del PC"""
    try:
        # Crear socket UDP para obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "No se pudo obtener la IP"

def configure_firewall():
    """Configurar firewall de Windows para permitir puerto 5000"""
    print("\n🔒 Configurando Firewall de Windows...")
    
    try:
        # Intentar crear regla de firewall
        cmd = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=TCG Multiplayer Server",
            "dir=in",
            "action=allow",
            "protocol=TCP",
            "localport=5000"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ Regla de firewall creada exitosamente")
        else:
            if "already exists" in result.stderr.lower():
                print("✅ Regla de firewall ya existe")
            else:
                print("⚠️ No se pudo crear la regla automáticamente")
                print("   Ejecuta este script como Administrador o abre el puerto 5000 manualmente")
                return False
        return True
    except Exception as e:
        print(f"⚠️ Error al configurar firewall: {e}")
        print("   Abre el puerto 5000 manualmente en el Firewall de Windows")
        return False

def main():
    print("=" * 60)
    print("🎮 MINI TCG - CONFIGURACIÓN DE SERVIDOR MULTIPLAYER")
    print("=" * 60)
    
    # Obtener IP local
    local_ip = get_local_ip()
    print(f"\n📍 Tu IP Local: {local_ip}")
    print(f"   Los clientes remotos deben conectarse a: http://{local_ip}:5000")
    print(f"   Los clientes locales pueden usar: http://localhost:5000")
    
    # Configurar firewall
    firewall_ok = configure_firewall()
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES:")
    print("=" * 60)
    
    print("\n1️⃣ INICIAR SERVIDOR:")
    print("   cd server")
    print("   python app.py")
    
    print("\n2️⃣ CONFIGURAR CLIENTES:")
    print("   - Cliente local: http://localhost:5000")
    print(f"   - Clientes remotos: http://{local_ip}:5000")
    
    print("\n3️⃣ VERIFICAR CONEXIÓN:")
    print("   Abre un navegador y ve a:")
    print(f"   http://{local_ip}:5000")
    print("   Deberías ver: {'status': 'online', 'message': '...'}")
    
    if not firewall_ok:
        print("\n⚠️  FIREWALL NO CONFIGURADO AUTOMÁTICAMENTE")
        print("   Opciones:")
        print("   A) Ejecutar este script como Administrador")
        print("   B) Configurar manualmente:")
        print("      - Panel de Control > Firewall de Windows")
        print("      - Regla de entrada > Puerto TCP 5000")
    
    print("\n" + "=" * 60)
    print("📖 Para más detalles, consulta:")
    print("   docs/MULTIPLAYER_TESTING_GUIDE.md")
    print("=" * 60)
    
    input("\n✅ Presiona ENTER para continuar...")

if __name__ == "__main__":
    main()
