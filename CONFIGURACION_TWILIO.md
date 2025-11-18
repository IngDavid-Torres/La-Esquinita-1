# 📱 Configuración de Twilio para Verificación SMS

## 🎯 Resumen
Este documento te guía paso a paso para configurar Twilio y enviar códigos de verificación por SMS a celulares reales.

---

## 📋 Paso 1: Crear/Configurar tu Cuenta de Twilio

### 1.1 Registro en Twilio
1. Ve a [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Crea una cuenta gratuita (incluye $15 USD de crédito de prueba)
3. Verifica tu email y número de teléfono personal

### 1.2 Obtener Credenciales
Una vez dentro del Dashboard de Twilio:

1. **Account SID** y **Auth Token**:
   - Ve al [Console Dashboard](https://console.twilio.com/)
   - Copia tu `Account SID`
   - Copia tu `Auth Token` (haz clic en "Show" para verlo)

2. **Número de Teléfono**:
   - En el menú lateral: **Phone Numbers** → **Manage** → **Buy a number**
   - Filtra por país (Mexico: +52)
   - Selecciona un número con capacidades **SMS**
   - Confirma la compra (se descontará de tu crédito)

---

## 🔧 Paso 2: Configurar Servicio de Mensajería (RECOMENDADO)

### ¿Por qué usar un Messaging Service?
- ✅ Mejor entregabilidad de mensajes
- ✅ Fallback automático si un número falla
- ✅ Gestión centralizada de múltiples números
- ✅ Configuración de webhooks simplificada

### 2.1 Crear Messaging Service
1. En Twilio Console: **Messaging** → **Services**
2. Haz clic en **Create Messaging Service**
3. **Nombre amigable**: `La Esquinita Verificacion`
4. **Use case**: Select `Verify users`
5. Haz clic en **Create Messaging Service**

### 2.2 Agregar tu Número al Servicio
1. En la página del servicio, ve a **Sender Pool**
2. Haz clic en **Add Senders**
3. Selecciona tu número de Twilio
4. Haz clic en **Add Phone Numbers**

### 2.3 Copiar el Messaging Service SID
1. En la parte superior del servicio verás el **Messaging Service SID**
2. Empieza con `MG...`
3. Cópialo para el siguiente paso

---

## ⚙️ Paso 3: Configurar Variables de Entorno

Abre tu archivo `.env` en La Esquinita y actualiza estas líneas:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Valores a reemplazar:
- `TWILIO_ACCOUNT_SID`: Tu Account SID del Dashboard
- `TWILIO_AUTH_TOKEN`: Tu Auth Token del Dashboard
- `TWILIO_PHONE_NUMBER`: El número que compraste (formato: +1234567890)
- `TWILIO_MESSAGING_SERVICE_SID`: El SID del Messaging Service que creaste

**⚠️ IMPORTANTE**: Si usas `TWILIO_MESSAGING_SERVICE_SID`, la aplicación lo usará automáticamente en lugar del número directo.

---

## 🔗 Paso 4: Configurar Webhooks en Twilio

### 4.1 Obtener la URL de tu Aplicación
Necesitas la URL pública de tu aplicación. Opciones:

**Opción A: Despliegue en Producción**
- Si ya tienes tu app desplegada (ej: Heroku, AWS, Render): `https://tudominio.com`

**Opción B: Desarrollo Local con ngrok**
```bash
# Instalar ngrok: https://ngrok.com/download
ngrok http 5000
# Copia la URL HTTPS que aparece (ej: https://abc123.ngrok.io)
```

### 4.2 Configurar en el Messaging Service

1. Ve a tu Messaging Service en Twilio Console
2. Navega a **Integration** (en el menú lateral)
3. **Incoming Messages** (Mensajes entrantes):
   - Selecciona: **Send a webhook**
   - **Request URL**: `https://tudominio.com/twilio_status`
   - **HTTP Method**: `POST`

4. **Delivery Status Callback** (Estado de entrega):
   - Ya está configurado automáticamente en el código
   - La URL se envía dinámicamente con cada mensaje

### 4.3 Configuración del Número (Alternativa)

Si NO usas Messaging Service, configura el webhook en el número:

1. **Phone Numbers** → **Manage** → **Active numbers**
2. Selecciona tu número
3. **Messaging Configuration**:
   - **A MESSAGE COMES IN**: Webhook `https://tudominio.com/twilio_status` (POST)

---

## 🧪 Paso 5: Probar la Integración

### 5.1 Iniciar la Aplicación
```bash
cd "c:\Users\doser\OneDrive\Escritorio\La Esquinita"
python app.py
```

### 5.2 Verificar Configuración
Abre en tu navegador:
```
http://localhost:5000/sms_diagnostico
```

Deberías ver:
```json
{
  "success": true,
  "diagnostico": {
    "twilio_account_sid_present": true,
    "twilio_auth_token_present": true,
    "twilio_phone_number_present": true,
    "twilio_messaging_service_sid_present": true,
    "using_messaging_service": true,
    "development_mode": false,
    "example_generated_code": "123456"
  }
}
```

### 5.3 Probar Envío de SMS

**Opción A: Desde el Frontend**
1. Ve a: `http://localhost:5000/registro_sms`
2. Llena el formulario con tu número real
3. Haz clic en "Enviar código"
4. Revisa tu celular

**Opción B: Usando curl/Postman**
```bash
curl -X POST http://localhost:5000/send_sms_verification \
  -d "phone_number=+5215512345678"
```

---

## 📊 Paso 6: Monitorear Mensajes en Twilio

### Dashboard de Mensajes
1. Ve a **Monitor** → **Logs** → **Messaging**
2. Verás todos los mensajes enviados con su estado:
   - ✅ `delivered`: Entregado correctamente
   - ⏳ `queued`: En cola
   - ⏳ `sent`: Enviado al operador
   - ❌ `failed`: Falló (revisa el error)
   - ❌ `undelivered`: No entregado

### Depuración de Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `21211` | Número inválido | Verifica formato: +52XXXXXXXXXX |
| `21608` | Número no puede recibir SMS | Usa un número móvil válido |
| `21610` | Número bloqueado | Elimina el bloqueo en Twilio Console |
| `30007` | Operador filtró el mensaje | Acorta el mensaje, evita spam |

---

## 🔒 Paso 7: Seguridad y Mejores Prácticas

### Variables de Entorno
- ✅ **NUNCA** subas el archivo `.env` a Git
- ✅ Agrega `.env` a tu `.gitignore`
- ✅ Usa variables de entorno en producción

### Límites y Quotas
- **Cuenta de Prueba**: Solo puedes enviar a números verificados en Twilio
- **Cuenta de Producción**: Sin límites, pero revisa pricing
- **Rate Limits**: Twilio tiene límites por segundo, configura colas

### Costos Aproximados
- SMS en México: ~$0.0075 USD por mensaje
- SMS en USA: ~$0.0079 USD por mensaje
- Número de teléfono: ~$1.15 USD/mes

---

## 🚀 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/sms_diagnostico` | GET | Diagnóstico de configuración |
| `/send_sms_verification` | POST | Enviar código de verificación |
| `/verify_sms_code` | POST | Verificar código ingresado |
| `/registro_sms` | GET/POST | Registro con verificación SMS |
| `/login_sms` | GET/POST | Login con 2FA por SMS |
| `/twilio_status` | POST | Webhook de estado de Twilio |
| `/sms_last_code` | GET | Debug: Ver último código (solo dev) |

---

## 📝 Parámetros de la Configuración en Twilio Console

### Mensajes Entrantes (Integration → Incoming Messages)
- **Opción seleccionada**: ✅ **Send a webhook**
- **Request URL**: `https://tudominio.com/twilio_status`
- **HTTP Method**: POST

### Callback de Estado de Entrega
- Se configura automáticamente en el código
- URL: `https://tudominio.com/twilio_status`
- Método: POST

### Periodo de Validez
- **Queue Timeout**: 36000 segundos (10 horas)
- Los códigos en la app expiran en **10 minutos**

---

## ✅ Checklist Final

Antes de ir a producción, verifica:

- [ ] Credenciales de Twilio configuradas en `.env`
- [ ] Messaging Service creado y configurado
- [ ] Número de teléfono agregado al Messaging Service
- [ ] Webhook configurado: `https://tudominio.com/twilio_status`
- [ ] `/sms_diagnostico` muestra todo en verde
- [ ] Prueba enviando SMS a tu celular
- [ ] Verifica que el código llegue y sea válido
- [ ] Monitorea logs en Twilio Console
- [ ] `.env` en `.gitignore`
- [ ] Actualiza a cuenta de producción si es necesario

---

## 🆘 Soporte

Si tienes problemas:

1. **Revisa logs de Python**: Busca mensajes de error en la consola
2. **Twilio Debugger**: [https://console.twilio.com/us1/monitor/logs/debugger](https://console.twilio.com/us1/monitor/logs/debugger)
3. **Documentación Twilio**: [https://www.twilio.com/docs/sms](https://www.twilio.com/docs/sms)

---

## 📞 URLs Útiles

- **Twilio Console**: https://console.twilio.com/
- **Messaging Services**: https://console.twilio.com/us1/develop/sms/services
- **Buy Phone Number**: https://console.twilio.com/us1/develop/phone-numbers/manage/search
- **Logs & Debugger**: https://console.twilio.com/us1/monitor/logs/debugger
- **Billing**: https://console.twilio.com/us1/billing

---

✨ **¡Listo!** Ahora tu aplicación puede enviar códigos de verificación por SMS a celulares reales.
