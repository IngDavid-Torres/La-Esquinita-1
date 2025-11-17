# Guía para configurar Twilio SMS - La Esquinita

## 1. Crear cuenta en Twilio
1. Ve a https://www.twilio.com/
2. Crea una cuenta gratuita
3. Verifica tu número de teléfono
4. Ve al Console Dashboard

## 2. Obtener credenciales
En tu Twilio Console encontrarás:
- Account SID (empieza con "AC...")
- Auth Token (cadena de caracteres alfanuméricos)
- Phone Number (tu número Twilio, formato +1234567890)

## 3. Configurar .env
Edita tu archivo .env y reemplaza:

TWILIO_ACCOUNT_SID=tu_account_sid_real_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_real_aqui  
TWILIO_PHONE_NUMBER=+1234567890

## 4. Nota importante
- Con cuenta gratuita solo puedes enviar SMS a números verificados
- Para números mexicanos, usa formato: +521234567890
- Para producción necesitarás upgrade a cuenta pagada

## 5. URLs de prueba
Después de configurar:
- Registro SMS: http://localhost:5000/registro_sms
- Login SMS: http://localhost:5000/login_sms