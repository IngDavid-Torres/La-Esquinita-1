
import requests

BASE_URL = "https://web-production-adfd.up.railway.app"

def test_sesion_completa():
    print("=" * 70)
    print("🔍 TEST DE PERSISTENCIA DE SESIÓN ADMIN")
    print("=" * 70)
    
    session = requests.Session()
    
   
    print("\n📋 PASO 1: GET /login")
    r1 = session.get(f"{BASE_URL}/login")
    print(f"   Status: {r1.status_code}")
    print(f"   Cookies: {dict(session.cookies)}")
    
    
    print("\n🔑 PASO 2: POST /login (admin)")
    datos = {
        'email': 'admin@laesquinita.com',
        'password': 'admin123'
    }
    r2 = session.post(f"{BASE_URL}/login", data=datos, allow_redirects=True)
    print(f"   Status final: {r2.status_code}")
    print(f"   URL final: {r2.url}")
    print(f"   Cookies: {dict(session.cookies)}")
    print(f"   Historia de redirects: {[h.url for h in r2.history]}")
    
    
    if 'Dashboard de Administración' in r2.text:
        print("\n✅ ¡ÉXITO! Panel admin cargado")
    elif 'Iniciar Sesión' in r2.text:
        print("\n❌ FALLO: Redirigido de vuelta al login")
        print("   Esto significa que la sesión no se está guardando correctamente")
    else:
        print(f"\n⚠️ Página desconocida")
        print(f"   Primeros 800 caracteres:\n{r2.text[:800]}")
    
    
    print("\n📍 PASO 3: GET directo a /panel_admin (con sesión)")
    r3 = session.get(f"{BASE_URL}/panel_admin", allow_redirects=True)
    print(f"   Status: {r3.status_code}")
    print(f"   URL final: {r3.url}")
    
    if 'Dashboard de Administración' in r3.text:
        print("   ✅ Sesión mantiene autenticación")
    elif 'Iniciar Sesión' in r3.text:
        print("   ❌ Sesión perdida - redirigido al login")
        print("   Problema: La sesión no persiste entre requests")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_sesion_completa()
