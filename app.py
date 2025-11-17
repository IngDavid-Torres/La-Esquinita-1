from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from datetime import datetime
import os
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
from dotenv import load_dotenv
load_dotenv()

def add_security_headers(response):
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'postgresql://postgres:789@localhost/laesquinita'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'connect_timeout': 10,
        'application_name': 'la_esquinita_app'
    }
}
app.secret_key = os.environ.get('SECRET_KEY') or 'clave_secreta_super_segura'

db = SQLAlchemy(app)
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN') or "TEST-7916427332588639-102718-00ee5129ad06c2ceba14e4e44b94d22e-191563398"
MP_PUBLIC_KEY = os.environ.get('MP_PUBLIC_KEY') or "TEST-c1e625f3-6498-4c5e-9fda-d2b6b5a0a7de-191563398"
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'laesquinita.antojitos.mx@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'pnyy wnaj yisq wtgv'
mail = Mail(app)
def enviar_confirmacion_pago(correo_destino, pedido, metodo_pago):
    try:
        subject = f"ðŸŒ½ ConfirmaciÃ³n de Pedido #{pedido.id} - La Esquinita"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #fffdf7; padding: 20px; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2e7d32; margin-bottom: 10px;">ðŸŒ½ La Esquinita</h1>
                <h2 style="color: #ff5722;">Â¡Pago Confirmado!</h2>
            </div>
            <div style="background: #f1f8e9; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #2e7d32; margin-top: 0;">ðŸ“‹ Detalles del Pedido</h3>
                <p><strong>Pedido #:</strong> {pedido.id}</p>
                <p><strong>Nombre:</strong> {pedido.nombre}</p>
                <p><strong>Correo:</strong> {pedido.correo}</p>
                <p><strong>DirecciÃ³n:</strong> {pedido.direccion}</p>
                <p><strong>Total:</strong> ${pedido.total:.2f} MXN</p>
                <p><strong>MÃ©todo de Pago:</strong> {metodo_pago}</p>
                <p><strong>Estado:</strong> <span style="color: #4caf50; font-weight: bold;">{pedido.estado}</span></p>
                <p><strong>Fecha:</strong> {pedido.fecha.strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #ff5722; margin-top: 0;">ðŸšš Â¿QuÃ© sigue?</h4>
                <p>â€¢ Tu pedido estÃ¡ siendo preparado con amor ðŸŒ½</p>
                <p>â€¢ Tiempo estimado de entrega: 30-45 minutos</p>
                <p>â€¢ Te contactaremos si necesitamos algo adicional</p>
            </div>
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #666;">Â¡Gracias por elegir La Esquinita!</p>
                <p style="color: #2e7d32; font-weight: bold;">El autÃ©ntico sabor mexicano ðŸ‡²ðŸ‡½</p>
            </div>
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #888;">
                    Este correo fue enviado automÃ¡ticamente desde La Esquinita<br>
                    MÃ©todo de pago: {metodo_pago}
                </p>
            </div>
        </div>
        """
        msg = Message(
            subject=subject,
            recipients=[correo_destino],
            html=html_body,
            sender=app.config['MAIL_USERNAME']
        )
        mail.send(msg)
        print(f"âœ… Correo de confirmaciÃ³n enviado a {correo_destino}")
        return True
    except Exception as e:
        print(f"âŒ Error enviando correo: {str(e)}")
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
        
        
        if Categoria.query.count() == 0:
            categorias = [
                Categoria(nombre="Elotes y Esquites"),
                Categoria(nombre="Patitas"),
                Categoria(nombre="Maruchan"),
                Categoria(nombre="Bebidas")
            ]
            for categoria in categorias:
                db.session.add(categoria)
            db.session.commit()
            print("✅ Categorías básicas creadas")
        
       
        if Producto.query.count() == 0:
            productos_ejemplo = [
                Producto(nombre="Elote con mayonesa", descripcion="Delicioso elote con mayonesa, chile y queso", precio=25.0, imagen="elote1.jpg", categoria_id=1, activo=True),
                Producto(nombre="Esquites en vaso", descripcion="Esquites tradicionales servidos en vaso", precio=20.0, imagen="esquite.png", categoria_id=1, activo=True),
                Producto(nombre="Patitas en escabeche", descripcion="Patitas de cerdo en delicioso escabeche", precio=35.0, imagen="patitas.jpeg", categoria_id=2, activo=True),
                Producto(nombre="Maruchan preparada", descripcion="Sopa maruchan con ingredientes adicionales", precio=30.0, imagen="Maruchaesquite.png", categoria_id=3, activo=True)
            ]
            for producto in productos_ejemplo:
                db.session.add(producto)
            db.session.commit()
            print("✅ Productos de ejemplo creados")

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
            flash("La contraseÃ±a debe tener al menos 8 caracteres, una mayÃºscula, una minÃºscula y un carÃ¡cter especial.", "error")
            return redirect(url_for('registro'))
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password, tipo_usuario=tipo_usuario)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso. Ahora puedes iniciar sesiÃ³n.", "success")
        return redirect(url_for('login'))
    tipo_usuario = request.args.get('tipo', 'Cliente')
    return render_template('registro.html', tipo_usuario=tipo_usuario)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not email or not password:
                flash('Por favor completa todos los campos', 'error')
                return render_template('login.html')
            
            # Verificar admin primero
            admin = Administrador.query.filter_by(email=email, password=password).first()
            if admin:
                session['usuario_id'] = admin.id
                session['usuario_nombre'] = admin.nombre
                session['tipo_usuario'] = "Administrador"
                flash(f'Bienvenido Administrador {admin.nombre}', 'success')
                return redirect(url_for('panel_admin'))
            
            # Verificar usuario
            usuario = Usuario.query.filter_by(email=email, password=password).first()
            if usuario:
                session['usuario_id'] = usuario.id
                session['usuario_nombre'] = usuario.nombre
                session['tipo_usuario'] = usuario.tipo_usuario
                flash(f'Bienvenido {usuario.nombre}', 'success')
                if usuario.tipo_usuario == "Cliente":
                    return redirect(url_for('panel_cliente'))
                elif usuario.tipo_usuario == "Productor":
                    return redirect(url_for('panel_productor'))
            
            flash('Credenciales incorrectas', 'error')
            return render_template('login.html')
            
        except Exception as e:
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
    flash(f'SesiÃ³n de administrador cerrada completamente. Â¡Hasta pronto, {admin_name}! ðŸ”', 'success')
    return response
@app.route('/logout/cliente')
def logout_cliente():
    if session.get('tipo_usuario') != 'Cliente':
        flash('Acceso denegado. Solo clientes pueden usar esta funciÃ³n.', 'error')
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
    flash(f'SesiÃ³n de cliente cerrada completamente. Â¡Hasta pronto, {client_name}! ðŸ›’', 'success')
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
    flash(f'DestrucciÃ³n total de sesiÃ³n completada. Todos los datos eliminados. Â¡Hasta pronto, {user_data["name"]}! ðŸ’¥', 'warning')
    return response
@app.route('/keep-alive', methods=['POST'])
def keep_alive():
    if 'usuario_id' in session:
        session.permanent = True
        return {'status': 'success', 'message': 'SesiÃ³n renovada'}, 200
    return {'status': 'error', 'message': 'No hay sesiÃ³n activa'}, 401
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
        flash("Tu carrito estÃ¡ vacÃ­o", "error")
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
            print(f"ðŸ”§ DEBUG: Creando preferencia con datos: {preference_data}")
            preference_response = sdk.preference().create(preference_data)
            print(f"ðŸ”§ DEBUG: Respuesta de MercadoPago: {preference_response}")
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
        print(f"ðŸ”§ DEBUG: Procesando pago exitoso para usuario {usuario_id}")
        print(f"ðŸ”§ DEBUG: Datos del pedido: {pedido_data}")
        carrito_antes = Carrito.query.filter_by(usuario_id=usuario_id).all()
        print(f"ðŸ”§ DEBUG: Items en carrito ANTES: {len(carrito_antes)}")
        nuevo_pedido = Pedido(
            usuario_id=usuario_id,
            estado='Confirmado',
            total=pedido_data['total'],
            fecha=datetime.now(),
            direccion=pedido_data['direccion']
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        print(f"ðŸ”§ DEBUG: Pedido creado con ID: {nuevo_pedido.id}")
        for producto_info in pedido_data['productos']:
            pedido_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=producto_info['id'],
                cantidad=producto_info['cantidad']
            )
            db.session.add(pedido_item)
            print(f"ðŸ”§ DEBUG: Agregado item: Producto {producto_info['id']}, Cantidad {producto_info['cantidad']}")
        print(f"ðŸ”§ DEBUG: Limpiando carrito para usuario {usuario_id}")
        items_eliminados = Carrito.query.filter_by(usuario_id=usuario_id).delete()
        print(f"ðŸ”§ DEBUG: Items eliminados del carrito: {items_eliminados}")
        db.session.commit()
        print(f"ðŸ”§ DEBUG: TransacciÃ³n confirmada en base de datos")
        carrito_despues = Carrito.query.filter_by(usuario_id=usuario_id).all()
        print(f"ðŸ”§ DEBUG: Items en carrito DESPUÃ‰S: {len(carrito_despues)}")
        try:
            enviar_confirmacion_pago(pedido_data['correo'], nuevo_pedido, 'MercadoPago')
        except Exception as email_error:
            print(f"âŒ Error enviando email de confirmaciÃ³n: {email_error}")
        session.pop('pedido_temp', None)
        print(f"ðŸ”§ DEBUG: Datos temporales limpiados")
        flash('Â¡Pago procesado exitosamente!', 'success')
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
            'ConfirmaciÃ³n de Pedido - La Esquinita',
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
                <p>Â¡Gracias por tu compra! Tu pedido ha sido confirmado y pronto comenzaremos a prepararlo.</p>
                <div style="background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 8px;">
                    <h3>ðŸ“‹ Detalles del pedido</h3>
                    <p><strong>NÃºmero de pedido:</strong> #{pedido.id}</p>
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
        nuevo_pedido = Pedido(usuario_id=usuario_id, total=total, estado="Pendiente")
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
            productos_detalle = ""
            for producto in productos:
                productos_detalle += f"- {producto.nombre} x{producto.cantidad} = ${producto.precio * producto.cantidad:.2f}\n"
            msg = Message(
                'ConfirmaciÃ³n de compra - La Esquinita',
                sender='laesquinita.antojitos.mx@gmail.com',
                recipients=[correo]
            )
            msg.body = (
                f"Hola {nombre},\n\n"
                f"Tu pago se realizÃ³ con Ã©xito. Tu pedido serÃ¡ enviado a:\n{direccion}\n\n"
                f"Detalle de tu compra:\n"
                f"{productos_detalle}\n"
                f"Total pagado: ${total:.2f}\n\n"
                f"Â¡Gracias por comprar en La Esquinita!"
            )
            mail.send(msg)
        except Exception as e:
            print("No se pudo enviar el correo:", e)
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
        flash("Debes iniciar sesiÃ³n.", "error")
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
        flash("Â¡Perfil actualizado correctamente!", "success")
    else:
        flash("No se encontrÃ³ el usuario.", "error")
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
        flash("âš ï¸ No se encontrÃ³ el usuario.", "error")
        return redirect(url_for('gestion_usuarios'))
    try:
        Direccion.query.filter_by(usuario_id=user_id).delete()
        Pedido.query.filter_by(usuario_id=user_id).delete()
        Carrito.query.filter_by(usuario_id=user_id).delete()
        Tarjeta.query.filter_by(usuario_id=user_id).delete()
        db.session.delete(usuario)
        db.session.commit()
        flash("âœ… Usuario eliminado correctamente, junto con sus registros asociados.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"âŒ Error al eliminar usuario: {str(e)}", "error")
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
        flash("âŒ Producto eliminado del carrito.", "info")
    else:
        flash("âš ï¸ El producto no estaba en el carrito.", "warning")
    return redirect(url_for('carrito'))
@app.route('/agregar_carrito/<int:producto_id>', methods=['POST'])
def agregar_carrito(producto_id):
    if 'usuario_id' not in session:
        flash("âš ï¸ Debes iniciar sesiÃ³n para agregar productos al carrito.", "error")
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
            flash(f"âœ… {producto.nombre} agregado al carrito.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"âŒ Error al agregar producto al carrito: {str(e)}", "error")
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
            flash("âœ… Â¡Producto actualizado correctamente!", "success")
        else:
            flash("âš ï¸ No se detectaron cambios en el producto.", "warning")
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
def validate_captcha_session(session, captcha_input):
    return True
def create_captcha_session(session):
    pass
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
        print("🧪 PROCESANDO PAGO TEST")
        
       
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
        
       
        try:
            enviar_confirmacion_pago(pedido_data['correo'], nuevo_pedido, 'MercadoPago TEST')
            print("✅ Correo de confirmación enviado")
        except Exception as email_error:
            print(f"⚠️ Error enviando email: {email_error}")
        
        
        session.pop('pedido_temp', None)
        
        flash('🧪 ¡Pago TEST procesado exitosamente! Revisa tu correo.', 'success')
        return render_template('pago_exitoso.html', pedido=nuevo_pedido)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error procesando pago TEST: {e}")
        flash(f'Error al procesar el pedido: {str(e)}', 'error')
        return redirect(url_for('carrito'))


def check_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        result = db.session.execute('SELECT 1').fetchone()
        return True, "Database connected"
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False, str(e)

@app.before_request
def ensure_db_connection():
    """Verificar conexión antes de cada request"""
    try:
        if request.endpoint not in ['health_check', 'static']:
            db_connected, _ = check_database_connection()
            if not db_connected:
                # Intentar reconectar
                try:
                    db.session.close()
                    db.session.remove()
                except:
                    pass
    except Exception as e:
        print(f"Error en before_request: {str(e)}")
        pass

@app.route('/test')
def test_simple():
    """Ruta simple para probar que la aplicación funciona"""
    return jsonify({
        'status': 'ok',
        'message': 'La Esquinita funcionando',
        'timestamp': datetime.utcnow().isoformat()
    })

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
    """Manejador personalizado para errores 404"""
    return render_template('error_404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Manejador personalizado para errores 500"""
    try:
        db.session.rollback()
    except Exception as db_error:
        print(f"Error during rollback: {str(db_error)}")
    
    # Log del error para debugging
    print(f"Error 500: {str(error)}")
    
    return render_template('error_500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Manejador personalizado para errores 403"""
    return render_template('error_404.html'), 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    try:
        with app.app_context():
            
            db_connected, db_message = check_database_connection()
            if not db_connected:
                print(f"❌ Error de conexión a base de datos: {db_message}")
                print("🔄 Intentando crear tablas de todas formas...")
            
            db.create_all()
            crear_admin()
            print("✅ Tablas creadas y administrador registrado 🚀")
            
    except Exception as init_error:
        print(f"⚠️ Error durante inicialización: {str(init_error)}")
        print("🔄 Continuando con el servidor...")
    
    app.run(host='0.0.0.0', port=port, debug=False)
