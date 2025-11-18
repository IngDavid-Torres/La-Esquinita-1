from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from datetime import datetime
import os
import sys
from werkzeug.utils import secure_filename
import re
import io
from flask import send_file
from flask_mail import Mail, Message
from sqlalchemy.sql import exists
from sqlalchemy import and_, not_, exists, cast, String, or_, func
from sqlalchemy.orm import aliased
import mercadopago
import time
import logging
from dotenv import load_dotenv
import json
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64
import threading
load_dotenv()


if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

logger = logging.getLogger(__name__)

def add_security_headers(response):
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

app = Flask(__name__)


app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['TESTING'] = False


app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🚀 Iniciando La Esquinita en modo: {app.config['ENV']}")


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///laesquinita.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if DATABASE_URL and 'postgresql://' in DATABASE_URL:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'pool_size': 5,
        'connect_args': {
            'connect_timeout': 30,
            'application_name': 'la_esquinita_app',
            'sslmode': 'prefer'  
        }
    }
    print("🐘 Configuración PostgreSQL para Railway")
else:
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'connect_args': {'timeout': 20}
    }
    print("📁 Configuración SQLite para desarrollo local")
app.secret_key = os.environ.get('SECRET_KEY') or 'clave_secreta_super_segura'


try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy inicializado correctamente")
except Exception as db_init_error:
    print(f"❌ Error inicializando SQLAlchemy: {str(db_init_error)}")
    # Fallback a configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    db = SQLAlchemy(app)
    print("🔄 Fallback a SQLite activado")
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN') or "TEST-7916427332588639-102718-00ee5129ad06c2ceba14e4e44b94d22e-191563398"
MP_PUBLIC_KEY = os.environ.get('MP_PUBLIC_KEY') or "TEST-c1e625f3-6498-4c5e-9fda-d2b6b5a0a7de-191563398"
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)


def generate_captcha_code(length=5):
    
    chars = string.ascii_uppercase + string.digits
   
    chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(random.choice(chars) for _ in range(length))

def create_captcha_image(code):
    
    try:
        width, height = 200, 80
        
        img = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
       
        for _ in range(50):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            draw.point((x, y), fill=(random.randint(220, 255), random.randint(220, 255), random.randint(220, 255)))
        
        
        font = ImageFont.load_default()
        
        
        x = 60
        y = 30
        
      
        color = (0, 0, 0)
       
        offset_x = x
        for char in code:
            
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    draw.text((offset_x + dx, y + dy), char, font=font, fill=color)
            offset_x += 20
        
       
        for _ in range(3):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(150, 150, 150), width=1)
        
        logger.info(f"Imagen CAPTCHA creada exitosamente para código: {code}")
        return img
    except Exception as e:
        logger.error(f"Error creando imagen CAPTCHA: {str(e)}", exc_info=True)
        
        img = Image.new('RGB', (200, 80), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 30), code, fill=(0, 0, 0))
        logger.info(f"Usando CAPTCHA ultra simple de emergencia")
        return img

def create_captcha_session(session):
   
    try:
        code = generate_captcha_code()
        logger.info(f"Código CAPTCHA generado: {code}")
        
        img = create_captcha_image(code)
        
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode()
        
        logger.info(f"Imagen convertida a base64. Tamaño: {len(img_base64)} caracteres")
        
       
        session['captcha_code'] = code
        
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        logger.error(f"Error en create_captcha_session: {str(e)}", exc_info=True)
       
        return None

def validate_captcha_session(session, user_input):
    
    if 'captcha_code' not in session:
        return False
    
    stored_code = session.get('captcha_code', '').upper()
    user_code = user_input.upper().strip()
    
    
    session.pop('captcha_code', None)
    
    return stored_code == user_code

@app.before_request
def mantener_sesion_activa():
    
    if 'usuario_id' in session:
        session.permanent = True
        session.modified = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'laesquinita.antojitos.mx@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'pnyy wnaj yisq wtgv'
mail = Mail(app)

def enviar_confirmacion_pago(correo_destino, pedido, metodo_pago):
    """Envía correo de confirmación de forma directa y robusta"""
    try:
        print(f"📧 INICIO envío correo a {correo_destino}")
        print(f"📧 SMTP Server: {app.config.get('MAIL_SERVER')}")
        print(f"📧 SMTP Port: {app.config.get('MAIL_PORT')}")
        print(f"📧 SMTP User: {app.config.get('MAIL_USERNAME')}")
        print(f"📧 SMTP Password configurado: {'Sí' if app.config.get('MAIL_PASSWORD') else 'No'}")
        
        subject = f"Confirmación de Pedido #{pedido.id} - La Esquinita"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #fffdf7; padding: 20px; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2e7d32; margin-bottom: 10px;">🌽 La Esquinita</h1>
                <h2 style="color: #ff5722;">¡Pago Confirmado!</h2>
            </div>
            <div style="background: #f1f8e9; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #2e7d32; margin-top: 0;">📋 Detalles del Pedido</h3>
                <p><strong>Pedido #:</strong> {pedido.id}</p>
                <p><strong>Nombre:</strong> {pedido.nombre}</p>
                <p><strong>Correo:</strong> {pedido.correo}</p>
                <p><strong>Dirección:</strong> {pedido.direccion}</p>
                <p><strong>Total:</strong> ${pedido.total:.2f} MXN</p>
                <p><strong>Método de Pago:</strong> {metodo_pago}</p>
                <p><strong>Estado:</strong> <span style="color: #4caf50; font-weight: bold;">{pedido.estado}</span></p>
                <p><strong>Fecha:</strong> {pedido.fecha.strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #ff5722; margin-top: 0;">🚀 ¿Qué sigue?</h4>
                <p>✅ Tu pedido está siendo preparado con amor</p>
                <p>⏱️ Tiempo estimado de entrega: 30-45 minutos</p>
                <p>📞 Te contactaremos si necesitamos algo adicional</p>
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #666;">¡Gracias por elegir La Esquinita! 🌽</p>
                <p style="color: #2e7d32; font-weight: bold;">El auténtico sabor mexicano</p>
            </div>
        </div>
        """
        
        msg = Message(
            subject=subject,
            recipients=[correo_destino],
            html=html_body,
            sender=app.config['MAIL_USERNAME']
        )
        
        print(f"📤 Enviando mensaje...")
        mail.send(msg)
        print(f"✅ Correo enviado exitosamente a {correo_destino}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR ENVIANDO CORREO:")
        print(f"❌ Destinatario: {correo_destino}")
        print(f"❌ Error: {str(e)}")
        print(f"❌ Tipo: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback completo:")
        traceback.print_exc()
        return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20))
    telefono_verificado = db.Column(db.Boolean, default=False)
    direcciones = db.relationship('Direccion', backref='usuario', lazy=True)
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)
    contacto = db.relationship('Contacto', backref='usuario', lazy=True)
    pagos = db.relationship('Pago', backref='usuario', lazy=True)
class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(200), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    categoria = db.relationship('Categoria', back_populates='productos')
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    productos = db.relationship('Producto', back_populates='categoria')
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name="fk_pedido_usuario"), nullable=False)
    nombre = db.Column(db.String(200), nullable=True)
    correo = db.Column(db.String(200), nullable=True)
    direccion = db.Column(db.String(500), nullable=True)
    metodo_pago = db.Column(db.String(100), nullable=True)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(50), default="Pendiente")
    payment_id = db.Column(db.String(200), nullable=True)
class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    producto = db.relationship('Producto')
class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    respuesta = db.Column(db.Text)
class Direccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
class MetodoPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name="fk_pago_usuario"), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id', name="fk_pago_pedido"), nullable=False)
    metodo_pago_id = db.Column(db.Integer, db.ForeignKey('metodo_pago.id', name="fk_pago_metodo"), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(50), default="Completado")
def crear_admin():
    with app.app_context():
        admin_existente = Administrador.query.filter_by(email="admin@laesquinita.com").first()
        if not admin_existente:
            nuevo_admin = Administrador(nombre="Admin La Esquinita", email="admin@laesquinita.com", password="admin123")
            db.session.add(nuevo_admin)
            db.session.commit()
            print("✅ Administrador creado: admin@laesquinita.com / admin123")
        else:
            print("ℹ️ Administrador ya existe")
        
        
        print("ℹ️ Las categorías y productos se crean desde el panel de administración")

class PedidoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    producto = db.relationship('Producto')
    pedido = db.relationship('Pedido', backref='items')
class Tarjeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    numero = db.Column(db.String(16), nullable=False)
    propietario = db.Column(db.String(100), nullable=False)
    fecha_expiracion = db.Column(db.String(5), nullable=False)
@app.route('/')
def inicio():
    cantidad_carrito = 0
    if 'usuario_id' in session and session.get('tipo_usuario') == 'Cliente':
        cantidad_carrito = db.session.query(func.sum(Carrito.cantidad)).filter_by(usuario_id=session['usuario_id']).scalar() or 0
    return render_template('inicio.html', cantidad_carrito=cantidad_carrito)
@app.route('/productos')
def productos():
    try:
       
        productos = []
        categorias = []
        
        try:
            productos = Producto.query.filter_by(activo=True).all()
            categorias = Categoria.query.all()
        except Exception as db_error:
            print(f"Error de BD en productos: {str(db_error)}")
            
            try:
                db.session.rollback()
                productos = Producto.query.filter_by(activo=True).all()
                categorias = Categoria.query.all()
            except Exception as retry_error:
                print(f"Error en reintento: {str(retry_error)}")
                productos = []
                categorias = []
        
        cantidad_carrito = 0
        if session.get('usuario_id') and session.get('tipo_usuario') == 'Cliente':
            try:
                cantidad_carrito = db.session.query(func.coalesce(func.sum(Carrito.cantidad), 0)).filter_by(usuario_id=session.get('usuario_id')).scalar() or 0
            except:
                cantidad_carrito = 0
        
        if not productos:
            flash('No hay productos disponibles por el momento', 'info')
        
        return render_template('productos.html', productos=productos, categorias=categorias, cantidad_carrito=cantidad_carrito)
        
    except Exception as e:
        print(f"Error general en productos: {str(e)}")
        flash('Error al cargar productos, intenta más tarde', 'error')
        return redirect(url_for('inicio'))
@app.route('/contacto')
def contacto():
    cantidad_carrito = 0
    if 'usuario_id' in session and session.get('tipo_usuario') == 'Cliente':
        cantidad_carrito = db.session.query(func.sum(Carrito.cantidad)).filter_by(usuario_id=session['usuario_id']).scalar() or 0
    return render_template('contacto.html', cantidad_carrito=cantidad_carrito)
@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    nombre = request.form['nombre']
    email = request.form['email']
    mensaje = request.form['mensaje']
    nuevo_mensaje = Contacto(usuario_id=session['usuario_id'], mensaje=mensaje)
    db.session.add(nuevo_mensaje)
    db.session.commit()
    flash("Tu mensaje fue enviado con Ã©xito.", "success")
    return redirect(url_for('contacto'))

@app.route('/generate_captcha')
def generate_captcha():
   
    try:
        logger.info("=== Generando CAPTCHA (SVG) ===")
        code = generate_captcha_code()
        session['captcha_code'] = code
        logger.info(f"📝 Código CAPTCHA guardado en sesión: {code}")

        width, height = 260, 100
        font_size = 42
        start_x = 28
        baseline_y = 62
        spacing = 40

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="captcha">',
            '<rect width="100%" height="100%" rx="10" fill="#eeeeee"/>',
        ]

      
        for _ in range(4):
            x1, y1 = random.randint(10, width-10), random.randint(10, height-10)
            x2, y2 = random.randint(10, width-10), random.randint(10, height-10)
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#d3d3d3" stroke-width="1"/>')

       
        x = start_x
        for ch in code:
            angle = random.randint(-12, 12)
            parts.append(
                f'<g transform="translate({x},{baseline_y}) rotate({angle})">'
                f'<text text-anchor="middle" font-family="DejaVu Sans Mono, Consolas, monospace" font-size="{font_size}" font-weight="700" fill="#111">{ch}</text>'
                f'</g>'
            )
            x += spacing

     
        parts.append('<line x1="20" y1="50" x2="240" y2="50" stroke="#bdbdbd" stroke-width="1"/>')
        parts.append('</svg>')

        svg = ''.join(parts)
        svg_b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        data_uri = f'data:image/svg+xml;base64,{svg_b64}'
        logger.info(f"✅ CAPTCHA SVG generado. Longitud: {len(data_uri)}")
        
        response = jsonify({'success': True, 'image': data_uri})
        logger.info("✅ Respuesta JSON creada correctamente")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generando CAPTCHA SVG: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        tipo_usuario = request.form.get('tipo_usuario', 'Cliente')
        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya estÃ¡ registrado.", "error")
            return redirect(url_for('registro'))
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$", password):
            flash("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un carácter especial.", "error")
            return redirect(url_for('registro'))
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password, tipo_usuario=tipo_usuario)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('login'))
    tipo_usuario = request.args.get('tipo', 'Cliente')
    return render_template('registro.html', tipo_usuario=tipo_usuario)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            logger.info("🚀 INICIO DE PROCESO DE LOGIN")
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            captcha_input = request.form.get('captcha', '').strip()
            
            logger.info(f"📧 Email recibido: '{email}'")
            logger.info(f"🔑 Password recibido: '{password}'")
            logger.info(f"🔒 CAPTCHA recibido: '{captcha_input}'")
            logger.info(f"📋 Form data completo: {dict(request.form)}")
            
            if not email or not password:
                logger.warning("⚠️ Campos vacíos detectados")
                flash('Por favor completa todos los campos', 'error')
                return render_template('login.html')
            
            
            logger.info("🔍 Buscando admin en base de datos...")
            admin = Administrador.query.filter_by(email=email, password=password).first()
            logger.info(f"🔎 Resultado búsqueda admin: {admin}")
            
            if admin:
                logger.info(f"✅ ADMIN ENCONTRADO: {admin.nombre} (ID: {admin.id})")
                session['usuario_id'] = admin.id
                session['usuario_nombre'] = admin.nombre
                session['tipo_usuario'] = "Administrador"
                session.permanent = True  
                logger.info(f"📝 Session configurada: {dict(session)}")
                logger.info(f"🔄 Generando redirect a: {url_for('panel_admin')}")
                flash(f'Bienvenido Administrador {admin.nombre}', 'success')
                redirect_response = redirect(url_for('panel_admin'))
                logger.info(f"📤 ENVIANDO REDIRECT A PANEL_ADMIN: {redirect_response}")
                logger.info("🎯 RETORNANDO RESPUESTA DE REDIRECT ADMIN")
                return redirect_response
            
           
            if not validate_captcha_session(session, captcha_input):
                logger.warning("⚠️ CAPTCHA incorrecto")
                flash('Código CAPTCHA incorrecto. Inténtalo de nuevo.', 'error')
                return render_template('login.html')
            
        
            logger.info("🔍 Buscando usuario en base de datos...")
            usuario = Usuario.query.filter_by(email=email, password=password).first()
            logger.info(f"🔎 Resultado búsqueda usuario: {usuario}")
            
            if usuario:
                logger.info(f"✅ USUARIO ENCONTRADO: {usuario.nombre} (Tipo: {usuario.tipo_usuario})")
                session['usuario_id'] = usuario.id
                session['usuario_nombre'] = usuario.nombre
                session['tipo_usuario'] = usuario.tipo_usuario
                session.permanent = True  # Mantener sesión activa
                flash(f'Bienvenido {usuario.nombre}', 'success')
                if usuario.tipo_usuario == "Cliente":
                    logger.info("🔄 REDIRIGIENDO A PANEL_CLIENTE")
                    return redirect(url_for('panel_cliente'))
                elif usuario.tipo_usuario == "Productor":
                    logger.info("🔄 REDIRIGIENDO A PANEL_PRODUCTOR")
                    return redirect(url_for('panel_productor'))
            else:
                logger.warning("❌ Usuario tampoco encontrado")
            
            logger.warning("❌❌ CREDENCIALES INCORRECTAS - Ni admin ni usuario encontrado")
            flash('Credenciales incorrectas', 'error')
            return render_template('login.html')
            
        except Exception as e:
            logger.error(f"💥 ERROR EN LOGIN: {str(e)}")
            print(f"Error en login: {str(e)}")
            flash('Error del servidor, intenta de nuevo', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/panel_cliente')
def panel_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    direccion = Direccion.query.filter_by(usuario_id=session['usuario_id']).first()
    cantidad_carrito = db.session.query(func.sum(Carrito.cantidad)).filter_by(usuario_id=session['usuario_id']).scalar() or 0
    tarjetas = Tarjeta.query.filter_by(usuario_id=session['usuario_id']).all()
    response = make_response(render_template('panel_cliente.html', usuario=usuario, direccion=direccion, cantidad_carrito=cantidad_carrito, tarjetas=tarjetas))
    return add_security_headers(response)
@app.route('/perfil_cliente', methods=['GET'])
def perfil_cliente():
    usuario = Usuario.query.get(session['usuario_id'])
    direccion = Direccion.query.filter_by(usuario_id=session['usuario_id']).first()
    return render_template('perfil_cliente.html', usuario=usuario, direccion=direccion)
@app.route('/panel_admin')
def panel_admin():
    logger.info(f"🎯 PANEL_ADMIN ACCEDIDO - Método: {request.method}")
    logger.info(f"🔍 Session actual COMPLETA: {dict(session)}")
    logger.info(f"🔍 Session.get('usuario_id'): {session.get('usuario_id')}")
    logger.info(f"🔍 Session.get('tipo_usuario'): {session.get('tipo_usuario')}")
    logger.info(f"🔍 'usuario_id' in session: {'usuario_id' in session}")
    logger.info(f"🔍 session.get('tipo_usuario') != 'Administrador': {session.get('tipo_usuario') != 'Administrador'}")
    logger.info(f"🌐 Headers: {dict(request.headers)}")
    logger.info(f"🍪 Cookies: {dict(request.cookies)}")
   
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'Administrador':
        logger.warning(f"⚠️ ACCESO DENEGADO a panel_admin")
        logger.warning(f"   - 'usuario_id' in session: {'usuario_id' in session}")
        logger.warning(f"   - session.get('tipo_usuario'): {session.get('tipo_usuario')}")
        logger.warning(f"   - Session completa: {dict(session)}")
        flash('Acceso denegado. Solo administradores pueden acceder a esta página.', 'error')
        return redirect(url_for('login'))
    
    logger.info(f"✅ Admin autenticado accediendo a panel: {session.get('usuario_nombre')}")
    
    try:
        q = request.args.get('q', '').strip()
        filtro = request.args.get('filtro', '')
        
        
        try:
            total_usuarios = Usuario.query.count()
            pedidos_activos = Pedido.query.filter(Pedido.estado != 'Entregado').count()
            total_productos = Producto.query.count()
            mensajes_pendientes = Contacto.query.filter(Contacto.respuesta == None).count()
        except Exception as stats_error:
            print(f"Error obteniendo estadísticas: {str(stats_error)}")
            total_usuarios = 0
            pedidos_activos = 0
            total_productos = 0
            mensajes_pendientes = 0
        
        resultados = []
        if q:
            try:
                if filtro == "usuarios":
                    resultados = Usuario.query.filter(
                        (Usuario.nombre.ilike(f"%{q}%")) | (Usuario.email.ilike(f"%{q}%"))
                    ).all()
                elif filtro == "pedidos":
                    resultados = Pedido.query.join(Usuario).filter(
                        (Pedido.id == q) |
                        (Usuario.nombre.ilike(f"%{q}%")) |
                        (Pedido.estado.ilike(f"%{q}%"))
                    ).all()
                elif filtro == "productos":
                    resultados = Producto.query.filter(
                        (Producto.nombre.ilike(f"%{q}%")) |
                        (Producto.descripcion.ilike(f"%{q}%"))
                    ).all()
                else:
                    usuarios = Usuario.query.filter(
                        (Usuario.nombre.ilike(f"%{q}%")) | (Usuario.email.ilike(f"%{q}%"))
                    ).all()
                    pedidos = Pedido.query.join(Usuario).filter(
                        (Pedido.id == q) |
                        (Usuario.nombre.ilike(f"%{q}%")) |
                        (Pedido.estado.ilike(f"%{q}%"))
                    ).all()
                    productos = Producto.query.filter(
                        (Producto.nombre.ilike(f"%{q}%")) |
                        (Producto.descripcion.ilike(f"%{q}%"))
                    ).all()
                    resultados = usuarios + pedidos + productos
            except Exception as search_error:
                print(f"Error en búsqueda: {str(search_error)}")
                resultados = []
                flash('Error en la búsqueda', 'warning')
        
        logger.info(f"🎨 Renderizando panel_admin.html para: {session.get('usuario_nombre')}")
        response = make_response(render_template(
            'panel_admin.html',
            total_usuarios=total_usuarios,
            pedidos_activos=pedidos_activos,
            total_productos=total_productos,
            mensajes_pendientes=mensajes_pendientes,
            resultados=resultados,
            q=q,
            filtro=filtro
        ))
        logger.info(f"✅ Template renderizado correctamente, enviando respuesta")
        return add_security_headers(response)
        
    except Exception as e:
        print(f"Error general en panel_admin: {str(e)}")
        flash('Error cargando panel de administración', 'error')
        return redirect(url_for('inicio'))

@app.route('/logout')
def logout():
    user_type = session.get('tipo_usuario', 'Desconocido')
    user_name = session.get('usuario_nombre', 'Usuario')
    session.clear()
    for key in list(session.keys()):
        session.pop(key, None)
    session.permanent = False
    response = make_response(redirect(url_for('inicio')))
    response.set_cookie('session', '', expires=0, path='/',
                       secure=False, httponly=True, samesite='Lax')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    flash(f'SesiÃ³n cerrada correctamente. Â¡Hasta pronto, {user_name}! ðŸ‘‹', 'success')
    return response
@app.route('/logout/admin')
def logout_admin():
    if session.get('tipo_usuario') != 'Administrador':
        flash('Acceso denegado. Solo administradores pueden usar esta funciÃ³n.', 'error')
        return redirect(url_for('inicio'))
    admin_name = session.get('usuario_nombre', 'Administrador')
    session_keys_to_clear = [
        'usuario_id', 'usuario_nombre', 'tipo_usuario',
        'pedido_temp', 'ticket_transferencia', 'productor_id'
    ]
    for key in session_keys_to_clear:
        session.pop(key, None)
    session.clear()
    session.permanent = False
    response = make_response(redirect(url_for('inicio')))
    response.set_cookie('session', '', expires=0, path='/',
                       secure=False, httponly=True, samesite='Lax')
    response.set_cookie('admin_session', '', expires=0, path='/',
                       secure=False, httponly=True, samesite='Lax')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    flash(f'Sesión de administrador cerrada completamente. ¡Hasta pronto, {admin_name}! 🔐', 'success')
    return response
@app.route('/logout/cliente')
def logout_cliente():
    if session.get('tipo_usuario') != 'Cliente':
        flash('Acceso denegado. Solo clientes pueden usar esta función.', 'error')
        return redirect(url_for('inicio'))
    client_name = session.get('usuario_nombre', 'Cliente')
    session_keys_to_clear = [
        'usuario_id', 'usuario_nombre', 'tipo_usuario',
        'pedido_temp', 'ticket_transferencia'
    ]
    for key in session_keys_to_clear:
        session.pop(key, None)
    session.clear()
    session.permanent = False
    response = make_response(redirect(url_for('inicio')))
    response.set_cookie('session', '', expires=0, path='/',
                       secure=False, httponly=True, samesite='Lax')
    response.set_cookie('client_session', '', expires=0, path='/',
                       secure=False, httponly=True, samesite='Lax')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    flash(f'Sesión de cliente cerrada completamente. ¡Hasta pronto, {client_name}! 🛡️', 'success')
    return response
@app.route('/logout/force')
def logout_force():
    
    session_keys = list(session.keys())
    user_data = {
        'name': session.get('usuario_nombre', 'Usuario'),
        'type': session.get('tipo_usuario', 'Desconocido')
    }
    for key in session_keys:
        session.pop(key, None)
    session.clear()
    session.permanent = False
    response = make_response(redirect(url_for('inicio')))
    cookies_to_clear = ['session', 'admin_session', 'client_session', 'csrf_token']
    for cookie_name in cookies_to_clear:
        response.set_cookie(cookie_name, '', expires=0, path='/',
                           secure=False, httponly=True, samesite='Lax')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    flash(f'Destrucción total de sesión completada. Todos los datos eliminados. ¡Hasta pronto, {user_data["name"]}! 🔥', 'warning')
    return response
@app.route('/keep-alive', methods=['POST'])
def keep_alive():
    if 'usuario_id' in session:
        session.permanent = True
        return {'status': 'success', 'message': 'Sesión renovada'}, 200
    return {'status': 'error', 'message': 'No hay sesión activa'}, 401
@app.route('/webhook/mercadopago', methods=['POST'])
def webhook_mercadopago():
    try:
        data = request.get_json()
        if data and data.get('type') == 'payment':
            payment_id = data['data']['id']
            payment_response = sdk.payment().get(payment_id)
            payment = payment_response["response"]
            if payment_response["status"] == 200:
                external_reference = payment.get('external_reference', '')
                payment_status = payment.get('status', '')
                if external_reference.startswith('laesquinita-'):
                    parts = external_reference.split('-')
                    if len(parts) >= 2:
                        usuario_id = int(parts[1])
                        if payment_status == 'approved':
                            pedido_data = session.get('pedido_temp')
                            if pedido_data:
                                try:
                                    nuevo_pedido = Pedido(
                                        usuario_id=usuario_id,
                                        nombre=pedido_data['nombre'],
                                        correo=pedido_data['correo'],
                                        direccion=pedido_data['direccion'],
                                        metodo_pago='MercadoPago',
                                        total=pedido_data['total'],
                                        estado='Confirmado',
                                        payment_id=str(payment_id)
                                    )
                                    db.session.add(nuevo_pedido)
                                    for producto_data in pedido_data['productos']:
                                        detalle = PedidoItem(
                                            pedido_id=nuevo_pedido.id,
                                            producto_id=producto_data['id'],
                                            cantidad=producto_data['cantidad']
                                        )
                                        db.session.add(detalle)
                                    Carrito.query.filter_by(usuario_id=usuario_id).delete()
                                    db.session.commit()
                                    try:
                                        enviar_confirmacion_pago(pedido_data['correo'], nuevo_pedido, 'MercadoPago TEST')
                                    except Exception as email_error:
                                        print(f"Error enviando email de confirmaciÃ³n: {email_error}")
                                except Exception as e:
                                    db.session.rollback()
                                    print(f"Error procesando webhook: {str(e)}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error en webhook MercadoPago: {str(e)}")
        return jsonify({'status': 'error'}), 500
@app.route('/carrito')
def carrito():
    if not session.get('usuario_nombre'):
        return redirect(url_for('inicio', no_sesion=1))
    usuario_id = session['usuario_id']
    carrito_items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    productos_en_carrito = []
    total = 0
    for item in carrito_items:
        producto = Producto.query.get(item.producto_id)
        if producto:
            producto.cantidad = item.cantidad
            productos_en_carrito.append(producto)
            total += producto.precio * item.cantidad
    return render_template('carrito.html', productos=productos_en_carrito, total=total)
def calcular_total_carrito(usuario_id):
    carrito_items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    if not carrito_items:
        return 0
    total = sum(item.producto.precio * item.cantidad for item in carrito_items)
    return total
@app.route('/pago_mercadopago', methods=['GET', 'POST'])
def pago_mercadopago():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    carrito_items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    if not carrito_items:
        flash("Tu carrito está vacío", "error")
        return redirect(url_for('carrito'))
    productos = []
    total = 0
    items_mp = []
    for item in carrito_items:
        producto = Producto.query.get(item.producto_id)
        if producto:
            producto.cantidad = item.cantidad
            productos.append(producto)
            subtotal = producto.precio * item.cantidad
            total += subtotal
            items_mp.append({
                "title": producto.nombre,
                "quantity": item.cantidad,
                "unit_price": float(producto.precio),
                "currency_id": "MXN"
            })
    if request.method == 'POST':
        print("🔄 POST recibido en pago_mercadopago")
        
        
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        print(f"📝 Datos recibidos: nombre='{nombre}', correo='{correo}', direccion='{direccion}'")
        
        
        if not nombre or len(nombre) < 3:
            flash("El nombre debe tener al menos 3 caracteres", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        if not correo or '@' not in correo:
            flash("Por favor ingresa un correo válido", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        if not direccion or len(direccion) < 10:
            flash("La dirección debe ser más específica (mínimo 10 caracteres)", "error")
            return render_template('pago_mercadopago.html', productos=productos, total=total)
        
        preference_data = {
            "items": items_mp,
            "payer": {
                "name": nombre,
                "email": correo
            },
            "back_urls": {
                "success": url_for('pago_exitoso', _external=True),
                "failure": url_for('pago_fallido', _external=True),
                "pending": url_for('pago_pendiente', _external=True)
            },
            "notification_url": url_for('webhook_mercadopago', _external=True),
            "auto_return": "approved",
            "external_reference": f"laesquinita-{usuario_id}-{int(datetime.now().timestamp())}",
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
        
        
        if MP_ACCESS_TOKEN.startswith("TEST-"):
            print("🧪 MODO TEST DETECTADO - Saltando API de MercadoPago")
            session['pedido_temp'] = {
                'nombre': nombre,
                'correo': correo,
                'direccion': direccion,
                'total': total,
                'productos': [{'id': p.id, 'cantidad': p.cantidad} for p in productos]
            }
            return render_template('pago_test_processing.html', 
                                 nombre=nombre, correo=correo, 
                                 direccion=direccion, total=total,
                                 productos=productos)
        
        try:
            print(f"🧪 DEBUG: Creando preferencia con datos: {preference_data}")
            preference_response = sdk.preference().create(preference_data)
            print(f"🧪 DEBUG: Respuesta de MercadoPago: {preference_response}")
            preference = preference_response["response"]
            if preference_response["status"] == 201:
                session['pedido_temp'] = {
                    'nombre': nombre,
                    'correo': correo,
                    'direccion': direccion,
                    'total': total,
                    'productos': [{'id': p.id, 'cantidad': p.cantidad} for p in productos]
                }
                print(f"ðŸ”§ DEBUG: Redirigiendo a: {preference['init_point']}")
                if MP_ACCESS_TOKEN.startswith("TEST-"):
                    print("🧪 Modo TEST detectado - Mostrando simulación")
                    return render_template('pago_test_processing.html', 
                                         nombre=nombre, correo=correo, 
                                         direccion=direccion, total=total,
                                         productos=productos)
                else:
                    
                    return redirect(preference["init_point"])
            else:
                print(f"âŒ DEBUG: Error en status: {preference_response}")
                flash("Error al procesar el pago", "error")
                return redirect(url_for('carrito'))
        except Exception as e:
            print(f"âŒ DEBUG: ExcepciÃ³n: {str(e)}")
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('carrito'))
    return render_template('pago_mercadopago.html', productos=productos, total=total)
@app.route('/pago_exitoso')
def pago_exitoso():
    if 'usuario_id' not in session or 'pedido_temp' not in session:
        return redirect(url_for('inicio'))
    pedido_data = session['pedido_temp']
    usuario_id = session['usuario_id']
    try:
        print(f"DEBUG: Procesando pago exitoso para usuario {usuario_id}")
        print(f"DEBUG: Datos del pedido: {pedido_data}")
        carrito_antes = Carrito.query.filter_by(usuario_id=usuario_id).all()
        print(f"🧪DEBUG: Items en carrito ANTES: {len(carrito_antes)}")
        nuevo_pedido = Pedido(
            usuario_id=usuario_id,
            estado='Confirmado',
            total=pedido_data['total'],
            fecha=datetime.now(),
            direccion=pedido_data['direccion']
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        print(f"DEBUG: Pedido creado con ID: {nuevo_pedido.id}")
        for producto_info in pedido_data['productos']:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=producto_info['id'],
                cantidad=producto_info['cantidad']
            )
            db.session.add(pedido_item)
            print(f"DEBUG: Agregado item: Producto {producto_info['id']}, Cantidad {producto_info['cantidad']}")
        print(f"DEBUG: Limpiando carrito para usuario {usuario_id}")
        items_eliminados = Carrito.query.filter_by(usuario_id=usuario_id).delete()
        print(f"DEBUG: Items eliminados del carrito: {items_eliminados}")
        db.session.commit()
        print(f"DEBUG: Transacción confirmada en base de datos")
        carrito_despues = Carrito.query.filter_by(usuario_id=usuario_id).all()
        print(f"DEBUG: Items en carrito DESPUÉS: {len(carrito_despues)}")
        try:
            enviar_confirmacion_pago(pedido_data['correo'], nuevo_pedido, 'MercadoPago')
        except Exception as email_error:
            print(f"❌ Error enviando email de confirmación: {email_error}")
        session.pop('pedido_temp', None)
        print(f"DEBUG: Datos temporales limpiados")
        flash('¡Pago procesado exitosamente!', 'success')
        return render_template('pago_exitoso.html', pedido=nuevo_pedido)
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el pedido: {str(e)}', 'error')
        return redirect(url_for('carrito'))
@app.route('/pago_fallido')
def pago_fallido():
    error_code = request.args.get('error_code', 'No especificado')
    error_message = request.args.get('error_message', 'Error al procesar el pago')
    session.pop('pedido_temp', None)
    flash('El pago no pudo ser procesado', 'error')
    return render_template('pago_fallido.html',
                         error_code=error_code,
                         error_message=error_message)
@app.route('/pago_pendiente')
def pago_pendiente():
    if 'pedido_temp' not in session:
        return redirect(url_for('inicio'))
    pedido_data = session['pedido_temp']
    payment_id = request.args.get('payment_id', '')
    payment_method = request.args.get('payment_type', 'MercadoPago')
    return render_template('pago_pendiente.html',
                         payment_id=payment_id,
                         payment_method=payment_method,
                         total=pedido_data.get('total', 0))
def send_confirmation_email(email, nombre, pedido):
    try:
        msg = Message(
            'Confirmación de Pedido - La Esquinita',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #00a650; color: white; padding: 20px; text-align: center;">
                <h1> La Esquinita</h1>
                <h2>Â¡Pedido Confirmado!</h2>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre}</strong>,</p>
                <p>¡Gracias por tu compra! Tu pedido ha sido confirmado y pronto comenzaremos a prepararlo.</p>
                <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <h3>📋 Detalles del pedido</h3>
                    <p><strong>Número de pedido:</strong> #{pedido.id}</p>
                    <p><strong>Fecha:</strong> {pedido.fecha.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Total:</strong> ${pedido.total:.2f}</p>
                    <p><strong>Estado:</strong> {pedido.estado}</p>
                </div>
                <p>Te mantendremos informado sobre el estado de tu pedido.</p>
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                <div style="text-align: center; margin-top: 30px;">
                    <p>Â¡Gracias por elegir La Esquinita!</p>
                </div>
            </div>
        </div>
        """
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False
@app.route('/pago', methods=['GET', 'POST'])
def pago():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tarjetas = Tarjeta.query.filter_by(usuario_id=usuario_id).all()
    carrito_items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    productos = []
    total = 0
    for item in carrito_items:
        producto = Producto.query.get(item.producto_id)
        if producto:
            producto.cantidad = item.cantidad
            productos.append(producto)
            total += producto.precio * item.cantidad
    if request.method == 'POST':
        tarjeta_id = request.form.get('tarjeta_guardada')
        if tarjeta_id:
            tarjeta = Tarjeta.query.get(int(tarjeta_id))
            nombre = request.form['nombre']
            correo = request.form['correo']
            direccion = request.form['direccion']
            numero_tarjeta = tarjeta.numero
            propietario = tarjeta.propietario
            fecha_expiracion = tarjeta.fecha_expiracion
        else:
            nombre = request.form['nombre']
            correo = request.form['correo']
            direccion = request.form['direccion']
            numero_tarjeta = request.form['numero_tarjeta']
            propietario = request.form['propietario']
            fecha_expiracion = request.form['fecha_expiracion']
            cvv = request.form['cvv']
            tarjeta_existente = Tarjeta.query.filter_by(
                usuario_id=usuario_id,
                numero=numero_tarjeta
            ).first()
            if not tarjeta_existente:
                nueva_tarjeta = Tarjeta(
                    usuario_id=usuario_id,
                    numero=numero_tarjeta,
                    propietario=propietario,
                    fecha_expiracion=fecha_expiracion
                )
                db.session.add(nueva_tarjeta)
                db.session.commit()
        
      
        nuevo_pedido = Pedido(
            usuario_id=usuario_id, 
            total=total, 
            estado="Confirmado",
            nombre=nombre,
            correo=correo,
            direccion=direccion,
            metodo_pago="Tarjeta de Crédito",
            fecha=datetime.now()
        )
        db.session.add(nuevo_pedido)
        db.session.commit()
        for item in carrito_items:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad
            )
            db.session.add(pedido_item)
        db.session.commit()
        Carrito.query.filter_by(usuario_id=usuario_id).delete()
        db.session.commit()
        
        
        try:
            print(f"📧 Preparando envío de correo para pedido #{nuevo_pedido.id}")
            enviar_confirmacion_pago(correo, nuevo_pedido, 'Tarjeta de Crédito')
        except Exception as e:
            print(f"⚠️ Error programando envío de correo: {e}")
        
        return render_template('pago.html', nombre=nombre, productos=productos, total=total)
    return render_template('metodos_pago.html', tarjetas=tarjetas, productos=productos, total=total)
@app.route('/historial_pedidos')
def historial_pedidos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    pedidos = Pedido.query.filter_by(usuario_id=session['usuario_id']).order_by(Pedido.fecha.desc()).all()
    return render_template('historial_pedidos.html', pedidos=pedidos)
@app.route('/guardar_perfil', methods=['POST'])
def guardar_perfil():
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for('login'))
    usuario = Usuario.query.get(session['usuario_id'])
    if usuario:
        usuario.nombre = request.form['nombre']
        usuario.email = request.form['email']
        nueva_password = request.form.get('password', '').strip()
        if nueva_password:
            usuario.password = nueva_password
        direccion_texto = request.form.get('direccion', '').strip()
        direccion_obj = Direccion.query.filter_by(usuario_id=usuario.id).first()
        if direccion_obj:
            direccion_obj.direccion = direccion_texto
        else:
            if direccion_texto:
                nueva_dir = Direccion(usuario_id=usuario.id, direccion=direccion_texto)
                db.session.add(nueva_dir)
        db.session.commit()
        flash("¡Perfil actualizado correctamente!", "success")
    else:
        flash("No se encontró el usuario.", "error")
    return redirect(url_for('perfil_cliente'))
def obtener_cantidad_carrito(usuario_id):
    cantidad = db.session.query(func.sum(Carrito.cantidad)).filter_by(usuario_id=usuario_id).scalar()
    return cantidad or 0
@app.route('/pedidos_cliente')
def pedidos_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    pedidos = Pedido.query.filter_by(usuario_id=session['usuario_id']).order_by(Pedido.fecha.desc()).all()
    cantidad_carrito = obtener_cantidad_carrito(session['usuario_id'])
    total = sum(pedido.total for pedido in pedidos) if pedidos else 0.00
    return render_template('pedidos_cliente.html', pedidos=pedidos, cantidad_carrito=cantidad_carrito, total=total)
@app.route('/gestion_usuarios')
def gestion_usuarios():
    q = request.args.get('q', '').strip()
    if q:
        usuarios = Usuario.query.filter(
            or_(
                Usuario.nombre.ilike(f"%{q}%"),
                Usuario.email.ilike(f"%{q}%"),
                cast(Usuario.id, String).ilike(f"%{q}%")
            )
        ).all()
    else:
        usuarios = Usuario.query.all()
    return render_template('gestion_usuarios.html', usuarios=usuarios)
@app.route('/eliminar_usuario/<int:user_id>', methods=['POST'])
def eliminar_usuario(user_id):
    usuario = Usuario.query.get(user_id)
    if not usuario:
        flash("⚠️ No se encontró el usuario.", "error")
        return redirect(url_for('gestion_usuarios'))
    try:
        Direccion.query.filter_by(usuario_id=user_id).delete()
        Pedido.query.filter_by(usuario_id=user_id).delete()
        Carrito.query.filter_by(usuario_id=user_id).delete()
        Tarjeta.query.filter_by(usuario_id=user_id).delete()
        db.session.delete(usuario)
        db.session.commit()
        flash("✔️ Usuario eliminado correctamente, junto con sus registros asociados.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar usuario: {str(e)}", "error")
    return redirect(url_for('gestion_usuarios'))
@app.route('/admin_pedidos')
def admin_pedidos():
    q = request.args.get('q', '').strip()
    if q:
        pedidos = Pedido.query.join(Usuario).filter(
            or_(
                cast(Pedido.id, String).ilike(f"%{q}%"),
                Usuario.nombre.ilike(f"%{q}%"),
                Pedido.estado.ilike(f"%{q}%")
            )
        ).all()
    else:
        pedidos = Pedido.query.all()
    return render_template('admin_pedidos.html', pedidos=pedidos)
@app.route('/admin_productos')
def admin_productos():
    q = request.args.get('q', '').strip()
    if q:
        productos = Producto.query.filter(
            or_(
                Producto.nombre.ilike(f"%{q}%"),
                cast(Producto.id, String).ilike(f"%{q}%")
            )
        ).all()
    else:
        productos = Producto.query.all()
    return render_template('admin_productos.html', productos=productos)
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'Productor':
        return redirect(url_for('login'))
    productor_id = session.get('productor_id')
    if not productor_id:
        flash("No se encontrÃ³ el productor asociado a este usuario.", "error")
        return redirect(url_for('admin_productos_productor'))
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = float(request.form['precio'])
    categoria_id = int(request.form['categoria_id'])
    imagen = request.files['imagen']
    filename = None
    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    nuevo_producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        imagen=filename,
        productor_id=productor_id
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    flash("âœ… Â¡Producto subido correctamente!", "success")
    return redirect(url_for('admin_productos_productor'))
@app.route('/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.precio = float(request.form['precio'])
        db.session.commit()
        return redirect(url_for('admin_productos_productor'))
    return render_template('editar_producto.html', producto=producto)
@app.route('/eliminar_carrito/<int:producto_id>', methods=['POST'])
def eliminar_carrito(producto_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    item = Carrito.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Producto eliminado del carrito.", "info")
    else:
        flash("⚠️ El producto no estaba en el carrito.", "warning")
    return redirect(url_for('carrito'))
@app.route('/agregar_carrito/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    if 'usuario_id' not in session:
        flash("⚠️ Debes iniciar sesión para agregar productos al carrito.", "error")
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    producto = Producto.query.get(producto_id)
    if producto:
        item_en_carrito = Carrito.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        if item_en_carrito:
            item_en_carrito.cantidad += 1
        else:
            nuevo_item = Carrito(usuario_id=usuario_id, producto_id=producto_id, cantidad=1)
            db.session.add(nuevo_item)
        try:
            db.session.commit()
            flash(f"✔️ {producto.nombre} agregado al carrito.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error al agregar producto al carrito: {str(e)}", "error")
    return redirect(url_for('productos'))
@app.route('/metodos_pago', methods=['GET', 'POST'])
def metodos_pago():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    tarjetas = Tarjeta.query.filter_by(usuario_id=usuario_id).all()
    return render_template('metodos_pago.html', tarjetas=tarjetas)
@app.route('/detalle_pedido/<int:pedido_id>')
def detalle_pedido(pedido_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    pedido = Pedido.query.get_or_404(pedido_id)
    cantidad_carrito = obtener_cantidad_carrito(session['usuario_id'])
    return render_template('detalle_pedido.html', pedido=pedido, cantidad_carrito=cantidad_carrito)
@app.route('/quitar_carrito/<int:producto_id>', methods=['POST'])
def quitar_carrito(producto_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    item = Carrito.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('carrito'))
@app.route('/marcar_entregado/<int:pedido_id>')
def marcar_entregado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    pedido.estado = "Entregado"
    db.session.commit()
    flash("âœ… Pedido entregado exitosamente.", "success")
    return redirect(url_for('admin_pedidos'))
@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    PedidoItem.query.filter_by(producto_id=producto_id).delete()
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente, junto con sus relaciones en pedidos.', 'success')
    return redirect(url_for('admin_productos_productor'))
@app.route('/actualizar_producto/<int:producto_id>', methods=['GET', 'POST'])
def actualizar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nombre_nuevo = request.form['nombre']
        descripcion_nueva = request.form['descripcion']
        precio_nuevo = float(request.form['precio'])
        categoria_nueva = int(request.form['categoria_id'])
        imagen = request.files['imagen']
        cambios_realizados = (
            producto.nombre != nombre_nuevo or
            producto.descripcion != descripcion_nueva or
            producto.precio != precio_nuevo or
            producto.categoria_id != categoria_nueva or
            (imagen and allowed_file(imagen.filename))
        )
        if cambios_realizados:
            producto.nombre = nombre_nuevo
            producto.descripcion = descripcion_nueva
            producto.precio = precio_nuevo
            producto.categoria_id = categoria_nueva
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                producto.imagen = filename
            db.session.commit()
            flash("✔️ ¡Producto actualizado correctamente!", "success")
        else:
            flash("⚠️ No se detectaron cambios en el producto.", "warning")
        return redirect(url_for('admin_productos_productor'))
    return render_template('actualizar_producto.html', producto=producto, categorias=categorias)

@app.route('/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password, tipo_usuario=tipo_usuario)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario agregado correctamente.", "success")
        return redirect(url_for('gestion_usuarios'))
    return render_template('agregar_usuario.html')
@app.route('/eliminar_pedido/<int:pedido_id>', methods=['POST'])
def eliminar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    PedidoItem.query.filter_by(pedido_id=pedido.id).delete()
    db.session.delete(pedido)
    db.session.commit()
    flash("Pedido eliminado correctamente.", "success")
    return redirect(url_for('admin_pedidos'))
@app.route('/admin/productos/agregar', methods=['GET', 'POST'])
def agregar_producto_admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        imagen = request.files['imagen']
        categoria_id = int(request.form['categoria_id'])
        filename = None
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            imagen=filename,
            categoria_id=categoria_id
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash("Producto agregado correctamente.", "success")
        return redirect(url_for('admin_productos'))
    categorias = Categoria.query.all()
    print(f"DEBUG: Número de categorías encontradas: {len(categorias)}")
    for cat in categorias:
        print(f"DEBUG: Categoría ID={cat.id}, Nombre={cat.nombre}")
    return render_template('agregar_producto_admin.html', categorias=categorias)


@app.route('/actualizar_producto_admin/<int:producto_id>', methods=['GET', 'POST'])
def actualizar_producto_admin(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        imagen = request.files['imagen']
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.imagen = filename
        db.session.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for('admin_productos'))
    return render_template('actualizar_producto_admin.html', producto=producto)
@app.route('/eliminar_producto_admin/<int:producto_id>', methods=['POST'])
def eliminar_producto_admin(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    PedidoItem.query.filter_by(producto_id=producto_id).delete()
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado permanentemente.", "success")
    return redirect(url_for('admin_productos'))

@app.route('/eliminar_tarjeta/<int:tarjeta_id>', methods=['POST'])
def eliminar_tarjeta(tarjeta_id):
    tarjeta = Tarjeta.query.get_or_404(tarjeta_id)
    if tarjeta.usuario_id == session['usuario_id']:
        db.session.delete(tarjeta)
        db.session.commit()
    return redirect(url_for('panel_cliente'))
@app.route('/agregar_tarjeta', methods=['GET', 'POST'])
def agregar_tarjeta():
    if request.method == 'POST':
        numero = request.form['numero_tarjeta']
        propietario = request.form['propietario']
        fecha_expiracion = request.form['fecha_expiracion']
        nueva_tarjeta = Tarjeta(
            usuario_id=session['usuario_id'],
            numero=numero,
            propietario=propietario,
            fecha_expiracion=fecha_expiracion
        )
        db.session.add(nueva_tarjeta)
        db.session.commit()
        return redirect(url_for('panel_cliente'))
    return render_template('agregar_tarjeta.html')
@app.route('/desactivar_producto/<int:producto_id>', methods=['POST'])
def desactivar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.activo = False
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('admin_productos_productor'))
@app.route('/desactivar_producto_admin/<int:producto_id>', methods=['POST'])
def desactivar_producto_admin(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.activo = False
    db.session.commit()
    flash('Producto desactivado correctamente.', 'success')
    return redirect(url_for('admin_productos'))
@app.route('/admin_mensajes')
def admin_mensajes():
    mensajes = Contacto.query.order_by(Contacto.id.desc()).all()
    return render_template('admin_mensajes.html', mensajes=mensajes)
@app.route('/eliminar_mensaje/<int:mensaje_id>', methods=['POST'])
def eliminar_mensaje(mensaje_id):
    mensaje = Contacto.query.get_or_404(mensaje_id)
    db.session.delete(mensaje)
    db.session.commit()
    flash('Mensaje eliminado correctamente.', 'success')
    return redirect(url_for('admin_mensajes'))
@app.route('/responder_mensaje/<int:mensaje_id>', methods=['POST'])
def responder_mensaje(mensaje_id):
    mensaje = Contacto.query.get_or_404(mensaje_id)
    respuesta = request.form.get('respuesta')
    if respuesta:
        mensaje.respuesta = respuesta
        db.session.commit()
        flash('Respuesta enviada correctamente.', 'success')
    else:
        flash('La respuesta no puede estar vacÃ­a.', 'danger')
    return redirect(url_for('admin_mensajes'))
@app.route('/bandeja_mensajes_productor')
def bandeja_mensajes_productor():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'Productor':
        return redirect(url_for('login'))
    mensajes = Contacto.query.filter_by(usuario_id=session['usuario_id']).order_by(Contacto.fecha.desc()).all()
    return render_template('bandeja_mensajes_productor.html', mensajes=mensajes)
@app.route('/enviar_mensaje_productor', methods=['GET', 'POST'])
def enviar_mensaje_productor():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'Productor':
        return redirect(url_for('login'))
    if request.method == 'POST':
        mensaje = request.form.get('mensaje')
        if mensaje:
            nuevo_mensaje = Contacto(usuario_id=session['usuario_id'], mensaje=mensaje)
            db.session.add(nuevo_mensaje)
            db.session.commit()
            flash('Mensaje enviado correctamente.', 'success')
            return redirect(url_for('bandeja_mensajes_productor'))
        else:
            flash('El mensaje no puede estar vacÃ­o.', 'danger')
    return render_template('enviar_mensaje_productor.html')
@app.route('/bandeja_mensajes_cliente')
def bandeja_mensajes_cliente():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'Cliente':
        return redirect(url_for('login'))
    mensajes = Contacto.query.filter_by(usuario_id=session['usuario_id']).order_by(Contacto.fecha.desc()).all()
    return render_template('bandeja_mensajes_cliente.html', mensajes=mensajes)
@app.route('/actualizar_usuario/<int:user_id>', methods=['GET', 'POST'])
def actualizar_usuario(user_id):
    usuario = Usuario.query.get(user_id)
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.email = request.form['email']
        usuario.password = request.form['password']
        usuario.tipo_usuario = request.form['tipo_usuario']
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('gestion_usuarios'))
    return render_template('actualizar_usuario.html', usuario=usuario)

from sms_routes import create_sms_routes
sms_bp = create_sms_routes(db, Usuario, validate_captcha_session, create_captcha_session)
app.register_blueprint(sms_bp)
@app.route('/logout_simple')
def logout_simple():
    session.pop('usuario_id', None)
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    flash('Sesión cerrada correctamente', 'success')
    return response

@app.route('/logout_completo')
def logout_completo():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    flash('Logout completo ejecutado - Datos del navegador limpiados', 'success')
    return response

@app.route('/logout_total')
def logout_total():
    session.clear()
    response = make_response(redirect(url_for('login')))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', expires=0, path='/')
        response.set_cookie(cookie, '', expires=0, path='/', domain=request.host)
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    flash('🧹 Logout total ejecutado - Destrucción completa de sesión', 'success')
    return response

@app.route('/logout_paranoid')
def logout_paranoid():
    session.clear()
    response = make_response(redirect(url_for('login')))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', expires=0, path='/')
        response.set_cookie(cookie, '', expires=0, path='/', domain=request.host)
        response.set_cookie(cookie, '', expires=0, path='/', secure=True, httponly=True)
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    flash('⚡ Logout paranoid ejecutado - Máxima seguridad aplicada', 'success')
    return response

@app.route('/logout_simple_admin')
def logout_simple_admin():
    session.pop('admin_id', None)
    session.pop('usuario_nombre', None)
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    flash('Sesión de administrador cerrada correctamente', 'success')
    return response

@app.route('/logout_completo_admin')
def logout_completo_admin():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    flash('Logout completo ejecutado - Datos del navegador limpiados', 'success')
    return response

@app.route('/logout_total_admin')
def logout_total_admin():
    session.clear()
    response = make_response(redirect(url_for('login')))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', expires=0, path='/')
        response.set_cookie(cookie, '', expires=0, path='/', domain=request.host)
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    flash('🧹 Logout total ejecutado - Destrucción completa de sesión', 'success')
    return response

@app.route('/logout_paranoid_admin')
def logout_paranoid_admin():
    session.clear()
    response = make_response(redirect(url_for('login')))
    for cookie in request.cookies:
        response.set_cookie(cookie, '', expires=0, path='/')
        response.set_cookie(cookie, '', expires=0, path='/', domain=request.host)
        response.set_cookie(cookie, '', expires=0, path='/', secure=True, httponly=True)
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage", "executionContexts"'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    flash('⚡ Logout paranoid ejecutado - Máxima seguridad aplicada', 'success')
    return response

@app.route('/procesar_pago_test', methods=['POST'])
def procesar_pago_test():
    if 'usuario_id' not in session or 'pedido_temp' not in session:
        return redirect(url_for('inicio'))
    
    pedido_data = session['pedido_temp']
    usuario_id = session['usuario_id']
    
    try:
        print("🧪 PROCESANDO PAGO TEST - INICIO")
        start_time = time.time()
        
       
        nuevo_pedido = Pedido(
            usuario_id=usuario_id,
            estado='Confirmado - TEST',
            total=pedido_data['total'],
            fecha=datetime.now(),
            direccion=pedido_data['direccion'],
            nombre=pedido_data['nombre'],
            correo=pedido_data['correo'],
            metodo_pago='MercadoPago TEST',
            payment_id=f"TEST-{int(datetime.now().timestamp())}"
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
      
        for producto_info in pedido_data['productos']:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=producto_info['id'],
                cantidad=producto_info['cantidad']
            )
            db.session.add(pedido_item)
        
       
        Carrito.query.filter_by(usuario_id=usuario_id).delete()
        db.session.commit()
        
        print(f"⚡ Pedido guardado en {(time.time() - start_time)*1000:.0f}ms")
        
       
        enviar_confirmacion_pago(pedido_data['correo'], nuevo_pedido, 'MercadoPago TEST')
        
       
        session.pop('pedido_temp', None)
        
        print(f"✅ Respuesta lista en {(time.time() - start_time)*1000:.0f}ms")
        flash('🧪 ¡Pago TEST procesado exitosamente! Recibirás un correo de confirmación en breve.', 'success')
        return render_template('pago_exitoso.html', pedido=nuevo_pedido)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error procesando pago TEST: {e}")
        flash(f'Error al procesar el pedido: {str(e)}', 'error')
        return redirect(url_for('carrito'))


def check_database_connection():
   
    max_retries = 3
    for attempt in range(max_retries):
        try:
            
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1 as test')).scalar()
            if result == 1:
                return True, f"Database connected (attempt {attempt + 1})"
        except Exception as e:
            print(f"Database connection error (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                try:
                    db.session.rollback()
                    db.session.close()
                except:
                    pass
                import time
                time.sleep(0.5)  # Esperar medio segundo antes del siguiente intento
            else:
                return False, f"Connection failed after {max_retries} attempts: {str(e)}"
    
    return False, "Max retries exceeded"

@app.before_request
def ensure_db_connection():
    
    try:
       
        critical_endpoints = ['login', 'panel_admin', 'productos', 'carrito']
        if request.endpoint in critical_endpoints:
            
            try:
                db.session.execute('SELECT 1').scalar()
            except Exception as db_error:
                print(f"DB issue detected: {str(db_error)}")
                try:
                    db.session.rollback()
                except:
                    pass
    except Exception as e:
        print(f"Error en before_request: {str(e)}")
        pass

@app.route('/test')
def test_simple():
    
    return jsonify({
        'status': 'ok',
        'message': 'La Esquinita funcionando',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/admin-direct', methods=['GET', 'POST'])
def admin_login_direct():
    """Login directo para admin sin CAPTCHA"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        try:
            admin = Administrador.query.filter_by(email=email, password=password).first()
            if admin:
                session['usuario_id'] = admin.id
                session['usuario_nombre'] = admin.nombre
                session['tipo_usuario'] = "Administrador"
                return redirect(url_for('panel_admin'))
            else:
                return "❌ Credenciales incorrectas. Verifique admin@laesquinita.com / admin123"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    
    return '''
    <h2>🔐 Login Admin Directo</h2>
    <form method="POST">
        <p>Email: <input type="email" name="email" value="admin@laesquinita.com" required></p>
        <p>Password: <input type="password" name="password" value="admin123" required></p>
        <p><button type="submit">Entrar</button></p>
    </form>
    '''

@app.route('/health')
def health_check():
    
    try:
        db_connected, db_message = check_database_connection()
        
        status = 'healthy' if db_connected else 'unhealthy'
        status_code = 200 if db_connected else 500
        
        return jsonify({
            'status': status,
            'message': 'La Esquinita API funcionando correctamente' if db_connected else 'Error en base de datos',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if db_connected else 'disconnected',
            'database_message': db_message
        }), status_code
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'Error en el sistema: {str(e)}',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'error'
        }), 500

@app.errorhandler(404)
def page_not_found(error):
    
    return render_template('error_404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    
    try:
        db.session.rollback()
    except Exception as db_error:
        print(f"Error during rollback: {str(db_error)}")
    
   
    print(f"Error 500: {str(error)}")
    
    return render_template('error_500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    
    return render_template('error_404.html'), 403


@app.route('/captcha_diagnostico')
def captcha_diagnostico():
    
    resultados = {
        'etapas': [],
        'modo': app.config.get('ENV'),
        'python_version': sys.version,
    }
    try:
      
        etapa = {'nombre': 'imports', 'ok': True, 'detalle': ''}
        try:
            import PIL
            from PIL import Image, ImageDraw, ImageFont
            etapa['detalle'] = f"Pillow versión: {getattr(PIL, '__version__', 'desconocida')}"
        except Exception as e:
            etapa['ok'] = False
            etapa['detalle'] = f"Error importando PIL: {str(e)}"
        resultados['etapas'].append(etapa)

        
        etapa = {'nombre': 'crear_imagen', 'ok': True, 'detalle': ''}
        try:
            img = Image.new('RGB', (200, 80), color='white')
            etapa['detalle'] = f"Imagen creada tamaño: {img.size} modo: {img.mode}"
        except Exception as e:
            etapa['ok'] = False
            etapa['detalle'] = f"Error creando imagen: {str(e)}"
        resultados['etapas'].append(etapa)

       
        etapa = {'nombre': 'image_draw', 'ok': True, 'detalle': ''}
        try:
            draw = ImageDraw.Draw(img)
            draw.point((10, 10), fill=(255, 0, 0))
            etapa['detalle'] = "ImageDraw operativo"
        except Exception as e:
            etapa['ok'] = False
            etapa['detalle'] = f"Error con ImageDraw: {str(e)}"
        resultados['etapas'].append(etapa)

       
        etapa = {'nombre': 'fuente', 'ok': True, 'detalle': ''}
        fuentes_intentadas = [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        fuente_usada = None
        for ruta in fuentes_intentadas:
            try:
                fuente_usada = ImageFont.truetype(ruta, 36)
                etapa['detalle'] = f"Fuente cargada: {ruta}"
                break
            except Exception:
                continue
        if not fuente_usada:
            try:
                fuente_usada = ImageFont.load_default()
                etapa['detalle'] = "Fuente por defecto usada"
            except Exception as e:
                etapa['ok'] = False
                etapa['detalle'] = f"Error cargando fuente: {str(e)}"
        resultados['etapas'].append(etapa)

        
        etapa = {'nombre': 'dibujar_texto', 'ok': True, 'detalle': ''}
        try:
            codigo = generate_captcha_code()
            draw.text((50, 30), codigo, font=fuente_usada, fill=(0, 0, 0))
            etapa['detalle'] = f"Texto dibujado código: {codigo}"
        except Exception as e:
            etapa['ok'] = False
            etapa['detalle'] = f"Error dibujando texto: {str(e)}"
        resultados['etapas'].append(etapa)

        
        etapa = {'nombre': 'base64', 'ok': True, 'detalle': ''}
        try:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode()
            resultados['data_uri_inicio'] = f"data:image/png;base64,{img_b64[:50]}..."
            etapa['detalle'] = f"Longitud base64: {len(img_b64)}"
        except Exception as e:
            etapa['ok'] = False
            etapa['detalle'] = f"Error convirtiendo a base64: {str(e)}"
        resultados['etapas'].append(etapa)

        resultados['status'] = 'ok' if all(e['ok'] for e in resultados['etapas']) else 'partial'
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


def init_database():
    
    try:
        with app.app_context():
            logger.info("🔧 Inicializando base de datos...")
            
            
            db_connected, db_message = check_database_connection()
            if not db_connected:
                logger.warning(f"❌ Error de conexión a base de datos: {db_message}")
                logger.info("🔄 Intentando crear tablas de todas formas...")
            
            db.create_all()
            crear_admin()
         
            try:
                from sms_verification import SMSCode
                SMSCode(db).create_table()
                logger.info("✅ Tabla sms_codes verificada/creada")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo verificar/crear sms_codes: {e}")
            logger.info("✅ Tablas creadas y administrador registrado 🚀")
            
    except Exception as init_error:
        logger.error(f"⚠️ Error durante inicialización: {str(init_error)}")
        logger.info("🔄 Continuando con el servidor...")


if not app.config.get('TESTING'):
    init_database()

@app.route('/admin/init-categorias-railway-secret-2024')
def init_categorias_railway():
    
    try:
        categorias = ["Elotes", "Esquites", "Patitas", "Maruchan"]
        insertadas = 0
        existentes = 0
        
        for nombre in categorias:
            cat_existe = Categoria.query.filter_by(nombre=nombre).first()
            if not cat_existe:
                nueva_cat = Categoria(nombre=nombre)
                db.session.add(nueva_cat)
                insertadas += 1
            else:
                existentes += 1
        
        db.session.commit()
        
        # Verificar
        todas = Categoria.query.all()
        resultado = {
            "status": "success",
            "insertadas": insertadas,
            "existentes": existentes,
            "total_en_db": len(todas),
            "categorias": [{"id": c.id, "nombre": c.nombre} for c in todas]
        }
        return jsonify(resultado), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin/test-email-config-secret')
def test_email_config():
    """Ruta para probar configuración de email"""
    try:
        config_info = {
            "MAIL_SERVER": app.config.get('MAIL_SERVER'),
            "MAIL_PORT": app.config.get('MAIL_PORT'),
            "MAIL_USE_TLS": app.config.get('MAIL_USE_TLS'),
            "MAIL_USERNAME": app.config.get('MAIL_USERNAME'),
            "MAIL_PASSWORD_SET": "✅ Sí" if app.config.get('MAIL_PASSWORD') else "❌ No",
            "MAIL_PASSWORD_LENGTH": len(app.config.get('MAIL_PASSWORD', ''))
        }
        return jsonify(config_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/send-test-email-secret/<email>')
def send_test_email(email):
    """Enviar correo de prueba"""
    try:
        print(f"🧪 Intentando enviar correo de prueba a {email}")
        
        # Crear datos de prueba
        pedido_data = {
            'id': 999,
            'nombre': 'Usuario de Prueba',
            'correo': email,
            'direccion': 'Dirección de prueba 123',
            'total': 100.00,
            'estado': 'TEST',
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        # Intentar envío síncrono para ver errores
        try:
            subject = f"🧪 TEST - Confirmación de Pedido - La Esquinita"
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #fffdf7; padding: 20px; border-radius: 10px;">
                <h1 style="color: #2e7d32;">🌽 La Esquinita - EMAIL TEST</h1>
                <p>Este es un correo de prueba.</p>
                <p><strong>Pedido #:</strong> {pedido_data['id']}</p>
                <p><strong>Nombre:</strong> {pedido_data['nombre']}</p>
                <p><strong>Total:</strong> ${pedido_data['total']:.2f} MXN</p>
                <p><strong>Fecha:</strong> {pedido_data['fecha']}</p>
                <p>Si recibes este correo, la configuración está correcta ✅</p>
            </div>
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_body,
                sender=app.config['MAIL_USERNAME']
            )
            
            print(f"📧 Configuración SMTP:")
            print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
            print(f"   Username: {app.config['MAIL_USERNAME']}")
            print(f"   TLS: {app.config['MAIL_USE_TLS']}")
            
            mail.send(msg)
            print(f"✅ Correo de prueba enviado exitosamente a {email}")
            
            return jsonify({
                "status": "success",
                "message": f"Correo enviado a {email}",
                "smtp_server": app.config['MAIL_SERVER'],
                "smtp_username": app.config['MAIL_USERNAME']
            }), 200
            
        except Exception as mail_error:
            print(f"❌ Error enviando correo: {str(mail_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(mail_error),
                "type": type(mail_error).__name__
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    try:
        with app.app_context():
            # Verificar conexión a base de datos
            db_connected, db_message = check_database_connection()
            if not db_connected:
                print(f"❌ Error de conexión a base de datos: {db_message}")
                print("🔄 Intentando crear tablas de todas formas...")
            
            db.create_all()
            crear_admin()
            try:
                from sms_verification import SMSCode
                SMSCode(db).create_table()
                print("✅ Tabla sms_codes verificada/creada")
            except Exception as e:
                print(f"⚠️ No se pudo verificar/crear sms_codes: {e}")
            print("✅ Tablas creadas y administrador registrado 🚀")
            
    except Exception as init_error:
        print(f"⚠️ Error durante inicialización: {str(init_error)}")
        print("🔄 Continuando con el servidor...")
    
    app.run(host='0.0.0.0', port=port, debug=False)
    try:
        with app.app_context():
            
            db_connected, db_message = check_database_connection()
            if not db_connected:
                print(f"❌ Error de conexión a base de datos: {db_message}")
                print("🔄 Intentando crear tablas de todas formas...")
            
            db.create_all()
            crear_admin()
            try:
                from sms_verification import SMSCode
                SMSCode(db).create_table()
                print("✅ Tabla sms_codes verificada/creada")
            except Exception as e:
                print(f"⚠️ No se pudo verificar/crear sms_codes: {e}")
            print("✅ Tablas creadas y administrador registrado 🚀")
            
    except Exception as init_error:
        print(f"⚠️ Error durante inicialización: {str(init_error)}")
        print("🔄 Continuando con el servidor...")
    
    app.run(host='0.0.0.0', port=port, debug=False)
