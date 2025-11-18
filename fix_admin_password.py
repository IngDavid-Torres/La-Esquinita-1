
import os
import sys
sys.path.append('.')

from app import app, db, Administrador

def fix_admin_password():
    print("🔧 Actualizando contraseña del administrador...")
    
    with app.app_context():
        try:
            admin = Administrador.query.filter_by(email="admin@laesquinita.com").first()
            if admin:
                print(f"🔍 Admin encontrado: {admin.nombre}")
                print(f"📧 Email: {admin.email}")
                print(f"🔑 Contraseña actual: {admin.password}")
                
                
                admin.password = "admin123"
                db.session.commit()
                
                print("✅ Contraseña actualizada correctamente a: admin123")
                
                
                admin_verificado = Administrador.query.filter_by(email="admin@laesquinita.com").first()
                print(f"🔍 Verificación - Nueva contraseña: {admin_verificado.password}")
                
            else:
                print("❌ No se encontró el administrador")
                
        except Exception as e:
            print(f"❌ Error actualizando contraseña: {e}")

if __name__ == "__main__":
    fix_admin_password()