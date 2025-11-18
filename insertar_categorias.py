
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Categoria

def insertar_categorias():
   
    
    with app.app_context():
        print("=" * 70)
        print("🌽 INSERTANDO CATEGORÍAS EN LA BASE DE DATOS")
        print("=" * 70)
        
        
        categorias = [
            "Esquites",
            "Patitas", 
            "Elotes",
            "Maruchan"
        ]
        
        categorias_insertadas = 0
        categorias_existentes = 0
        
        for nombre_cat in categorias:
            
            categoria_existente = Categoria.query.filter_by(nombre=nombre_cat).first()
            
            if categoria_existente:
                print(f"⚠️  '{nombre_cat}' ya existe (ID: {categoria_existente.id})")
                categorias_existentes += 1
            else:
               
                nueva_categoria = Categoria(nombre=nombre_cat)
                db.session.add(nueva_categoria)
                print(f"✅ '{nombre_cat}' insertada correctamente")
                categorias_insertadas += 1
        
       
        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"📊 RESUMEN:")
            print(f"   ✅ Categorías nuevas insertadas: {categorias_insertadas}")
            print(f"   ⚠️  Categorías que ya existían: {categorias_existentes}")
            print("=" * 70)
            
            
            print("\n📋 CATEGORÍAS EN LA BASE DE DATOS:")
            todas_categorias = Categoria.query.all()
            for cat in todas_categorias:
                print(f"   ID {cat.id}: {cat.nombre}")
            
            print("\n✅ ¡Proceso completado exitosamente!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR al guardar categorías: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    print("\n🚀 Iniciando inserción de categorías...\n")
    exito = insertar_categorias()
    
    if exito:
        print("\n🎉 Las categorías están listas para usar en La Esquinita!")
    else:
        print("\n⚠️  Hubo un problema al insertar las categorías")
