from flask import Blueprint, request, session, flash, redirect, url_for, render_template, jsonify
import os
from sqlalchemy import text
from sms_verification import SMSVerification, SMSCode
import json

def create_sms_routes(db, Usuario, validate_captcha_session, create_captcha_session):
    
    
    sms_bp = Blueprint('sms_bp', __name__)
    sms_service = SMSVerification()
    sms_code_manager = SMSCode(db)

    @sms_bp.route('/sms_diagnostico')
    def sms_diagnostico():
        
        try:
            status = {
                'twilio_account_sid_present': bool(sms_service.account_sid),
                'twilio_auth_token_present': bool(sms_service.auth_token),
                'twilio_phone_number_present': bool(sms_service.phone_number),
                'twilio_messaging_service_sid_present': bool(getattr(sms_service, 'messaging_service_sid', None)),
                'using_messaging_service': bool(getattr(sms_service, 'messaging_service_sid', None)),
                'development_mode': sms_service.development_mode,
                'example_generated_code': sms_service.generate_verification_code(),
            }
            return jsonify({'success': True, 'diagnostico': status})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @sms_bp.route('/send_sms_verification', methods=['POST'])
    def send_sms_verification():
        try:
            phone_number = request.form.get('phone_number', '').strip()
            
            if not phone_number:
                return jsonify({
                    'success': False,
                    'message': 'Número de teléfono requerido'
                }), 400
            
            normalized_phone = sms_service.validate_phone_number(phone_number)
            if not normalized_phone:
                return jsonify({
                    'success': False,
                    'message': 'Número de teléfono inválido'
                }), 400
            
            verification_code = sms_service.generate_verification_code()
            
            if sms_code_manager.save_code(normalized_phone, verification_code):
                callback_url = url_for('sms_bp.twilio_status', _external=True)
                sms_result = sms_service.send_verification_sms(normalized_phone, verification_code, callback_url)
                
                if sms_result['success']:
                    return jsonify({
                        'success': True,
                        'message': f'Código enviado a {normalized_phone}',
                        'phone_number': normalized_phone
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'Error al enviar SMS: {sms_result["message"]}'
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error al generar código de verificación'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }), 500

    @sms_bp.route('/verify_sms_code', methods=['POST'])
    def verify_sms_code():
        try:
            phone_number = request.form.get('phone_number', '').strip()
            verification_code = request.form.get('verification_code', '').strip()
            
            if not phone_number or not verification_code:
                return jsonify({
                    'success': False,
                    'message': 'Número de teléfono y código requeridos'
                }), 400
                
            normalized_phone = sms_service.validate_phone_number(phone_number)
            if not normalized_phone:
                return jsonify({
                    'success': False,
                    'message': 'Número de teléfono inválido'
                }), 400
            
            verification_result = sms_code_manager.verify_code(normalized_phone, verification_code)
            
            if verification_result['success']:
                if 'usuario_id' in session:
                    usuario = Usuario.query.get(session['usuario_id'])
                    if usuario:
                        usuario.telefono = normalized_phone
                        usuario.telefono_verificado = True
                        db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Código verificado correctamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': verification_result['message']
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error interno: {str(e)}'
            }), 500

    @sms_bp.route('/registro_sms', methods=['GET', 'POST'])
    def registro_sms():
        if request.method == 'GET':
            return render_template('registro_sms.html', step=1)
        
        try:
            nombre = request.form.get('nombre', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            telefono = request.form.get('telefono', '').strip()
            verification_code = request.form.get('verification_code', '').strip()
            step = request.form.get('step', '1')
            
            if step == '1':
                if Usuario.query.filter_by(email=email).first():
                    flash('El email ya está registrado', 'error')
                    return render_template('registro_sms.html', step=1)
                
                if not all([nombre, email, password, telefono]):
                    flash('Todos los campos son obligatorios', 'error')
                    return render_template('registro_sms.html', step=1)
                
                session['registro_temp'] = {
                    'nombre': nombre,
                    'email': email,
                    'password': password,
                    'telefono': telefono,
                    'tipo_usuario': 'Cliente'
                }
                
                normalized_phone = sms_service.validate_phone_number(telefono)
                if not normalized_phone:
                    flash('Número de teléfono inválido', 'error')
                    return render_template('registro_sms.html', step=1)
                
                verification_code = sms_service.generate_verification_code()
                callback_url = url_for('sms_bp.twilio_status', _external=True)
                sms_result = sms_service.send_verification_sms(normalized_phone, verification_code, callback_url)
                
                if sms_result['success']:
                    sms_code_manager.save_code(normalized_phone, verification_code)
                    session['phone_for_verification'] = normalized_phone
                    flash(f'Código enviado a {normalized_phone}', 'info')
                    return render_template('registro_sms.html', step=2, phone=normalized_phone)
                else:
                    error_msg = sms_result.get('message', 'Error desconocido al enviar SMS')
                    flash(f'Error al enviar SMS: {error_msg}', 'error')
                    return render_template('registro_sms.html', step=1)
            
            elif step == '2':
                phone_number = session.get('phone_for_verification')
                if not phone_number:
                    flash('Sesión expirada, intenta nuevamente', 'error')
                    return redirect(url_for('sms_bp.registro_sms'))
                
                verification_result = sms_code_manager.verify_code(phone_number, verification_code)
                
                if verification_result['success']:
                    registro_data = session.get('registro_temp', {})
                    if registro_data:
                        try:
                            nuevo_usuario = Usuario(
                                nombre=registro_data['nombre'],
                                email=registro_data['email'],
                                password=registro_data['password'],
                                tipo_usuario=registro_data['tipo_usuario'],
                                telefono=phone_number,
                                telefono_verificado=True
                            )
                            
                            db.session.add(nuevo_usuario)
                            db.session.commit()
                            
                            session.pop('registro_temp', None)
                            session.pop('phone_for_verification', None)
                            
                            
                            return render_template('registro_sms.html', step=3, 
                                                 nombre=nuevo_usuario.nombre, 
                                                 email=nuevo_usuario.email)
                            
                        except Exception as e:
                            db.session.rollback()
                            flash(f'Error al crear usuario: {str(e)}', 'error')
                            return render_template('registro_sms.html', step=2, phone=phone_number)
                    else:
                        flash('Datos de registro no encontrados', 'error')
                        return redirect(url_for('sms_bp.registro_sms'))
                else:
                    flash(verification_result['message'], 'error')
                    return render_template('registro_sms.html', step=2, phone=phone_number)
            
        except Exception as e:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('registro_sms.html', step=1)
        
        
        return render_template('registro_sms.html', step=1)

    @sms_bp.route('/login_sms', methods=['GET', 'POST'])
    def login_sms():
        if request.method == 'GET':
            create_captcha_session(session)
            return render_template('login_sms.html', step=1)
        
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            captcha_input = request.form.get('captcha', '').strip()
            verification_code = request.form.get('verification_code', '').strip()
            step = request.form.get('step', '1')
            
            if step == '1':
                if not validate_captcha_session(session, captcha_input):
                    flash('CAPTCHA incorrecto', 'error')
                    create_captcha_session(session)
                    return render_template('login_sms.html')
                
                usuario = Usuario.query.filter_by(email=email, password=password).first()
                if not usuario:
                    flash('Credenciales incorrectas', 'error')
                    create_captcha_session(session)
                    return render_template('login_sms.html')
                
                if not usuario.telefono:
                    flash('Este usuario no tiene teléfono registrado. Usa el login normal.', 'error')
                    return redirect(url_for('login'))
                
                verification_code = sms_service.generate_verification_code()
                callback_url = url_for('sms_bp.twilio_status', _external=True)
                sms_result = sms_service.send_verification_sms(usuario.telefono, verification_code, callback_url)
                
                if sms_result['success']:
                    sms_code_manager.save_code(usuario.telefono, verification_code)
                    session['login_temp'] = {
                        'usuario_id': usuario.id,
                        'phone': usuario.telefono
                    }
                    flash(f'Código enviado a {usuario.telefono}', 'info')
                    return render_template('login_sms.html', step=2, phone=usuario.telefono)
                else:
                    flash(f'Error al enviar SMS: {sms_result["message"]}', 'error')
                    return render_template('login_sms.html', step=1)
            
            elif step == '2':
                login_data = session.get('login_temp')
                if not login_data:
                    flash('Sesión expirada, intenta nuevamente', 'error')
                    return redirect(url_for('sms_bp.login_sms'))
                
                phone_number = login_data['phone']
                verification_result = sms_code_manager.verify_code(phone_number, verification_code)
                
                if verification_result['success']:
                    usuario = Usuario.query.get(login_data['usuario_id'])
                    if usuario:
                        session['usuario_id'] = usuario.id
                        session['usuario_tipo'] = usuario.tipo_usuario
                        session.pop('login_temp', None)
                        
                        if usuario.tipo_usuario == 'Administrador':
                            return redirect(url_for('admin_productos'))
                        else:
                            return redirect(url_for('productos'))
                    else:
                        flash('Usuario no encontrado', 'error')
                        return redirect(url_for('sms_bp.login_sms'))
                else:
                    flash(verification_result['message'], 'error')
                    return render_template('login_sms.html', step=2, phone=phone_number)
            
        except Exception as e:
            flash(f'Error interno: {str(e)}', 'error')
            create_captcha_session(session)
            return render_template('login_sms.html', step=1)

    @sms_bp.route('/twilio_status', methods=['POST'])
    def twilio_status():
        try:
            data = request.form.to_dict()
            # Log minimal delivery info; avoid sensitive data leakage
            print(f"[Twilio Status] sid={data.get('MessageSid')} status={data.get('MessageStatus')} to={data.get('To')} error={data.get('ErrorCode')}")
            return ('', 204)
        except Exception as e:
            print(f"[Twilio Status ERROR] {e}")
            return ('', 204)

    @sms_bp.route('/sms_last_code')
    def sms_last_code():
        # Debug-only endpoint: returns last code for a phone if explicitly enabled
        if not os.environ.get('SMS_DEBUG_SHOW_CODE', '').lower() in ('1', 'true', 'yes'):
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        phone = request.args.get('phone', '').strip()
        if not phone:
            return jsonify({'success': False, 'message': 'Parámetro phone requerido'}), 400
        try:
            normalized = sms_service.validate_phone_number(phone)
            if not normalized:
                return jsonify({'success': False, 'message': 'Número inválido'}), 400
            
            if getattr(sms_code_manager, 'development_mode', False):
                stored = sms_code_manager.temp_codes.get(normalized)
                if stored:
                    return jsonify({'success': True, 'data': {
                        'phone': normalized,
                        'code': stored.get('code'),
                        'used': stored.get('used'),
                        'attempts': stored.get('attempts')
                    }})
            with db.engine.begin() as conn:
                row = conn.execute(
                    text("""
                        SELECT code, created_at, expires_at, used, attempts
                        FROM sms_codes
                        WHERE phone_number = :pn
                        ORDER BY created_at DESC
                        LIMIT 1
                    """),
                    {'pn': normalized}
                ).fetchone()
            if not row:
                return jsonify({'success': False, 'message': 'Sin registros'}), 404
            m = getattr(row, '_mapping', None)
            payload = {
                'phone': normalized,
                'code': (m['code'] if m else row[0]),
                'used': (m['used'] if m else row[3]),
                'attempts': (m['attempts'] if m else row[4])
            }
            return jsonify({'success': True, 'data': payload})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    return sms_bp