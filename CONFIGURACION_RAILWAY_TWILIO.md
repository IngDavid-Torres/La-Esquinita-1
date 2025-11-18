# 🚂 Configuración de Twilio en Railway - Paso a Paso

## 📋 Información Importante

La aplicación **La Esquinita** ya está desplegada en Railway y el código SMS está funcionando localmente. Ahora necesitas configurar Twilio para que funcione en producción.

---

## 🔑 Paso 1: Configurar Variables de Entorno en Railway

### 1.1 Acceder a tu Proyecto en Railway

1. Ve a [https://railway.app](https://railway.app)
2. Inicia sesión
3. Selecciona tu proyecto **La Esquinita**

### 1.2 Agregar Variables de Entorno

1. Haz clic en tu servicio/aplicación
2. Ve a la pestaña **Variables**
3. Agrega las siguientes variables (haz clic en **+ New Variable** para cada una):

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
```

**Opcional pero RECOMENDADO** (para mejor entregabilidad):
```env
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxx
```
*(Deja esto vacío por ahora si no lo tienes, lo configuraremos después)*

### 1.3 Verificar el Despliegue

Después de agregar las variables, Railway redesplegará automáticamente tu aplicación.

---

## 🌐 Paso 2: Obtener tu URL de Railway

### 2.1 Encontrar tu Dominio

1. En tu proyecto de Railway, ve a **Settings** → **Domains**
2. Encontrarás algo como:
   - `tu-app.up.railway.app` (dominio autogenerado)
   - O tu dominio personalizado si lo configuraste

### 2.2 Anotar la URL Completa

Tu URL base será algo como:
```
https://laesquinita-production.up.railway.app
```

**⚠️ IMPORTANTE**: Debe ser **HTTPS** (Railway lo proporciona automáticamente)

---

## 🔗 Paso 3: Configurar Webhook en Twilio

Ahora que tienes tu URL de Railway, debes configurar Twilio para que envíe notificaciones de estado.

### Opción A: Si NO usas Messaging Service (configuración actual)

1. Ve a [Twilio Console - Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/active)
2. Haz clic en tu número: **+13139921329**
3. Desplázate hasta **Messaging Configuration**
4. En **A MESSAGE COMES IN**:
   - **Webhook**: `https://tu-dominio-railway.up.railway.app/twilio_status`
   - **HTTP Method**: `POST`
5. Haz clic en **Save**

### Opción B: Usando Messaging Service (RECOMENDADO)

#### 3.1 Crear Messaging Service en Twilio

1. Ve a [Twilio Console - Messaging Services](https://console.twilio.com/us1/develop/sms/services)
2. Haz clic en **Create Messaging Service**
3. **Nombre**: `La Esquinita Verificacion`
4. **Use case**: Selecciona `Verify users`
5. Haz clic en **Create Messaging Service**

#### 3.2 Agregar tu Número al Servicio

1. En la página del servicio, ve a **Sender Pool**
2. Haz clic en **Add Senders**
3. Selecciona tu número: **+13139921329**
4. Haz clic en **Add Phone Numbers**

#### 3.3 Configurar Integration (Webhooks)

1. En tu Messaging Service, ve a **Integration** (menú lateral)
2. **Incoming Messages**:
   - Selecciona: **Send a webhook**
   - **Request URL**: `https://tu-dominio-railway.up.railway.app/twilio_status`
   - **HTTP Method**: `POST`
3. Haz clic en **Save**

#### 3.4 Copiar el Messaging Service SID

1. En la parte superior verás el **Messaging Service SID**
2. Empieza con `MG...`
3. Cópialo

#### 3.5 Agregar SID a Railway

1. Regresa a Railway → Tu proyecto → **Variables**
2. Agrega/edita la variable:
   ```
   TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Guarda y espera el redespliegue

---

## ✅ Paso 4: Verificar que Todo Funciona

### 4.1 Probar el Diagnóstico

Abre en tu navegador:
```
https://tu-dominio-railway.up.railway.app/sms_diagnostico
```

Deberías ver algo como:
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

### 4.2 Probar Envío de SMS

Puedes probar directamente desde tu aplicación:
1. Ve a: `https://tu-dominio-railway.up.railway.app/registro_sms`
2. Llena el formulario con tu número real
3. Haz clic en "Enviar código"
4. Revisa tu celular

### 4.3 Monitorear en Twilio

1. Ve a [Twilio Console - Logs](https://console.twilio.com/us1/monitor/logs/messaging)
2. Verás todos los mensajes enviados con su estado:
   - ✅ `delivered` = Entregado
   - ⏳ `sent` = Enviado al operador
   - ❌ `failed` = Falló (revisa el error)

---

## 🔧 Paso 5: Configuraciones Adicionales en Twilio (Opcional)

### 5.1 Configurar Callback de Estado de Entrega (Delivery Status)

Si usas Messaging Service:
1. Ve a tu Messaging Service en Twilio
2. **Integration** → **Delivery Status Callback**
3. **URL**: `https://tu-dominio-railway.up.railway.app/twilio_status`
4. **HTTP Method**: `POST`

### 5.2 Configurar Periodo de Validez

En el Messaging Service:
1. **Integration** → **Advanced Settings**
2. **Validity Period**: `36000` segundos (10 horas)

---

## 📊 Endpoints Disponibles en Producción

| Endpoint | URL Completa | Descripción |
|----------|--------------|-------------|
| Diagnóstico | `https://tu-app.railway.app/sms_diagnostico` | Ver estado de configuración |
| Enviar SMS | `https://tu-app.railway.app/send_sms_verification` | Enviar código (POST) |
| Verificar | `https://tu-app.railway.app/verify_sms_code` | Verificar código (POST) |
| Registro | `https://tu-app.railway.app/registro_sms` | Registro con SMS |
| Login | `https://tu-app.railway.app/login_sms` | Login con 2FA |
| Webhook | `https://tu-app.railway.app/twilio_status` | Recibir estados de Twilio |

---

## 🆘 Solución de Problemas

### Problema: "development_mode": true

**Causa**: Las variables de entorno no están configuradas en Railway

**Solución**:
1. Verifica que agregaste las 3 variables obligatorias en Railway
2. Redesplega la aplicación
3. Espera 2-3 minutos y vuelve a verificar

### Problema: SMS no llegan

**Causa**: Webhook no configurado o número no válido

**Solución**:
1. Verifica la URL del webhook en Twilio (debe ser HTTPS)
2. Revisa los logs en Twilio Console
3. Asegúrate que el número tenga formato: +52XXXXXXXXXX

### Problema: Error 21609 (Invalid URL)

**Causa**: La URL del webhook es localhost o no es HTTPS

**Solución**:
1. Usa la URL de Railway (HTTPS)
2. Verifica que no tenga `localhost` o `127.0.0.1`

### Problema: Error 21211 (Invalid phone number)

**Causa**: Formato de número incorrecto

**Solución**:
- Usa formato internacional: `+525512345678` (México)
- 10 dígitos después del +52

---

## 📝 Checklist Final de Producción

Antes de considerar completada la configuración:

- [ ] Variables de Twilio agregadas en Railway
- [ ] Railway redesplegó la aplicación
- [ ] `/sms_diagnostico` muestra `development_mode: false`
- [ ] Webhook configurado en Twilio con URL de Railway
- [ ] Probaste enviar SMS a tu celular desde producción
- [ ] El mensaje llegó correctamente
- [ ] El código fue verificado exitosamente
- [ ] Revisaste logs en Twilio Console
- [ ] (Opcional) Messaging Service creado y configurado
- [ ] (Opcional) Messaging Service SID agregado a Railway

---

## 🎯 Resumen Rápido

### URLs que necesitas configurar en Twilio:

**Webhook de Status/Incoming Messages:**
```
https://TU-DOMINIO.up.railway.app/twilio_status
```

### Variables que necesitas en Railway:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxx (opcional)
```

---

## 📞 Enlaces Útiles

- **Railway Dashboard**: https://railway.app/dashboard
- **Twilio Console**: https://console.twilio.com/
- **Twilio Phone Numbers**: https://console.twilio.com/us1/develop/phone-numbers/manage/active
- **Twilio Messaging Services**: https://console.twilio.com/us1/develop/sms/services
- **Twilio Logs**: https://console.twilio.com/us1/monitor/logs/messaging
- **Twilio Debugger**: https://console.twilio.com/us1/monitor/logs/debugger

---

## 🚀 ¡Siguiente Paso!

1. **Obtén tu URL de Railway** (Settings → Domains)
2. **Configura el webhook en Twilio** con esa URL + `/twilio_status`
3. **Prueba enviando un SMS** desde producción
4. **Monitorea en Twilio Console** para ver el estado

✨ **¡Tu sistema de verificación SMS estará completamente funcional en producción!**
