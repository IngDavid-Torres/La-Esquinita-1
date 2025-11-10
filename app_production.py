import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
from werkzeug.utils import secure_filename
import re
from xhtml2pdf import pisa
import io
from flask import send_file
from flask_mail import Mail, Message
from sqlalchemy.sql import exists
from flask_login import login_required, current_user
from sqlalchemy import and_, not_, exists, cast, String, or_
from sqlalchemy.orm import aliased
import pandas as pd
import mercadopago
import time

app = Flask(__name__)

# Configuración de base de datos para producción
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'postgresql://postgres:789@localhost/agroconnect'
app.secret_key = os.environ.get('SECRET_KEY') or 'clave_secreta_super_segura'

db = SQLAlchemy(app)

# Configuración de archivos
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuración MercadoPago
MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN') or "TEST-7916427332588639-102718-00ee5129ad06c2ceba14e4e44b94d22e-191563398"
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'laesquinita.antojitos.mx@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'pnyy wnaj yisq wtgv'

# Inicializar correo
mail = Mail(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ... resto del código igual ...