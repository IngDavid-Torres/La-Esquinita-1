import subprocess
import sys
import os

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        print(f"✅ {package_name} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package_name}: {e}")
        return False

def install_sms_dependencies():
    packages = [
        'twilio==8.10.0',
        'boto3==1.34.0',
        'vonage==3.14.0',
        'phonenumbers==8.13.26',
        'psycopg2-binary==2.9.9'
    ]
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"✅ Paquetes instalados: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("🎉 ¡Todas las dependencias instaladas correctamente!")
    else:
        print("⚠️ Algunas dependencias fallaron. Instálalas manualmente si es necesario.")

def setup_environment_variables():
    env_content = """TWILIO_ACCOUNT_SID=tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_PHONE_NUMBER=+1234567890

AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
AWS_REGION=us-east-1

VONAGE_API_KEY=tu_api_key_aqui
VONAGE_API_SECRET=tu_api_secret_aqui

DATABASE_URL=postgresql://postgres:password@localhost/laesquinita
"""
    
    try:
        with open('.env.example', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("📝 Archivo .env.example creado")
    except Exception as e:
        print(f"❌ Error creando .env.example: {e}")

def create_database_migration():
    sql_content = """ALTER TABLE usuario 
ADD COLUMN IF NOT EXISTS telefono VARCHAR(20),
ADD COLUMN IF NOT EXISTS telefono_verificado BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS sms_codes (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sms_codes_phone ON sms_codes(phone_number);
CREATE INDEX IF NOT EXISTS idx_sms_codes_expires ON sms_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_usuario_telefono ON usuario(telefono);

COMMIT;
"""
    
    try:
        with open('sms_migration.sql', 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print("📄 Script de migración SQL creado: sms_migration.sql")
    except Exception as e:
        print(f"❌ Error creando migración SQL: {e}")

if __name__ == "__main__":
    print("🌽 La Esquinita - Instalador SMS")
    print("=" * 40)
    
    install_sms_dependencies()
    print("\n" + "=" * 40)
    setup_environment_variables()
    print("\n" + "=" * 40)
    create_database_migration()
    
    print("\n🎯 Instalación completada!")