

from app import app, db, Administrador, Usuario
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_duplicacion():
   
    with app.app_context():
        try:
            
            admin = Administrador.query.filter_by(email='admin@laesquinita.com').first()
            logger.info("🔍 TABLA ADMINISTRADORES:")
            if admin:
                logger.info(f"  ✅ Admin encontrado: ID={admin.id}, Nombre={admin.nombre}, Email={admin.email}, Password={admin.password}")
            else:
                logger.info("  ❌ No se encontró admin")
            
          
            usuario = Usuario.query.filter_by(email='admin@laesquinita.com').first()
            logger.info("🔍 TABLA USUARIOS:")
            if usuario:
                logger.warning(f"  ⚠️ DUPLICACIÓN DETECTADA: ID={usuario.id}, Nombre={usuario.nombre}, Email={usuario.email}, Password={usuario.password}, Tipo={usuario.tipo_usuario}")
                return True
            else:
                logger.info("  ✅ No se encontró usuario con email admin")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando duplicación: {str(e)}")
            return False

def eliminar_usuario_admin():
    
    with app.app_context():
        try:
            usuario = Usuario.query.filter_by(email='admin@laesquinita.com').first()
            if usuario:
                logger.info(f"🗑️ Eliminando usuario duplicado: {usuario.nombre}")
                db.session.delete(usuario)
                db.session.commit()
                logger.info("✅ Usuario duplicado eliminado")
                return True
            else:
                logger.info("ℹ️ No hay usuario duplicado que eliminar")
                return False
        except Exception as e:
            logger.error(f"❌ Error eliminando usuario: {str(e)}")
            return False

def mostrar_todos_usuarios():
    
    with app.app_context():
        try:
            usuarios = Usuario.query.all()
            logger.info(f"📋 TODOS LOS USUARIOS ({len(usuarios)}):")
            for usuario in usuarios:
                logger.info(f"  ID: {usuario.id} | Nombre: {usuario.nombre} | Email: {usuario.email} | Tipo: {usuario.tipo_usuario}")
                
            admins = Administrador.query.all()
            logger.info(f"📋 TODOS LOS ADMINISTRADORES ({len(admins)}):")
            for admin in admins:
                logger.info(f"  ID: {admin.id} | Nombre: {admin.nombre} | Email: {admin.email}")
                
        except Exception as e:
            logger.error(f"❌ Error mostrando usuarios: {str(e)}")

if __name__ == "__main__":
    logger.info("🔍 Verificando duplicación de email admin...")
    mostrar_todos_usuarios()
    
    duplicacion = verificar_duplicacion()
    
    if duplicacion:
        logger.warning("⚠️ PROBLEMA DETECTADO: Email admin existe en ambas tablas")
        respuesta = input("¿Eliminar usuario duplicado? (s/n): ")
        if respuesta.lower() == 's':
            eliminar_usuario_admin()
            logger.info("✅ Problema solucionado")
        else:
            logger.info("ℹ️ Usuario eligió no eliminar duplicado")
    else:
        logger.info("✅ No hay duplicación de email")