from captcha_generator import create_captcha_session, validate_captcha_session
import json

@app.route('/generate_captcha')
def generate_captcha():
    try:
        image_data = create_captcha_session(session)
        return json.dumps({
            'success': True,
            'image': image_data
        })
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        captcha_input = request.form.get('captcha')
        
        if not validate_captcha_session(session, captcha_input):
            flash('Código CAPTCHA incorrecto. Inténtalo de nuevo.', 'error')
            return redirect(url_for('login'))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, email, password, tipo_usuario 
                FROM usuario 
                WHERE email = %s AND activo = TRUE
            """, (email,))
            
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario[3], password):
                session['usuario_id'] = usuario[0]
                session['usuario_nombre'] = usuario[1] 
                session['usuario_email'] = usuario[2]
                session['tipo_usuario'] = usuario[4]
                
                flash(f'¡Bienvenido {usuario[1]}!', 'success')
                
                if usuario[4] == 'Administrador':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('inicio'))
            else:
                flash('Email o contraseña incorrectos', 'error')
                
        except Exception as e:
            flash(f'Error en el sistema: {str(e)}', 'error')
        finally:
            if 'conn' in locals():
                conn.close()
    
    if request.method == 'GET':
        create_captcha_session(session)
    
    return render_template('login.html')

@app.route('/validate_captcha', methods=['POST'])
def validate_captcha():
    captcha_input = request.form.get('captcha')
    
    temp_session = session.copy()
    is_valid = validate_captcha_session(temp_session, captcha_input)
    
    return json.dumps({
        'valid': is_valid
    })