
from app import app
import json

def test_captcha_generation():
    print("\n" + "="*60)
    print("TEST: Generación de CAPTCHA")
    print("="*60)
    
    with app.test_client() as client:
       
        print("\n1. Probando /generate_captcha...")
        response = client.get('/generate_captcha')
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.content_type}")
        
        try:
            data = response.get_json()
            print(f"   Success: {data.get('success')}")
            print(f"   Image presente: {'Sí' if data.get('image') else 'No'}")
            
            if data.get('image'):
                img_len = len(data.get('image', ''))
                print(f"   Longitud de imagen: {img_len} caracteres")
                print(f"   Prefix: {data.get('image', '')[:50]}...")
            else:
                print(f"   ⚠️ Image es null!")
                
            if data.get('error'):
                print(f"   ❌ Error: {data.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Error parseando JSON: {e}")
            print(f"   Response data: {response.data[:200]}")
        
        
        with client.session_transaction() as sess:
            if 'captcha_code' in sess:
                print(f"\n2. ✅ Código CAPTCHA en sesión: {sess['captcha_code']}")
            else:
                print(f"\n2. ❌ No hay código CAPTCHA en la sesión")
    
    print("\n" + "="*60)
    print("TEST COMPLETADO")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_captcha_generation()
