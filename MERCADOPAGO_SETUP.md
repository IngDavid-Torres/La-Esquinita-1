# 📋 Guía de Integración de MercadoPago - AgroConnect

## 🚀 Instalación del SDK

### 1. Instalar el SDK de MercadoPago
```bash
pip install mercadopago
```

### 2. Obtener credenciales de MercadoPago

1. **Crear cuenta en MercadoPago**:
   - Ve a [https://mercadopago.com.mx](https://mercadopago.com.mx)
   - Regístrate o inicia sesión

2. **Acceder al panel de desarrolladores**:
   - Ve a [https://www.mercadopago.com.mx/developers](https://www.mercadopago.com.mx/developers)
   - Crear nueva aplicación

3. **Obtener tokens**:
   - **Token de prueba**: Para desarrollo y testing
   - **Token de producción**: Para ambiente real

### 3. Configurar credenciales en la aplicación

En `app.py`, reemplaza:
```python
MP_ACCESS_TOKEN = "TEST-TU_ACCESS_TOKEN_AQUI"
```

**Para pruebas** (recomendado al inicio):
```python
MP_ACCESS_TOKEN = "TEST-1234567890-123456-abcdefghijklmnopqrstuvwxyz123456-123456789"
```

**Para producción**:
```python
MP_ACCESS_TOKEN = "APP_USR-1234567890-123456-abcdefghijklmnopqrstuvwxyz123456-123456789"
```

## 🔧 Configuración de Email

### Configurar Gmail para envío de confirmaciones

1. **Habilitar verificación en 2 pasos** en tu cuenta de Gmail
2. **Generar contraseña de aplicación**:
   - Ve a configuración de Google → Seguridad
   - Contraseñas de aplicaciones
   - Genera una nueva para "AgroConnect"

3. **Actualizar configuración en app.py**:
```python
app.config['MAIL_USERNAME'] = 'tu_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'abcd efgh ijkl mnop'  # Contraseña de aplicación
```

## 🎯 URLs de Callback

### Configuración en MercadoPago

Al crear tu aplicación en MercadoPago, configura estas URLs:

**Para desarrollo local**:
- Success: `http://localhost:5000/pago_exitoso`
- Failure: `http://localhost:5000/pago_fallido`
- Pending: `http://localhost:5000/pago_pendiente`

**Para producción**:
- Success: `https://tudominio.com/pago_exitoso`
- Failure: `https://tudominio.com/pago_fallido`
- Pending: `https://tudominio.com/pago_pendiente`

## 🧪 Testing

### Tarjetas de prueba de MercadoPago

**Visa (Aprobada)**:
- Número: `4170068810108020`
- CVV: `123`
- Vencimiento: `12/25`

**Mastercard (Rechazada)**:
- Número: `5031755734530604`
- CVV: `123`
- Vencimiento: `12/25`

**OXXO (Pago en efectivo)**:
- Se genera un código para pagar en tienda

## 📱 Métodos de Pago Disponibles

### MercadoPago México soporta:

1. **Tarjetas de crédito/débito**:
   - Visa, Mastercard, American Express
   - Tarjetas locales mexicanas

2. **Transferencias bancarias**:
   - SPEI
   - Bancos mexicanos principales

3. **Efectivo**:
   - OXXO
   - 7-Eleven
   - Farmacias del Ahorro
   - Círculo K

4. **Monederos digitales**:
   - Cuenta de MercadoPago
   - Meses sin intereses

## 🔒 Seguridad

### Variables de entorno (Recomendado para producción)

1. **Crear archivo `.env`**:
```env
MP_ACCESS_TOKEN=APP_USR-tu-token-real
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_app
SECRET_KEY=tu_clave_secreta_super_segura
DATABASE_URL=postgresql://user:pass@localhost/agroconnect
```

2. **Instalar python-dotenv**:
```bash
pip install python-dotenv
```

3. **Modificar app.py**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

MP_ACCESS_TOKEN = os.getenv('MP_ACCESS_TOKEN')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
```

## 🎨 Personalización

### Customizar la experiencia de pago

En el archivo `pago_mercadopago.html` puedes:

1. **Cambiar colores**: Modificar variables CSS
2. **Agregar logos**: Incluir imagen de tu marca
3. **Personalizar textos**: Adaptar mensajes a tu audiencia
4. **Responsive design**: Ya incluido para móviles

## 📊 Webhooks (Opcional - Avanzado)

### Para notificaciones automáticas de pago

1. **Crear endpoint para webhooks**:
```python
@app.route('/webhook/mercadopago', methods=['POST'])
def webhook_mercadopago():
    # Procesar notificaciones de estado de pago
    pass
```

2. **Configurar en MercadoPago**:
   - URL: `https://tudominio.com/webhook/mercadopago`
   - Eventos: payment, merchant_order

## 🚦 Estados de Pago

### Estados que maneja la integración:

- ✅ **approved**: Pago aprobado → `pago_exitoso.html`
- ❌ **rejected**: Pago rechazado → `pago_fallido.html`
- ⏳ **pending**: Pago pendiente → `pago_pendiente.html`
- 🔄 **in_process**: En proceso → `pago_pendiente.html`

## 📞 Soporte

### En caso de problemas:

1. **Documentación oficial**: [https://www.mercadopago.com.mx/developers](https://www.mercadopago.com.mx/developers)
2. **Comunidad de desarrolladores**: GitHub, Stack Overflow
3. **Soporte MercadoPago**: A través de su panel de desarrolladores

## ✅ Checklist Final

- [ ] SDK de MercadoPago instalado
- [ ] Credenciales configuradas
- [ ] Email configurado
- [ ] URLs de callback configuradas
- [ ] Probado con tarjetas de test
- [ ] Templates personalizados
- [ ] Variables de entorno configuradas (producción)
- [ ] Webhooks configurados (opcional)

¡Tu integración con MercadoPago está lista! 🎉