
import sys

print("=== TEST DE CAPTCHA ===\n")


print("1. Probando imports...")
try:
    from PIL import Image, ImageDraw, ImageFont
    print("   ✅ PIL/Pillow importado correctamente")
    print(f"   Versión Pillow: {Image.__version__ if hasattr(Image, '__version__') else 'Desconocida'}")
except ImportError as e:
    print(f"   ❌ Error al importar PIL: {e}")
    sys.exit(1)

try:
    import io
    import base64
    import random
    import string
    print("   ✅ Módulos estándar importados")
except ImportError as e:
    print(f"   ❌ Error al importar módulos: {e}")
    sys.exit(1)

print("\n2. Probando creación de imagen...")
try:
    img = Image.new('RGB', (200, 80), color='white')
    print(f"   ✅ Imagen creada: {img.size}, modo: {img.mode}")
except Exception as e:
    print(f"   ❌ Error creando imagen: {e}")
    sys.exit(1)


print("\n3. Probando ImageDraw...")
try:
    draw = ImageDraw.Draw(img)
    draw.point((10, 10), fill=(255, 0, 0))
    print("   ✅ ImageDraw funciona correctamente")
except Exception as e:
    print(f"   ❌ Error con ImageDraw: {e}")
    sys.exit(1)

print("\n4. Probando fuentes...")
font_paths = [
    "arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

font = None
for path in font_paths:
    try:
        font = ImageFont.truetype(path, 36)
        print(f"   ✅ Fuente cargada: {path}")
        break
    except:
        print(f"   ⚠️ Fuente no disponible: {path}")

if not font:
    print("   ⚠️ Usando fuente por defecto")
    font = ImageFont.load_default()


print("\n5. Probando dibujo de texto...")
try:
    draw.text((50, 30), "TEST", font=font, fill=(0, 0, 0))
    print("   ✅ Texto dibujado correctamente")
except Exception as e:
    print(f"   ❌ Error dibujando texto: {e}")
    sys.exit(1)

print("\n6. Probando conversión a base64...")
try:
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode()
    data_uri = f"data:image/png;base64,{img_base64}"
    print(f"   ✅ Imagen convertida a base64")
    print(f"   Tamaño: {len(img_base64)} caracteres")
    print(f"   Data URI: {data_uri[:100]}...")
except Exception as e:
    print(f"   ❌ Error convirtiendo a base64: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


print("\n7. Probando función completa de CAPTCHA...")
try:
    def generate_captcha_code(length=5):
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1')
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_captcha_image(code):
        width, height = 200, 80
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
       
        for _ in range(100):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            draw.point((x, y), fill=(random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)))
        
      
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            except:
                font = ImageFont.load_default()
        
        
        try:
            text_width = draw.textlength(code, font=font)
        except AttributeError:
            text_width = len(code) * 20
        
        text_height = 36
        x = max(10, (width - text_width) // 2)
        y = max(10, (height - text_height) // 2)
        
      
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), code, font=font, fill=color)
        
        
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
        
        return img
    
    code = generate_captcha_code()
    print(f"   Código generado: {code}")
    
    img = create_captcha_image(code)
    print(f"   Imagen creada: {img.size}")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode()
    data_uri = f"data:image/png;base64,{img_base64}"
    
    print(f"   ✅ CAPTCHA completo generado exitosamente")
    print(f"   Tamaño final: {len(data_uri)} caracteres")
    
except Exception as e:
    print(f"   ❌ Error en función completa: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== ✅ TODOS LOS TESTS PASARON ===")
print("El sistema de CAPTCHA debería funcionar correctamente.")
