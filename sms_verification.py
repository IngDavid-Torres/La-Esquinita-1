from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random
import string
from datetime import datetime, timedelta
import os
from sqlalchemy import text

class SMSVerification:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        
        self.development_mode = not self.account_sid or not self.auth_token or not self.phone_number
        
        
        print(f"""
🔍 [TWILIO CONFIG] Estado de Configuración:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 ACCOUNT_SID: {'✅ Configurado' if self.account_sid else '❌ NO configurado'}
📌 AUTH_TOKEN: {'✅ Configurado' if self.auth_token else '❌ NO configurado'}
📌 PHONE_NUMBER: {'✅ Configurado (' + self.phone_number + ')' if self.phone_number else '❌ NO configurado'}
📌 Modo: {'🔧 DESARROLLO' if self.development_mode else '🚀 PRODUCCIÓN (Twilio Real)'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        if not self.development_mode:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("[✅] Cliente Twilio inicializado correctamente")
            except Exception as e:
                print(f"[❌ ERROR] Error al inicializar Twilio Client: {str(e)}")
                self.development_mode = True
                self.client = None
        else:
            self.client = None
            print("[⚠️] Usando modo DESARROLLO - Los SMS no se enviarán realmente")
        
    def generate_verification_code(self, length=6):
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_sms(self, phone_number, code):
        try:
            if self.development_mode:
                print(f"""
🌽 [MODO DESARROLLO] La Esquinita - SMS Simulado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Para: {phone_number}
🔐 Código: {code}
⚠️ NOTA: Configura las variables de entorno de Twilio para envío real
⏰ Expira en 10 minutos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                return {
                    'success': True,
                    'message_sid': f'dev_message_{code}',
                    'message': f'Código enviado a {phone_number} (modo desarrollo)'
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
            
        except TwilioRestException as e:
            print(f"[TWILIO ERROR] status={getattr(e, 'status', None)} code={getattr(e, 'code', None)} msg={str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Twilio error (code {getattr(e, "code", "?")}) {str(e)}'
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
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')  
        self.development_mode = not self.account_sid  
        self.temp_codes = {}
        self.create_table()
    
    def create_table(self):
        try:
            ddl = text("""
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
            with self.db.engine.begin() as conn:
                conn.execute(ddl)
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
            with self.db.engine.begin() as conn:
                conn.execute(
                    text("UPDATE sms_codes SET used = TRUE WHERE phone_number = :pn AND used = FALSE"),
                    {"pn": phone_number}
                )
                conn.execute(
                    text("INSERT INTO sms_codes (phone_number, code, expires_at) VALUES (:pn, :code, :exp)") ,
                    {"pn": phone_number, "code": code, "exp": expires_at}
                )
                return True
                
        except Exception as e:
            print(f"Error guardando código SMS: {e}")
            return False
    
    def verify_code(self, phone_number, input_code):
        try:
            if self.development_mode:
                print(f"DEBUG (DEV MODE): Verificando código '{input_code}' para '{phone_number}'")
                
                if phone_number in self.temp_codes:
                    stored = self.temp_codes[phone_number]
                    if not stored['used'] and datetime.now() < stored['expires_at']:
                        if input_code == stored['code']:
                            stored['used'] = True
                            return {'success': True, 'message': 'Código verificado correctamente (dev)'}
                        else:
                            stored['attempts'] += 1
                            if stored['attempts'] >= 3:
                                stored['used'] = True
                                return {'success': False, 'message': 'Demasiados intentos. Solicita un nuevo código'}
                            remaining = 3 - stored['attempts']
                            return {'success': False, 'message': f'Código incorrecto. Te quedan {remaining} intentos'}
                return {'success': False, 'message': 'Código expirado o no válido'}
            
            with self.db.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, code, expires_at, attempts
                        FROM sms_codes 
                        WHERE phone_number = :pn 
                        AND used = FALSE 
                        AND expires_at > CURRENT_TIMESTAMP
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """),
                    {"pn": phone_number}
                ).fetchone()
                
                if not result:
                    return {'success': False, 'message': 'Código expirado o no válido'}
                
                code_id, stored_code, expires_at, attempts = result
                
                conn.execute(text("UPDATE sms_codes SET attempts = attempts + 1 WHERE id = :id"), {"id": code_id})
                
                if attempts >= 3:
                    conn.execute(text("UPDATE sms_codes SET used = TRUE WHERE id = :id"), {"id": code_id})
                    return {'success': False, 'message': 'Demasiados intentos. Solicita un nuevo código'}
                
                is_valid_code = input_code == stored_code
                
                if is_valid_code:
                    conn.execute(text("UPDATE sms_codes SET used = TRUE WHERE id = :id"), {"id": code_id})
                    
                    return {'success': True, 'message': 'Código verificado correctamente'}
                else:
                    remaining_attempts = 3 - (attempts + 1)
                    return {
                        'success': False, 
                        'message': f'Código incorrecto. Te quedan {remaining_attempts} intentos'
                    }
                    
        except Exception as e:
            print(f"Error verificando código SMS: {e}")
            return {'success': False, 'message': 'Error interno del servidor'}