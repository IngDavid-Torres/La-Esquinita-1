# Despliegue en Railway - La Esquinita

## 📋 Requisitos Previos
- Cuenta en [Railway](https://railway.app)
- Cuenta de GitHub con el repositorio
- Tokens de MercadoPago
- Credenciales de email (Gmail con app password)

## 🚀 Pasos para el Despliegue

### 1. Preparación en Railway
1. Ve a [Railway.app](https://railway.app)
2. Inicia sesión con GitHub
3. Crear nuevo proyecto: "New Project" → "Deploy from GitHub repo"
4. Selecciona el repositorio `La-Esquinita-1`

### 2. Configuración de Variables de Entorno
En Railway, ve a Variables y agrega las siguientes:

```env
DATABASE_URL=postgresql://...  # Railway generará automáticamente
SECRET_KEY=tu-clave-super-secreta-aqui
MP_ACCESS_TOKEN=TEST-tu-token-mercadopago
MP_PUBLIC_KEY=TEST-tu-public-key-mercadopago
MAIL_USERNAME=laesquinita.antojitos.mx@gmail.com
MAIL_PASSWORD=tu-app-password-gmail
FLASK_ENV=production
FLASK_DEBUG=False
```

### 3. Configuración de Base de Datos
1. En Railway: "New" → "Database" → "PostgreSQL"
2. Railway conectará automáticamente la base de datos
3. La variable `DATABASE_URL` se configurará automáticamente

### 4. Despliegue
1. Railway desplegará automáticamente desde GitHub
2. El proceso tomará 2-5 minutos
3. Recibirás una URL como: `https://tu-app.up.railway.app`

### 5. Configuración Post-Despliegue
1. **MercadoPago**: Configura webhook URL en tu dashboard de MercadoPago:
   ```
   https://tu-app.up.railway.app/webhook/mercadopago
   ```

2. **Email**: Asegúrate de que Gmail tenga habilitadas las "App Passwords"

3. **SSL**: Railway proporciona HTTPS automáticamente

## 🔧 Configuraciones Opcionales

### SMS con Twilio (Opcional)
Si deseas habilitar SMS:
```env
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### Dominio Personalizado
1. Ve a Settings en Railway
2. Agregar dominio personalizado
3. Configura DNS según instrucciones

## 📊 Monitoreo
- **Logs**: Disponibles en Railway dashboard
- **Métricas**: CPU, memoria, requests
- **Base de datos**: Métricas de conexiones y rendimiento

## 🛠️ Comandos Útiles
```bash
# Ver logs en tiempo real
railway logs

# Conectar a base de datos
railway connect postgresql

# Ejecutar migraciones (si necesario)
railway run python -c "from app import db; db.create_all()"
```

## 🚨 Resolución de Problemas

### Error de Conexión a Base de Datos
- Verifica que DATABASE_URL esté configurada
- Revisa logs para errores de conexión

### Error de MercadoPago
- Confirma tokens de TEST vs PRODUCTION
- Verifica webhook URL

### Error de Email
- Revisa App Password de Gmail
- Confirma configuración SMTP

## 📋 Checklist de Despliegue
- [ ] Repositorio actualizado en GitHub
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL agregada
- [ ] MercadoPago configurado (TEST mode)
- [ ] Email configurado
- [ ] Despliegue exitoso
- [ ] Pruebas básicas funcionando
- [ ] SSL habilitado (automático)

## 🌐 URLs Importantes
- **Aplicación**: `https://tu-app.up.railway.app`
- **Admin**: `https://tu-app.up.railway.app/panel_admin`
- **API Status**: `https://tu-app.up.railway.app/keep-alive`

¡Tu aplicación estará lista para recibir pedidos! 🌮🎉