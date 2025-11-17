import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error instalando {package}")
        return False

def main():
    print("🌽 La Esquinita - Instalador de dependencias CAPTCHA")
    print("=" * 50)
    
    packages = [
        "Pillow",
    ]
    
    success_count = 0
    
    for package in packages:
        print(f"\n📦 Instalando {package}...")
        if install_package(package):
            success_count += 1
    
    print(f"\n🎉 Instalación completada: {success_count}/{len(packages)} paquetes")
    
    if success_count == len(packages):
        print("\n✅ ¡Todas las dependencias del CAPTCHA están listas!")
        print("\n📋 Próximos pasos:")
        print("1. Agrega las rutas de captcha_routes.py a tu app.py")
        print("2. Reinicia tu aplicación Flask")  
        print("3. El CAPTCHA estará funcionando en el login")
    else:
        print("\n⚠️  Algunas dependencias no se instalaron correctamente")
        print("Intenta instalar manualmente: pip install Pillow")

if __name__ == "__main__":
    main()