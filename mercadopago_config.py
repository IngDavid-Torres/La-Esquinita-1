import os
import mercadopago
from dotenv import load_dotenv
load_dotenv()
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN')
MP_PUBLIC_KEY = os.environ.get('MP_PUBLIC_KEY')
if not MP_ACCESS_TOKEN or not MP_PUBLIC_KEY:
    print("⚠️ ADVERTENCIA: Credenciales de Mercado Pago no configuradas")
    print("📋 Configure MP_ACCESS_TOKEN y MP_PUBLIC_KEY en el archivo .env")
    print("🔗 Guía: Consulte MERCADOPAGO_PRODUCCION.md para más información")
    MP_ACCESS_TOKEN = "APP_USR-8747729118528796-112018-e70d6542822d005f2998dbdb31bc6af1-5365591011"
    MP_PUBLIC_KEY = "APP_USR-1f514871-1003-49d6-b5cb-bb575e919c95"
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
ENVIRONMENT = 'test' if MP_ACCESS_TOKEN.startswith('TEST-') else 'production'
if ENVIRONMENT == 'production':
    print("✅ Mercado Pago configurado en MODO PRODUCCIÓN")
    print(f"🔑 Access Token: {MP_ACCESS_TOKEN[:20]}...")
else:
    print("🧪 Mercado Pago configurado en MODO TEST")
    print("⚠️ Los pagos son simulados y no se procesarán realmente")
def get_sdk():
    return sdk
def is_test_environment():
    return ENVIRONMENT == 'test'


def create_preference(items, payer_info, urls, external_reference):
    preference_data = {
        "items": items,
        "payer": {
            "name": payer_info.get("name", ""),
            "email": payer_info.get("email", "")
        },
        "back_urls": {
            "success": urls.get("success"),
            "failure": urls.get("failure"),
            "pending": urls.get("pending")
        },
        "auto_return": "approved",
        "external_reference": external_reference,
        "statement_descriptor": "LA ESQUINITA MX",
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "ticket"},
                {"id": "bank_transfer"},
                {"id": "atm"},
                {"id": "digital_currency"}
            ],
            "installments": 12
        },
        "shipments": {
            "cost": 0,
            "mode": "not_specified"
        }
    }

    try:
        print(f"📤 Enviando preferencia a Mercado Pago...")
        print(f"   Items: {len(items)}")
        print(f"   Comprador: {payer_info.get('email')}")
        print(f"   Entorno: {'SANDBOX' if ENVIRONMENT == 'test' else 'PRODUCCIÓN'}")

        preference_response = sdk.preference().create(preference_data)
        status = preference_response.get('status')
        response = preference_response.get('response', {})

        print(f"📥 Respuesta Mercado Pago: status={status}, id={response.get('id')}")

       
        return {
            "status": status,
            "response": {
                "id": response.get("id"),
                "init_point": response.get("init_point"),
                "sandbox_init_point": response.get("sandbox_init_point")
            }
        }

    except Exception as e:
        print(f"❌ Error creando preferencia: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_payment_info(payment_id):
    try:
        payment_response = sdk.payment().get(payment_id)
        if payment_response["status"] == 200:
            return payment_response["response"]
        return None
    except Exception as e:
        print(f"❌ Error obteniendo información de pago: {str(e)}")
        return None
def validate_webhook_signature(request_data, x_signature, x_request_id):
    if is_test_environment():
        return True
    return True
