
import os
os.environ['FLASK_ENV'] = 'production'

from app import app, db, Categoria

def insertar_categorias():
    print("=" * 70)
    print("🌽 INSERTANDO CATEGORÍAS EN PRODUCCIÓN")
    print("=" * 70)
    
    with app.app_context():
        
        print(f"\n📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'No configurada')[:50]}...")
        
        categorias = [
            "Elotes",
            "Esquites", 
            "Patitas",
            "Maruchan"
        ]
        
        insertadas = 0
        existentes = 0
        
        for nombre in categorias:
            categoria_existe = Categoria.query.filter_by(nombre=nombre).first()
            
            if categoria_existe:
                print(f"⚠️  Categoría '{nombre}' ya existe (ID: {categoria_existe.id})")
                existentes += 1
            else:
                nueva_categoria = Categoria(nombre=nombre)
                db.session.add(nueva_categoria)
                insertadas += 1
                print(f"✅ Categoría '{nombre}' insertada")
        
        if insertadas > 0:
            db.session.commit()
            print(f"\n✅ {insertadas} categorías insertadas correctamente")
        
        if existentes > 0:
            print(f"ℹ️  {existentes} categorías ya existían")
        
       
        print("\n" + "=" * 70)
        print("📋 CATEGORÍAS EN BASE DE DATOS:")
        print("=" * 70)
        todas_categorias = Categoria.query.all()
        print(f"Total: {len(todas_categorias)} categorías")
        for cat in todas_categorias:
            print(f"  - ID {cat.id}: {cat.nombre}")
        print("=" * 70)

if __name__ == "__main__":
    insertar_categorias()
