
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def insertar_categorias_railway():
    
    
   
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL no encontrada en las variables de entorno")
        print("   Asegúrate de tener el archivo .env con la variable DATABASE_URL")
        return False
    
   
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 70)
    print("🌽 INSERTANDO CATEGORÍAS EN RAILWAY (PostgreSQL)")
    print("=" * 70)
    
    categorias = [
        "Elotes",
        "Esquites",
        "Patitas",
        "Maruchan"
    ]
    
    try:
        
        print("\n🔌 Conectando a la base de datos de Railway...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Conexión establecida")
        
        categorias_insertadas = 0
        categorias_existentes = 0
        
        for nombre_cat in categorias:
            
            cursor.execute(
                "SELECT id FROM categoria WHERE nombre = %s",
                (nombre_cat,)
            )
            resultado = cursor.fetchone()
            
            if resultado:
                print(f"⚠️  '{nombre_cat}' ya existe (ID: {resultado[0]})")
                categorias_existentes += 1
            else:
               
                cursor.execute(
                    "INSERT INTO categoria (nombre) VALUES (%s) RETURNING id",
                    (nombre_cat,)
                )
                nuevo_id = cursor.fetchone()[0]
                print(f"✅ '{nombre_cat}' insertada correctamente (ID: {nuevo_id})")
                categorias_insertadas += 1
        
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print(f"📊 RESUMEN:")
        print(f"   ✅ Categorías nuevas insertadas: {categorias_insertadas}")
        print(f"   ⚠️  Categorías que ya existían: {categorias_existentes}")
        print("=" * 70)
        
        
        print("\n📋 CATEGORÍAS EN RAILWAY:")
        cursor.execute("SELECT id, nombre FROM categoria ORDER BY id")
        todas_categorias = cursor.fetchall()
        for cat_id, nombre in todas_categorias:
            print(f"   ID {cat_id}: {nombre}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ ¡Proceso completado exitosamente!")
        print("🎉 Las categorías ahora están disponibles en producción!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que tengas psycopg2 instalado: pip install psycopg2-binary")
        print("   2. Verifica que DATABASE_URL esté correcta en el archivo .env")
        print("   3. Verifica que tengas conexión a internet")
        return False

if __name__ == "__main__":
    print("\n🚀 Iniciando inserción de categorías en Railway...\n")
    exito = insertar_categorias_railway()
    
    if not exito:
        print("\n⚠️  Hubo un problema. Revisa los errores arriba.")
