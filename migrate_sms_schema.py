
from app import app, db, Usuario
from sms_verification import SMSCode
from sqlalchemy import text, inspect

def check_column_exists(table_name, column_name):
    
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_sms_tables():
    with app.app_context():
        print("🔍 Verificando estructura de base de datos para SMS...")
        
        
        try:
            sms_code_manager = SMSCode(db)
            print("✅ Tabla sms_codes verificada/creada")
        except Exception as e:
            print(f"❌ Error al verificar sms_codes: {e}")
            return False
        
       
        try:
            has_telefono = check_column_exists('usuario', 'telefono')
            has_telefono_verificado = check_column_exists('usuario', 'telefono_verificado')
            
            if not has_telefono:
                print("⚠️ Agregando columna 'telefono' a tabla usuario...")
                with db.engine.begin() as conn:
                    conn.execute(text("""
                        ALTER TABLE usuario 
                        ADD COLUMN IF NOT EXISTS telefono VARCHAR(20)
                    """))
                print("✅ Columna 'telefono' agregada")
            else:
                print("✅ Columna 'telefono' ya existe")
            
            if not has_telefono_verificado:
                print("⚠️ Agregando columna 'telefono_verificado' a tabla usuario...")
                with db.engine.begin() as conn:
                    conn.execute(text("""
                        ALTER TABLE usuario 
                        ADD COLUMN IF NOT EXISTS telefono_verificado BOOLEAN DEFAULT FALSE
                    """))
                print("✅ Columna 'telefono_verificado' agregada")
            else:
                print("✅ Columna 'telefono_verificado' ya existe")
            
        except Exception as e:
            print(f"❌ Error al verificar columnas de Usuario: {e}")
            return False
        
        print("\n" + "="*60)
        print("✅ Migración completada exitosamente")
        print("="*60)
        print("\n📋 Estructura verificada:")
        print("   - Tabla 'usuario' con campos: telefono, telefono_verificado")
        print("   - Tabla 'sms_codes' con índices optimizados")
        print("\n🚀 Sistema listo para enviar códigos de verificación por SMS")
        return True

if __name__ == '__main__':
    success = migrate_sms_tables()
    if not success:
        print("\n⚠️ La migración tuvo problemas. Revisa los errores arriba.")
        exit(1)
