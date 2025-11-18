

from app import app, db, Administrador
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_admin():
    
    with app.app_context():
        try:
            # Buscar el admin
            admin = Administrador.query.filter_by(email='admin@laesquinita.com').first()
            
            if admin:
                logger.info(f"✅ Admin encontrado: {admin.nombre} (ID: {admin.id})")
                logger.info(f"📧 Email: {admin.email}")
                logger.info(f"🔑 Password (hash): {admin.password}")
                
                # Verificar contraseña
                test_password = "Admin123!"  # Contraseña común de admin
                if admin.password == test_password:
                    logger.info(f"✅ Contraseña coincide: {test_password}")
                else:
                    logger.warning(f"⚠️ Contraseña NO coincide con {test_password}")
                    logger.info(f"💡 Contraseña actual en BD: {admin.password}")
                
                return admin
            else:
                logger.warning("⚠️ No se encontró admin con email admin@laesquinita.com")
                
                # Crear admin si no existe
                logger.info("🔧 Creando administrador...")
                nuevo_admin = Administrador(
                    nombre="Administrador Principal",
                    email="admin@laesquinita.com", 
                    password="Admin123!"
                )
                db.session.add(nuevo_admin)
                db.session.commit()
                logger.info("✅ Administrador creado exitosamente")
                return nuevo_admin
                
        except Exception as e:
            logger.error(f"❌ Error verificando admin: {str(e)}")
            return None

def listar_todos_admins():
    
    with app.app_context():
        try:
            admins = Administrador.query.all()
            logger.info(f"📋 Total de administradores: {len(admins)}")
            
            for i, admin in enumerate(admins, 1):
                logger.info(f"  {i}. ID: {admin.id} | Nombre: {admin.nombre} | Email: {admin.email} | Password: {admin.password}")
                
        except Exception as e:
            logger.error(f"❌ Error listando admins: {str(e)}")

if __name__ == "__main__":
    logger.info("🔍 Verificando administrador...")
    listar_todos_admins()
    admin = verificar_admin()
    
    if admin:
        logger.info("✅ Verificación completa")
    else:
        logger.error("❌ Fallo en verificación")