
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
    # Valores por defecto solo para desarrollo local
    MP_ACCESS_TOKEN = "TEST-7916427332588639-102718-00ee5129ad06c2ceba14e4e44b94d22e-191563398"
    MP_PUBLIC_KEY = "TEST-c1e625f3-6498-4c5e-9fda-d2b6b5a0a7de-191563398"


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
    """
    Crea una preferencia de pago en Mercado Pago
    
    Args:
        items: Lista de productos [{title, quantity, unit_price, currency_id}]
        payer_info: Información del pagador {name, email}
        urls: URLs de retorno {success, failure, pending}
        external_reference: Referencia externa del pedido
    
    Returns:
        dict: Respuesta de Mercado Pago con la preferencia creada
    """
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
            "excluded_payment_methods": [],
            "excluded_payment_types": [],
            "installments": 12
        },
        "shipments": {
            "cost": 0,
            "mode": "not_specified"
        }
    }
    
    try:
        print(f"📤 Enviando preferencia a MercadoPago:")
        print(f"   Items: {len(items)}")
        print(f"   Payer: {payer_info.get('email')}")
        print(f"   Back URLs: success={preference_data['back_urls']['success'][:50]}...")
        
        preference_response = sdk.preference().create(preference_data)
        
        print(f"📥 Respuesta de MercadoPago: status={preference_response.get('status')}")
        
        return preference_response
    except Exception as e:
        print(f"❌ Error creando preferencia: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def get_payment_info(payment_id):
    """
    Obtiene información de un pago específico
    
    Args:
        payment_id: ID del pago en Mercado Pago
    
    Returns:
        dict: Información del pago
    """
    try:
        payment_response = sdk.payment().get(payment_id)
        if payment_response["status"] == 200:
            return payment_response["response"]
        return None
    except Exception as e:
        print(f"❌ Error obteniendo información de pago: {str(e)}")
        return None

def validate_webhook_signature(request_data, x_signature, x_request_id):
    """
    Valida la firma de un webhook de Mercado Pago
    (Implementación básica - mejorar en producción)
    
    Args:
        request_data: Datos del request
        x_signature: Firma del header X-Signature
        x_request_id: ID del header X-Request-Id
    
    Returns:
        bool: True si la firma es válida
    """
    
    if is_test_environment():
        return True
    
    # TODO: Implementar validación real de firma para producción
    return True
