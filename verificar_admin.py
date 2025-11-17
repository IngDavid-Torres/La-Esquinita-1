

import os
import sys
from datetime import datetime


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Administrador, Usuario, Producto, Categoria

def verificar_admin():
    
    with app.app_context():
        try:
            print("🔍 Verificando credenciales de administrador...")
            
           
            admin = Administrador.query.filter_by(email="admin@laesquinita.com").first()
            
            if admin:
                print(f"✅ Administrador encontrado:")
                print(f"   ID: {admin.id}")
                print(f"   Nombre: {admin.nombre}")
                print(f"   Email: {admin.email}")
                print(f"   Password: {admin.password}")
                
                
                admin_login = Administrador.query.filter_by(
                    email="admin@laesquinita.com", 
                    password="admin123"
                ).first()
                
                if admin_login:
                    print("✅ Las credenciales admin@laesquinita.com / admin123 funcionan correctamente")
                else:
                    print("❌ Las credenciales no coinciden")
                    print("🔧 Actualizando password a 'admin123'...")
                    admin.password = "admin123"
                    db.session.commit()
                    print("✅ Password actualizado")
                    
            else:
                print("❌ No se encontró el administrador")
                print("🔧 Creando administrador...")
                nuevo_admin = Administrador(
                    nombre="Admin La Esquinita", 
                    email="admin@laesquinita.com", 
                    password="admin123"
                )
                db.session.add(nuevo_admin)
                db.session.commit()
                print("✅ Administrador creado correctamente")
            
            
            print(f"\n📊 Estadísticas de la base de datos:")
            print(f"   Administradores: {Administrador.query.count()}")
            print(f"   Usuarios: {Usuario.query.count()}")
            print(f"   Productos: {Producto.query.count()}")
            print(f"   Categorías: {Categoria.query.count()}")
            
        except Exception as e:
            print(f"❌ Error verificando admin: {str(e)}")

def listar_todos_admins():
   
    with app.app_context():
        try:
            admins = Administrador.query.all()
            print(f"\n👥 Todos los administradores ({len(admins)}):")
            for admin in admins:
                print(f"   ID: {admin.id} | Nombre: {admin.nombre} | Email: {admin.email} | Pass: {admin.password}")
        except Exception as e:
            print(f"❌ Error listando admins: {str(e)}")

def test_login():
    
    with app.app_context():
        try:
            print(f"\n🧪 Probando login con admin@laesquinita.com / admin123")
            admin = Administrador.query.filter_by(
                email="admin@laesquinita.com", 
                password="admin123"
            ).first()
            
            if admin:
                print("✅ Login exitoso simulado")
                print(f"   Se redirigiría a panel_admin")
                print(f"   Session sería: usuario_id={admin.id}, tipo_usuario=Administrador")
            else:
                print("❌ Login falló - credenciales incorrectas")
                
        except Exception as e:
            print(f"❌ Error en test login: {str(e)}")

if __name__ == "__main__":
    print("🌽 La Esquinita - Verificador de Credenciales Admin")
    print("=" * 50)
    
    verificar_admin()
    listar_todos_admins()
    test_login()
    
    print("\n" + "=" * 50)
    print("✅ Verificación completada")
    print("\n💡 Credenciales para login:")
    print("   Email: admin@laesquinita.com")
    print("   Password: admin123")