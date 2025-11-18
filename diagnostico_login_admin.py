
from app import app, db, Administrador, Usuario
from flask import session

def verificar_admin():
    with app.app_context():
        print("\n" + "="*60)
        print("DIAGNÓSTICO DE LOGIN ADMIN")
        print("="*60)
        
        
        print("\n1. Verificando tabla Administrador...")
        try:
            admin_count = Administrador.query.count()
            print(f"   ✅ Total de administradores: {admin_count}")
            
            if admin_count > 0:
                admins = Administrador.query.all()
                for admin in admins:
                    print(f"   - ID: {admin.id}, Email: {admin.email}, Nombre: {admin.nombre}")
            else:
                print("   ⚠️  No hay administradores registrados")
                print("\n   Creando administrador de prueba...")
                nuevo_admin = Administrador(
                    nombre="Admin Test",
                    email="admin@laesquinita.com",
                    password="Admin123!"
                )
                db.session.add(nuevo_admin)
                db.session.commit()
                print("   ✅ Admin creado: admin@laesquinita.com / Admin123!")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
       
        print("\n2. Verificando ruta /panel_admin...")
        try:
            with app.test_client() as client:
                # Intentar acceder sin sesión
                response = client.get('/panel_admin', follow_redirects=False)
                print(f"   - Sin sesión: Status {response.status_code}")
                print(f"   - Redirect: {response.location if response.status_code in [301, 302] else 'N/A'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        
        print("\n3. Simulando login de admin...")
        try:
            admin = Administrador.query.filter_by(email="admin@laesquinita.com").first()
            if admin:
                with app.test_client() as client:
                    response = client.post('/login', data={
                        'email': 'admin@laesquinita.com',
                        'password': 'Admin123!',
                        'captcha': 'TEST'  # Captcha de prueba
                    }, follow_redirects=False)
                    
                    print(f"   - Status: {response.status_code}")
                    print(f"   - Redirect: {response.location if response.status_code in [301, 302] else 'N/A'}")
                    
                    if response.status_code == 302:
                        print(f"   ✅ Login exitoso, redirigiendo a: {response.location}")
                    else:
                        print(f"   ⚠️  Respuesta inesperada")
                        print(f"   - Data: {response.data[:200]}")
            else:
                print("   ❌ Admin no encontrado")
        except Exception as e:
            print(f"   ❌ Error en login: {e}")
        
        
        print("\n4. Verificando configuración de sesión...")
        print(f"   - SECRET_KEY configurada: {'✅' if app.secret_key else '❌'}")
        print(f"   - PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME', 'N/A')}")
        print(f"   - SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE', 'N/A')}")
        print(f"   - SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY', 'N/A')}")
        
        print("\n" + "="*60)
        print("DIAGNÓSTICO COMPLETADO")
        print("="*60 + "\n")

if __name__ == "__main__":
    verificar_admin()
