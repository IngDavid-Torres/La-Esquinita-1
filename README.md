# La Esquinita - Plataforma de Comercio de Antojitos Mexicanos

Plataforma web para adquirir Elotes, Esquites, Patitas y Maruchan.

## Características

- 🌱 Catálogo de productos Mexicanos.
- 🛒 Sistema de carrito de compras
- 💳 Integración con MercadoPago
- 📧 Notificaciones por correo
- 👥 Panel de administración
- 📱 Diseño responsivo

## Tecnologías

- **Backend**: Flask (Python)
- **Base de datos**: PostgreSQL
- **Pagos**: MercadoPago API
- **Email**: Flask-Mail
- **Frontend**: HTML, CSS, JavaScript

## Instalación Local

```bash
pip install -r requirements.txt
python app.py
```

## Deploy en Railway

1. Conectar con GitHub
2. Configurar variables de entorno
3. Deploy automático

## Variables de Entorno

```
DATABASE_URL=postgresql://...
SECRET_KEY=tu_clave_secreta
MP_ACCESS_TOKEN=tu_token_mercadopago
MAIL_USERNAME=laesquinita.antojitos.mx@gmail.com
MAIL_PASSWORD=tu_password_app
```

## URL de Producción

Una vez desplegado, tu plataforma estará disponible en:
`https://laesquinita-production.up.railway.app`