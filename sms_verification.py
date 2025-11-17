from twilio.rest import Client
import random
import string
from datetime import datetime, timedelta
import os

class SMSVerification:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'tu_account_sid'
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN') or 'tu_auth_token'
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER') or '+1234567890'
        self.development_mode = self.account_sid == 'tu_account_sid' or not self.account_sid
        
        if not self.development_mode:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
        
    def generate_verification_code(self, length=6):
        if self.development_mode:
            return '123456'
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_sms(self, phone_number, code):
        try:
            is_dev_credentials = (
                not self.account_sid or 
                self.account_sid == 'tu_account_sid_aqui' or
                not self.auth_token or 
                self.auth_token == 'tu_auth_token_aqui'
            )
            
            if self.development_mode or is_dev_credentials:
                print(f"""
🌽 [MODO DESARROLLO] La Esquinita - SMS Simulado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Para: {phone_number}
🔐 Código: {code}
💡 Para pruebas usa: 123456
⏰ Expira en 10 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                return {
                    'success': True,
                    'message_sid': f'dev_message_{code}',
                    'message': f'Código enviado a {phone_number}'
                }
            
            message_body = f"""🌽 La Esquinita - Código de Verificación

Tu código de verificación es: {code}

Este código expira en 10 minutos.
No compartas este código con nadie.

¡Gracias por elegir La Esquinita!"""
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=phone_number
            )
            
            return {
                'success': True,
                'message_sid': message.sid,
                'message': 'SMS enviado correctamente'
            }
            
        except Exception as e:
            print(f"[ERROR] Error al enviar SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error al enviar SMS: {str(e)}'
            }
    
    def validate_phone_number(self, phone_number):
        import re
        
        clean_number = re.sub(r'[^\d+]', '', phone_number)
        
        patterns = [
            r'^\+52\d{10}$',
            r'^52\d{10}$',
            r'^\d{10}$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, clean_number):
                if clean_number.startswith('+52'):
                    return clean_number
                elif clean_number.startswith('52'):
                    return '+' + clean_number
                else:
                    return '+52' + clean_number
        
        return None

class SMSCode:
    def __init__(self, db):
        self.db = db
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID') or 'tu_account_sid'
        self.development_mode = account_sid == 'tu_account_sid'
        self.temp_codes = {}
        self.create_table()
    
    def create_table(self):
        try:
            with self.db.engine.connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sms_codes (
                        id SERIAL PRIMARY KEY,
                        phone_number VARCHAR(20) NOT NULL,
                        code VARCHAR(10) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        attempts INT DEFAULT 0
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Error creando tabla sms_codes: {e}")
    
    def save_code(self, phone_number, code, expires_in_minutes=10):
        try:
            if self.development_mode:
                expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
                self.temp_codes[phone_number] = {
                    'code': code,
                    'expires_at': expires_at,
                    'used': False,
                    'attempts': 0
                }
                print(f"DEBUG: Código guardado en memoria: {phone_number} -> {code}")
                return True
            
            expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
            
            with self.db.engine.connect() as conn:
                conn.execute("""
                    UPDATE sms_codes 
                    SET used = TRUE 
                    WHERE phone_number = %s AND used = FALSE
                """, (phone_number,))
                
                conn.execute("""
                    INSERT INTO sms_codes (phone_number, code, expires_at)
                    VALUES (%s, %s, %s)
                """, (phone_number, code, expires_at))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error guardando código SMS: {e}")
            return False
    
    def verify_code(self, phone_number, input_code):
        try:
            if self.development_mode:
                print(f"DEBUG: Verificando código '{input_code}' para '{phone_number}'")
                
                if input_code == '123456':
                    print("DEBUG: Código de desarrollo aceptado")
                    return {'success': True, 'message': 'Código de desarrollo verificado correctamente'}
                
                if phone_number in self.temp_codes:
                    stored_data = self.temp_codes[phone_number]
                    if not stored_data['used'] and datetime.now() < stored_data['expires_at']:
                        if input_code == stored_data['code']:
                            stored_data['used'] = True
                            return {'success': True, 'message': 'Código verificado correctamente'}
                        else:
                            stored_data['attempts'] += 1
                            if stored_data['attempts'] >= 3:
                                stored_data['used'] = True
                                return {'success': False, 'message': 'Demasiados intentos. Solicita un nuevo código'}
                            remaining = 3 - stored_data['attempts']
                            return {'success': False, 'message': f'Código incorrecto. Te quedan {remaining} intentos'}
                
                return {'success': False, 'message': 'Código expirado o no válido'}
            
            with self.db.engine.connect() as conn:
                result = conn.execute("""
                    SELECT id, code, expires_at, attempts
                    FROM sms_codes 
                    WHERE phone_number = %s 
                    AND used = FALSE 
                    AND expires_at > CURRENT_TIMESTAMP
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (phone_number,)).fetchone()
                
                if not result:
                    return {'success': False, 'message': 'Código expirado o no válido'}
                
                code_id, stored_code, expires_at, attempts = result
                
                conn.execute("""
                    UPDATE sms_codes 
                    SET attempts = attempts + 1 
                    WHERE id = %s
                """, (code_id,))
                
                if attempts >= 3:
                    conn.execute("""
                        UPDATE sms_codes 
                        SET used = TRUE 
                        WHERE id = %s
                    """, (code_id,))
                    conn.commit()
                    return {'success': False, 'message': 'Demasiados intentos. Solicita un nuevo código'}
                
                is_valid_code = (
                    input_code == stored_code or 
                    (self.development_mode and input_code == '123456')
                )
                
                if is_valid_code:
                    conn.execute("""
                        UPDATE sms_codes 
                        SET used = TRUE 
                        WHERE id = %s
                    """, (code_id,))
                    conn.commit()
                    
                    if input_code == '123456':
                        return {'success': True, 'message': 'Código de desarrollo verificado correctamente'}
                    else:
                        return {'success': True, 'message': 'Código verificado correctamente'}
                else:
                    conn.commit()
                    remaining_attempts = 3 - (attempts + 1)
                    return {
                        'success': False, 
                        'message': f'Código incorrecto. Te quedan {remaining_attempts} intentos'
                    }
                    
        except Exception as e:
            print(f"Error verificando código SMS: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}