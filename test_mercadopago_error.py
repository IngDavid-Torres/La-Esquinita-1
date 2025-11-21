
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 DIAGNÓSTICO DE ERROR 500 EN PAGO_MERCADOPAGO")
print("=" * 60)


print("\n1️⃣ VERIFICANDO CREDENCIALES DE MERCADOPAGO:")
print("-" * 60)

MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')
MP_PUBLIC_KEY = os.environ.get('MP_PUBLIC_KEY')

if MP_ACCESS_TOKEN:
    print(f"✅ MP_ACCESS_TOKEN configurado: {MP_ACCESS_TOKEN[:30]}...")
    if MP_ACCESS_TOKEN.startswith('TEST-'):
        print("   🧪 Modo: TEST")
    else:
        print("   🔴 Modo: PRODUCCIÓN")
else:
    print("❌ MP_ACCESS_TOKEN NO configurado")

if MP_PUBLIC_KEY:
    print(f"✅ MP_PUBLIC_KEY configurado: {MP_PUBLIC_KEY[:30]}...")
else:
    print("❌ MP_PUBLIC_KEY NO configurado")


print("\n2️⃣ VERIFICANDO SDK DE MERCADOPAGO:")
print("-" * 60)

try:
    import mercadopago
    print(f"✅ mercadopago instalado - versión: {mercadopago.__version__ if hasattr(mercadopago, '__version__') else 'desconocida'}")
    
    
    try:
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        print("✅ SDK inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar SDK: {e}")
        
except ImportError as e:
    print(f"❌ mercadopago NO instalado: {e}")
    print("   Ejecuta: pip install mercadopago")


print("\n3️⃣ PROBANDO CREACIÓN DE PREFERENCIA:")
print("-" * 60)

try:
    from mercadopago_config import create_preference, is_test_environment
    
    print(f"✅ Módulo mercadopago_config importado")
    print(f"   Modo test: {is_test_environment()}")
    
   
    items_test = [{
        "title": "Producto de prueba",
        "quantity": 1,
        "unit_price": 100.0,
        "currency_id": "MXN"
    }]
    
    payer_test = {
        "name": "Usuario Prueba",
        "email": "test@test.com"
    }
    
    urls_test = {
        "success": "https://web-production-adfd.up.railway.app/pago_exitoso",
        "failure": "https://web-production-adfd.up.railway.app/pago_fallido",
        "pending": "https://web-production-adfd.up.railway.app/pago_pendiente"
    }
    
    external_ref = "test-123456"
    
    print("\n   Intentando crear preferencia de prueba...")
    result = create_preference(items_test, payer_test, urls_test, external_ref)
    
    if result:
        if result.get("status") == 201:
            print("   ✅ Preferencia creada exitosamente")
            print(f"   ID: {result['response'].get('id', 'N/A')}")
            print(f"   Init Point: {result['response'].get('init_point', 'N/A')[:50]}...")
        else:
            print(f"   ⚠️ Respuesta con status: {result.get('status')}")
            print(f"   Contenido: {result}")
    else:
        print("   ❌ create_preference retornó None")
        
except Exception as e:
    print(f"❌ Error al probar preferencia: {e}")
    import traceback
    print("\n📋 TRACEBACK COMPLETO:")
    traceback.print_exc()


print("\n4️⃣ VERIFICANDO CONEXIÓN A API DE MERCADOPAGO:")
print("-" * 60)

try:
    import requests
    response = requests.get("https://api.mercadopago.com/v1/payment_methods", 
                           headers={"Authorization": f"Bearer {MP_ACCESS_TOKEN}"},
                           timeout=10)
    
    if response.status_code == 200:
        print("✅ Conexión exitosa a la API de MercadoPago")
        print(f"   Métodos de pago disponibles: {len(response.json())}")
    else:
        print(f"⚠️ Respuesta de API: {response.status_code}")
        print(f"   {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error al conectar con API: {e}")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 60)
