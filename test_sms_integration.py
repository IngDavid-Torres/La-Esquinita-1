
from app import app
import requests

def test_sms_diagnostic():
    
    print("\n" + "="*60)
    print("🔍 PRUEBA 1: Diagnóstico del Sistema SMS")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/sms_diagnostico')
        data = response.get_json()
        
        if data.get('success'):
            diag = data['diagnostico']
            print("\n✅ Estado de Configuración:")
            print(f"   Account SID: {'✅' if diag['twilio_account_sid_present'] else '❌'}")
            print(f"   Auth Token: {'✅' if diag['twilio_auth_token_present'] else '❌'}")
            print(f"   Phone Number: {'✅' if diag['twilio_phone_number_present'] else '❌'}")
            print(f"   Messaging Service: {'✅' if diag['twilio_messaging_service_sid_present'] else '❌'}")
            print(f"   Modo: {'🔧 Desarrollo' if diag['development_mode'] else '🚀 Producción'}")
            print(f"   Ejemplo código: {diag['example_generated_code']}")
            
            if not diag['twilio_messaging_service_sid_present']:
                print("\n⚠️ NOTA: Sin Messaging Service configurado")
                print("   Se usará el número de teléfono directamente")
                print("   Para mejor entregabilidad, configura un Messaging Service")
                print("   Ver: CONFIGURACION_TWILIO.md - Paso 2")
        else:
            print(f"❌ Error: {data.get('error')}")

def test_sms_send(phone_number):
   
    print("\n" + "="*60)
    print("📱 PRUEBA 2: Envío de Código de Verificación")
    print("="*60)
    print(f"📞 Enviando SMS a: {phone_number}")
    
    with app.test_client() as client:
        response = client.post('/send_sms_verification', 
                               data={'phone_number': phone_number})
        data = response.get_json()
        
        if data.get('success'):
            print(f"\n✅ {data['message']}")
            print(f"📱 Número normalizado: {data['phone_number']}")
            print("\n⏰ El código expira en 10 minutos")
            print("📲 Revisa tu celular para el código")
            return True
        else:
            print(f"\n❌ Error: {data.get('message')}")
            return False

def test_sms_verify(phone_number, code):
    
    print("\n" + "="*60)
    print("🔐 PRUEBA 3: Verificación de Código")
    print("="*60)
    
    with app.test_client() as client:
        response = client.post('/verify_sms_code',
                               data={
                                   'phone_number': phone_number,
                                   'verification_code': code
                               })
        data = response.get_json()
        
        if data.get('success'):
            print(f"\n✅ {data['message']}")
            return True
        else:
            print(f"\n❌ Error: {data.get('message')}")
            return False

if __name__ == '__main__':
    print("\n" + "🧪 SUITE DE PRUEBAS SMS".center(60, "="))
    print("La Esquinita - Verificación Twilio\n")
    
    with app.app_context():
       
        test_sms_diagnostic()
        
        
        print("\n" + "-"*60)
        phone = input("\n📱 Ingresa tu número de celular (ej: 5512345678): ").strip()
        
        if not phone:
            print("\n⚠️ No se proporcionó número. Saltando prueba de envío.")
        else:
            if test_sms_send(phone):
                
                print("\n" + "-"*60)
                code = input("\n🔐 Ingresa el código que recibiste: ").strip()
                
                if code:
                    test_sms_verify(phone, code)
                else:
                    print("\n⚠️ No se proporcionó código. Saltando verificación.")
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60 + "\n")
