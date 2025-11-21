

import os
from dotenv import load_dotenv


load_dotenv()

def verificar_mercadopago():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE MERCADO PAGO")
    print("=" * 60)
    print()
    
 
    mp_access_token = os.getenv('MP_ACCESS_TOKEN')
    mp_public_key = os.getenv('MP_PUBLIC_KEY')
    
   
    if not mp_access_token:
        print("❌ ERROR: MP_ACCESS_TOKEN no está configurado")
        print("📋 Agrega MP_ACCESS_TOKEN en tu archivo .env")
        print()
        return False
    
    if not mp_public_key:
        print("❌ ERROR: MP_PUBLIC_KEY no está configurado")
        print("📋 Agrega MP_PUBLIC_KEY en tu archivo .env")
        print()
        return False
    
    
    is_test = mp_access_token.startswith('TEST-')
    is_production = mp_access_token.startswith('APP_USR-')
    
    print("✅ Credenciales encontradas")
    print()
    print("-" * 60)
    print("📊 INFORMACIÓN DE CONFIGURACIÓN")
    print("-" * 60)
    
   
    if is_test:
        print("🔧 MODO: 🧪 TEST (Pruebas)")
        print("⚠️  Los pagos son SIMULADOS")
        print("💡 Para producción, usa credenciales APP_USR-")
    elif is_production:
        print("🔧 MODO: ✅ PRODUCCIÓN")
        print("💰 Los pagos son REALES")
        print("🎉 ¡Listo para procesar pagos!")
    else:
        print("🔧 MODO: ❌ DESCONOCIDO")
        print("⚠️  Formato de credencial no reconocido")
    
    print()
    
   
    print("-" * 60)
    print("🔑 CREDENCIALES")
    print("-" * 60)
    print(f"Access Token: {mp_access_token[:30]}...")
    print(f"Public Key:   {mp_public_key[:30]}...")
    print()
    
    
    print("-" * 60)
    print("📋 PRÓXIMOS PASOS")
    print("-" * 60)
    
    if is_test:
        print("1. Obtén credenciales de producción en:")
        print("   https://www.mercadopago.com.mx/developers")
        print()
        print("2. Tu cuenta debe estar certificada")
        print()
        print("3. Reemplaza las credenciales en el archivo .env:")
        print("   MP_ACCESS_TOKEN=APP_USR-tu_access_token")
        print("   MP_PUBLIC_KEY=APP_USR-tu_public_key")
        print()
        print("4. Consulta MERCADOPAGO_PRODUCCION.md para más información")
    elif is_production:
        print("1. ✅ Verifica que tu cuenta esté certificada")
        print("2. ✅ Configura webhooks en el panel de Mercado Pago")
        print("3. ✅ Vincula una cuenta bancaria para recibir pagos")
        print("4. ✅ Realiza una prueba con un pago pequeño")
    
    print()
    print("-" * 60)
    print("🔗 ENLACES ÚTILES")
    print("-" * 60)
    print("📚 Panel de Desarrolladores:")
    print("   https://www.mercadopago.com.mx/developers")
    print()
    print("💰 Balance y Ventas:")
    print("   https://www.mercadopago.com.mx/balance")
    print()
    print("📖 Documentación:")
    print("   https://www.mercadopago.com.mx/developers/es/docs")
    print()
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        verificar_mercadopago()
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()
