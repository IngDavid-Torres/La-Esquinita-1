
from app import app, db, Administrador, Usuario
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simular_login(email, password):
    
    with app.app_context():
        try:
            logger.info(f"🔐 SIMULANDO LOGIN:")
            logger.info(f"  📧 Email: {email}")
            logger.info(f"  🔑 Password: {password}")
            
           
            logger.info("🔍 PASO 1: Verificando en tabla ADMINISTRADORES...")
            admin = Administrador.query.filter_by(email=email, password=password).first()
            
            if admin:
                logger.info(f"✅ ADMIN ENCONTRADO:")
                logger.info(f"  ID: {admin.id}")
                logger.info(f"  Nombre: {admin.nombre}")
                logger.info(f"  Email: {admin.email}")
                logger.info(f"  Password: {admin.password}")
                logger.info("🎯 RESULTADO: Debería ir a panel_admin")
                return "admin"
            else:
                logger.warning("❌ Admin NO encontrado")
            
           
            logger.info("🔍 PASO 2: Verificando en tabla USUARIOS...")
            usuario = Usuario.query.filter_by(email=email, password=password).first()
            
            if usuario:
                logger.warning(f"⚠️ USUARIO ENCONTRADO (ESTO NO DEBERÍA PASAR):")
                logger.warning(f"  ID: {usuario.id}")
                logger.warning(f"  Nombre: {usuario.nombre}")
                logger.warning(f"  Email: {usuario.email}")
                logger.warning(f"  Password: {usuario.password}")
                logger.warning(f"  Tipo: {usuario.tipo_usuario}")
                logger.warning("🎯 RESULTADO: Iría a panel_cliente")
                return "usuario"
            else:
                logger.info("✅ Usuario NO encontrado")
            
            logger.info("❌ RESULTADO: Credenciales incorrectas")
            return "incorrecto"
            
        except Exception as e:
            logger.error(f"❌ Error en simulación: {str(e)}")
            return "error"

def verificar_todas_combinaciones():
    
    logger.info("🧪 PROBANDO COMBINACIONES DE CREDENCIALES:")
    
   
    combinaciones = [
        ("admin@laesquinita.com", "securepassword"),
        ("admin@laesquinita.com", "Admin123!"),
        ("admin@laesquinita.com", "admin"),
        ("doser97.mix@outlook.com", "securepassword")  
    ]
    
    for email, password in combinaciones:
        logger.info(f"\n{'='*50}")
        resultado = simular_login(email, password)
        logger.info(f"📊 RESULTADO FINAL: {resultado}")

if __name__ == "__main__":
    logger.info("🔬 INICIANDO DIAGNÓSTICO DE LOGIN...")
    verificar_todas_combinaciones()