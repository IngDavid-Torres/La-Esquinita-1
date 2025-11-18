
import requests
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except ImportError:
    from requests.packages.urllib3.util.retry import Retry


BASE_URL = "https://web-production-adfd.up.railway.app"


def crear_sesion():
    
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def test_login_admin():
   
    print("=" * 70)
    print("🧪 TEST COMPLETO DE LOGIN ADMIN")
    print("=" * 70)
    
    session = crear_sesion()
    
    
    print("\n📋 PASO 1: Accediendo a /login para obtener sesión...")
    try:
        response_get = session.get(f"{BASE_URL}/login", timeout=10)
        print(f"   Status: {response_get.status_code}")
        print(f"   Cookies: {dict(session.cookies)}")
        
        if response_get.status_code != 200:
            print(f"   ❌ Error: No se pudo cargar la página de login")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return
    
   
    print("\n🔑 PASO 2: Enviando credenciales admin...")
    datos_login = {
        'email': 'admin@laesquinita.com',
        'password': 'admin123',
        'captcha': ''  # Admin no requiere CAPTCHA
    }
    
    try:
        response_post = session.post(
            f"{BASE_URL}/login",
            data=datos_login,
            allow_redirects=False,  # No seguir redirects automáticamente
            timeout=10,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        print(f"   Status: {response_post.status_code}")
        print(f"   Headers: {dict(response_post.headers)}")
        print(f"   Cookies después de POST: {dict(session.cookies)}")
        
     
        if response_post.status_code in [301, 302, 303, 307, 308]:
            location = response_post.headers.get('Location', 'No redirect')
            print(f"\n✅ REDIRECT DETECTADO: {location}")
            
            if 'panel_admin' in location:
                print("   ✅ ¡Redirect correcto a panel_admin!")
                
                
                print("\n📍 PASO 3: Siguiendo redirect a panel_admin...")
                
                
                if location.startswith('http'):
                    redirect_url = location
                elif location.startswith('/'):
                    redirect_url = f"{BASE_URL}{location}"
                else:
                    redirect_url = f"{BASE_URL}/{location}"
                
                response_panel = session.get(redirect_url, timeout=10)
                print(f"   Status: {response_panel.status_code}")
                print(f"   Content-Type: {response_panel.headers.get('Content-Type')}")
                print(f"   Tamaño respuesta: {len(response_panel.text)} caracteres")
                
                if response_panel.status_code == 200:
                    if 'Dashboard de Administración' in response_panel.text:
                        print("\n🎉 ¡¡¡ÉXITO!!! Panel admin cargado correctamente")
                        print("   ✅ Se encontró 'Dashboard de Administración' en la respuesta")
                    else:
                        print("\n⚠️ Página cargada pero no es panel_admin")
                        print(f"   Primeros 500 caracteres:\n{response_panel.text[:500]}")
                else:
                    print(f"\n❌ Error al cargar panel_admin: {response_panel.status_code}")
            else:
                print(f"   ⚠️ Redirect a lugar incorrecto: {location}")
        
        elif response_post.status_code == 200:
            print(f"\n⚠️ Status 200 (sin redirect)")
            print("   Esto significa que el login NO está redirigiendo")
            
           
            if 'Credenciales incorrectas' in response_post.text:
                print("   ❌ Error: Credenciales incorrectas")
            elif 'CAPTCHA' in response_post.text:
                print("   ⚠️ Aún pide CAPTCHA para admin")
            else:
                print(f"   Primeros 300 caracteres de respuesta:\n{response_post.text[:300]}")
        
        else:
            print(f"\n❌ Status inesperado: {response_post.status_code}")
            print(f"   Respuesta: {response_post.text[:500]}")
    
    except Exception as e:
        print(f"\n❌ Error en POST: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_admin()
    print("\n" + "=" * 70)
    print("Diagnóstico completo finalizado")
    print("=" * 70)
