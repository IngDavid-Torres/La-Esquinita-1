# 🚀 Guía de Configuración de Mercado Pago en Producción

Esta guía te ayudará a configurar Mercado Pago en modo producción para procesar pagos reales en **La Esquinita**.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Obtener Credenciales de Producción](#obtener-credenciales-de-producción)
3. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
4. [Verificar la Configuración](#verificar-la-configuración)
5. [Webhook y Notificaciones](#webhook-y-notificaciones)
6. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
7. [Pruebas y Resolución de Problemas](#pruebas-y-resolución-de-problemas)

---

## ✅ Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta de Mercado Pago verificada
- ✅ Documentación legal de tu negocio (RFC, CURP, etc.)
- ✅ Cuenta bancaria vinculada a Mercado Pago
- ✅ Acceso al panel de desarrolladores de Mercado Pago

---

## 🔑 Obtener Credenciales de Producción

### Paso 1: Acceder al Panel de Desarrolladores

1. Ve a [https://www.mercadopago.com.mx/developers](https://www.mercadopago.com.mx/developers)
2. Inicia sesión con tu cuenta de Mercado Pago
3. Si no tienes una aplicación, crea una nueva:
   - Haz clic en **"Crear aplicación"**
   - Nombre: `La Esquinita - Pagos en Línea`
   - Descripción: `Aplicación para procesar pagos en el e-commerce de La Esquinita`

### Paso 2: Activar Modo Producción

**IMPORTANTE:** Para obtener credenciales de producción, tu cuenta debe estar **certificada**.

1. En el panel de tu aplicación, ve a la sección **"Credenciales"**
2. Verás dos opciones:
   - 🧪 **Credenciales de prueba (TEST)**: Para desarrollo
   - ✅ **Credenciales de producción**: Para ambiente real

3. **Proceso de Certificación:**
   - Mercado Pago requiere que completes un proceso de verificación
   - Deberás proporcionar:
     - Información del negocio
     - Documentación fiscal (RFC)
     - Datos bancarios
     - Descripción de tu modelo de negocio
   - El proceso puede tomar 24-48 horas

### Paso 3: Copiar las Credenciales

Una vez certificado, copia las siguientes credenciales:

```
Access Token: APP_USR-1234567890-123456-abcdefghijklmnopqrstuvwxyz123456-123456789
Public Key:   APP_USR-abcdefgh-1234-5678-90ab-cdefghijklmn-123456789
```

**⚠️ IMPORTANTE:** 
- Estas credenciales son **SECRETAS**
- **NUNCA** las compartas públicamente
- **NUNCA** las subas a repositorios de Git
- Guárdalas en un lugar seguro (gestor de contraseñas)

---

## 🔧 Configurar Variables de Entorno

### Opción 1: Configuración Local (Desarrollo)

1. **Copia el archivo de ejemplo:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edita el archivo `.env`:**
   ```bash
   # Abre con VS Code
   code .env
   ```

3. **Reemplaza las credenciales de TEST con las de PRODUCCIÓN:**
   ```env
   # Mercado Pago - PRODUCCIÓN
   MP_ACCESS_TOKEN=APP_USR-TU_ACCESS_TOKEN_AQUI
   MP_PUBLIC_KEY=APP_USR-TU_PUBLIC_KEY_AQUI
   ```

4. **Guarda el archivo** (Ctrl+S)

### Opción 2: Configuración en Railway (Producción)

Si estás desplegando en Railway:

1. Ve a tu proyecto en [railway.app](https://railway.app)
2. Selecciona tu servicio
3. Ve a la pestaña **"Variables"**
4. Agrega las siguientes variables:

   ```
   MP_ACCESS_TOKEN = APP_USR-tu_access_token_aqui
   MP_PUBLIC_KEY = APP_USR-tu_public_key_aqui
   ```

5. **Guarda y redeploya** la aplicación

### Opción 3: Configuración en Render

1. Ve a tu proyecto en [render.com](https://render.com)
2. Selecciona tu web service
3. Ve a **"Environment"**
4. Agrega las variables de entorno:

   ```
   MP_ACCESS_TOKEN = APP_USR-tu_access_token_aqui
   MP_PUBLIC_KEY = APP_USR-tu_public_key_aqui
   ```

5. **Guarda** - Render redeployará automáticamente

---

## ✅ Verificar la Configuración

### 1. Verificar Variables de Entorno

```powershell
# En PowerShell, dentro del proyecto:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('MP_ACCESS_TOKEN:', os.getenv('MP_ACCESS_TOKEN')[:20] if os.getenv('MP_ACCESS_TOKEN') else 'NO CONFIGURADO')"
```

### 2. Iniciar la Aplicación

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar aplicación
python app.py
```

### 3. Verificar el Modo en la Consola

Al iniciar, deberías ver:

```
✅ Mercado Pago configurado en MODO PRODUCCIÓN
🔑 Access Token: APP_USR-1234567890...
```

Si ves:
```
🧪 Mercado Pago configurado en MODO TEST
```
Significa que aún estás usando credenciales de prueba.

### 4. Probar el Flujo de Pago

1. Navega a: `http://localhost:5000`
2. Agrega productos al carrito
3. Ve al carrito
4. Haz clic en **"Pagar con MercadoPago"**
5. Completa el formulario
6. **Deberías ser redirigido al checkout real de Mercado Pago**

---

## 🔔 Webhook y Notificaciones

Los webhooks permiten que Mercado Pago notifique automáticamente a tu aplicación sobre cambios en el estado de los pagos.

### Configurar URL del Webhook

1. Ve al panel de tu aplicación en Mercado Pago
2. Sección **"Webhooks"**
3. Agrega la URL de notificación:

   ```
   https://tu-dominio.com/webhook/mercadopago
   ```

4. **Eventos a suscribirse:**
   - ✅ Pagos aprobados
   - ✅ Pagos rechazados
   - ✅ Pagos pendientes
   - ✅ Contracargos (chargebacks)
   - ✅ Reembolsos

### URL según tu plataforma:

**Railway:**
```
https://laesquinita-production.up.railway.app/webhook/mercadopago
```

**Render:**
```
https://laesquinita.onrender.com/webhook/mercadopago
```

**Dominio Propio:**
```
https://laesquinita.com.mx/webhook/mercadopago
```

### Verificar Webhooks en Logs

Los webhooks se registran automáticamente en los logs de la aplicación:

```
🔔 WEBHOOK RECIBIDO DE MERCADOPAGO
📦 Data recibida: {...}
💳 Procesando payment_id: 123456789
📊 Status del pago: approved
✅ Pedido 45 actualizado a: Confirmado
```

---

## 🔒 Consideraciones de Seguridad

### 1. Protege tus Credenciales

- ✅ **SÍ:** Usar variables de entorno (`.env`)
- ✅ **SÍ:** Usar gestores de secretos (Railway Variables, Render Environment)
- ❌ **NO:** Hardcodear credenciales en el código
- ❌ **NO:** Subir el archivo `.env` a Git

### 2. Configura `.gitignore`

Verifica que tu `.gitignore` incluya:

```gitignore
.env
.env.local
.env.production
*.env
```

### 3. Usa HTTPS en Producción

- ✅ Todos los endpoints deben usar HTTPS
- ✅ Railway y Render proporcionan HTTPS automáticamente
- ✅ Si usas dominio propio, configura certificado SSL (Let's Encrypt)

### 4. Valida Webhooks (Opcional pero Recomendado)

Para mayor seguridad, valida las firmas de los webhooks. La función `validate_webhook_signature` en `mercadopago_config.py` está preparada para esto.

---

## 🧪 Pruebas y Resolución de Problemas

### Escenario 1: Sigo viendo "MODO TEST"

**Problema:** La aplicación muestra que está en modo test.

**Solución:**
1. Verifica que las credenciales en `.env` comiencen con `APP_USR-` (no `TEST-`)
2. Reinicia la aplicación completamente
3. Verifica que el archivo `.env` esté en la raíz del proyecto
4. Ejecuta: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('MP_ACCESS_TOKEN'))"`

### Escenario 2: Error al crear preferencia de pago

**Problema:** Aparece error al intentar procesar el pago.

**Solución:**
1. Verifica que tu cuenta esté certificada
2. Revisa que las credenciales sean de producción
3. Verifica que tu cuenta tenga una cuenta bancaria vinculada
4. Revisa los logs para más detalles

### Escenario 3: Los webhooks no llegan

**Problema:** No recibes notificaciones de pago.

**Solución:**
1. Verifica que la URL del webhook sea pública (no `localhost`)
2. Asegúrate de que el endpoint `/webhook/mercadopago` esté accesible
3. Revisa la configuración de webhooks en el panel de Mercado Pago
4. Verifica los logs de tu aplicación

### Escenario 4: El pago se procesa pero no se registra en la BD

**Problema:** El cliente paga pero el pedido no aparece en el sistema.

**Solución:**
1. Verifica los webhooks
2. Revisa los logs de la aplicación
3. Verifica la tabla `pedido` en la base de datos
4. Asegúrate de que el campo `payment_id` se esté guardando correctamente

---

## 📊 Monitoreo y Análisis

### Panel de Mercado Pago

Accede al panel para ver:
- 💰 **Ventas realizadas**
- 📈 **Gráficos de ingresos**
- 🔄 **Estado de los pagos**
- 💳 **Métodos de pago utilizados**
- 📉 **Tasas de conversión**

URL: [https://www.mercadopago.com.mx/balance](https://www.mercadopago.com.mx/balance)

### Logs de la Aplicación

En Railway o Render, revisa los logs en tiempo real:

```powershell
# Railway CLI
railway logs

# Render
# Accede a la sección "Logs" en el dashboard
```

---

## 💰 Comisiones de Mercado Pago

Al procesar pagos reales, Mercado Pago cobra comisiones:

### Tarifas Estándar (México):

- **Tarjeta de crédito/débito:** 3.6% + $3 MXN por transacción
- **Transferencia bancaria:** 0.9% por transacción
- **Depósito en efectivo:** 2.9% + $10 MXN por transacción

### Retiro de Fondos:

- **A cuenta bancaria:** Gratuito (1-2 días hábiles)
- **Retiro instantáneo:** 2.5% (mínimo $5 MXN)

**Nota:** Las tarifas pueden variar. Consulta: [https://www.mercadopago.com.mx/costs](https://www.mercadopago.com.mx/costs)

---

## 📞 Soporte

### Mercado Pago

- **Panel de Ayuda:** [https://www.mercadopago.com.mx/ayuda](https://www.mercadopago.com.mx/ayuda)
- **Desarrolladores:** [https://www.mercadopago.com.mx/developers/es/support](https://www.mercadopago.com.mx/developers/es/support)
- **Teléfono:** 01 800 633 7275

### Documentación Técnica

- **API Reference:** [https://www.mercadopago.com.mx/developers/es/reference](https://www.mercadopago.com.mx/developers/es/reference)
- **SDK Python:** [https://github.com/mercadopago/sdk-python](https://github.com/mercadopago/sdk-python)

---

## 🎉 ¡Listo!

Ahora tu aplicación está configurada para procesar pagos reales con Mercado Pago.

### Checklist Final:

- ✅ Credenciales de producción configuradas
- ✅ Variables de entorno en el servidor
- ✅ Webhooks configurados
- ✅ HTTPS habilitado
- ✅ Cuenta bancaria vinculada
- ✅ Prueba de pago realizada exitosamente

---

## 📝 Notas Adicionales

### Diferencias entre TEST y PRODUCCIÓN:

| Característica | TEST | PRODUCCIÓN |
|---------------|------|------------|
| Procesa pagos reales | ❌ No | ✅ Sí |
| Requiere certificación | ❌ No | ✅ Sí |
| Cobra comisiones | ❌ No | ✅ Sí |
| Notificaciones reales | ❌ No | ✅ Sí |
| Retiros a banco | ❌ No | ✅ Sí |

### Migración de TEST a PRODUCCIÓN:

1. **No necesitas cambiar código** - Solo las credenciales
2. **Los pedidos de TEST no se migran** - Son simulados
3. **Haz pruebas con montos pequeños** al principio
4. **Monitorea los primeros pagos** de cerca

---

**¿Dudas o problemas?** Revisa los logs y la documentación oficial de Mercado Pago.

**Última actualización:** Noviembre 2025
