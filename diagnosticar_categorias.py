
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def diagnosticar_categorias():
   
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL no encontrada")
        return
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DE CATEGORÍAS EN RAILWAY")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
       
        print("\n📋 1. Verificando tabla 'categoria'...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'categoria'
            );
        """)
        tabla_existe = cursor.fetchone()[0]
        
        if not tabla_existe:
            print("❌ La tabla 'categoria' NO EXISTE")
            print("💡 Necesitas crear la tabla. Ejecuta:")
            print("   python app.py (para inicializar la base de datos)")
            cursor.close()
            conn.close()
            return
        
        print("✅ Tabla 'categoria' existe")
        
        
        print("\n📊 2. Contando categorías...")
        cursor.execute("SELECT COUNT(*) FROM categoria")
        total = cursor.fetchone()[0]
        print(f"✅ Total de categorías: {total}")
        
        if total == 0:
            print("⚠️  NO HAY CATEGORÍAS en la base de datos")
            print("💡 Ejecuta: python insertar_categorias_railway.py")
            cursor.close()
            conn.close()
            return
        
       
        print("\n📝 3. Categorías registradas:")
        cursor.execute("SELECT id, nombre FROM categoria ORDER BY id")
        categorias = cursor.fetchall()
        
        for cat_id, nombre in categorias:
            print(f"   ✅ ID {cat_id}: {nombre}")
        
       
        print("\n🔧 4. Estructura de la tabla 'categoria':")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'categoria'
            ORDER BY ordinal_position
        """)
        columnas = cursor.fetchall()
        
        for col_name, col_type in columnas:
            print(f"   📌 {col_name}: {col_type}")
        
        
        print("\n🛒 5. Productos por categoría:")
        cursor.execute("""
            SELECT c.nombre, COUNT(p.id) as total_productos
            FROM categoria c
            LEFT JOIN producto p ON c.id = p.categoria_id
            GROUP BY c.id, c.nombre
            ORDER BY c.id
        """)
        productos_por_cat = cursor.fetchall()
        
        for cat_nombre, total_prod in productos_por_cat:
            print(f"   📦 {cat_nombre}: {total_prod} producto(s)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("=" * 70)
        
        if total > 0:
            print("\n💡 Las categorías ESTÁN en la base de datos.")
            print("   Si no las ves en el formulario:")
            print("   1. Cierra sesión y vuelve a entrar")
            print("   2. Presiona Ctrl+Shift+R para limpiar cache")
            print("   3. Verifica que estés en /admin/productos/agregar")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 Iniciando diagnóstico...\n")
    diagnosticar_categorias()
