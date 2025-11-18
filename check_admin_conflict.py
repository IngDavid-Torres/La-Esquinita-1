
import os
import sys
sys.path.append('.')

from app import app, db, Administrador, Usuario

def check_admin_user_conflict():
    print("🔍 Verificando conflictos entre admin y usuarios...")
    
    with app.app_context():
        try:
            # Verificar admin
            admin = Administrador.query.filter_by(email="admin@laesquinita.com").first()
            if admin:
                print(f"✅ Admin encontrado:")
                print(f"   - ID: {admin.id}")
                print(f"   - Nombre: {admin.nombre}")
                print(f"   - Email: {admin.email}")
                print(f"   - Password: {admin.password}")
            else:
                print("❌ No se encontró admin")
            
           
            usuario_conflicto = Usuario.query.filter_by(email="admin@laesquinita.com").first()
            if usuario_conflicto:
                print(f"⚠️ CONFLICTO DETECTADO - Usuario con mismo email:")
                print(f"   - ID: {usuario_conflicto.id}")
                print(f"   - Nombre: {usuario_conflicto.nombre}")
                print(f"   - Email: {usuario_conflicto.email}")
                print(f"   - Password: {usuario_conflicto.password}")
                print(f"   - Tipo: {usuario_conflicto.tipo_usuario}")
                
                # Eliminar usuario conflictivo
                respuesta = input("¿Eliminar usuario conflictivo? (s/n): ")
                if respuesta.lower() == 's':
                    db.session.delete(usuario_conflicto)
                    db.session.commit()
                    print("✅ Usuario conflictivo eliminado")
            else:
                print("✅ No hay conflictos - No existe usuario con email de admin")
            
            
            usuarios_similares = Usuario.query.filter(Usuario.email.like("%admin%")).all()
            if usuarios_similares:
                print(f"\n👥 Usuarios con 'admin' en el email:")
                for u in usuarios_similares:
                    print(f"   - {u.nombre} ({u.email}) - Tipo: {u.tipo_usuario}")
                    
        except Exception as e:
            print(f"❌ Error verificando conflictos: {e}")

if __name__ == "__main__":
    check_admin_user_conflict()