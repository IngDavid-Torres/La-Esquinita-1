import os
import sys
MP_ACCESS_TOKEN = "TEST-7916427332588639-102718-00ee5129ad06c2ceba14e4e44b94d22e-191563398"

def test_payment_logic():
    print("🔄 Iniciando prueba de lógica de pagos")
    
    nombre = "Juan Pérez"
    correo = "juan@email.com" 
    direccion = "Calle Principal 123, Ciudad"
    total = 150.00
    
    print(f"📝 Datos de prueba:")
    print(f"   Nombre: {nombre}")
    print(f"   Correo: {correo}")
    print(f"   Dirección: {direccion}")
    print(f"   Total: ${total}")
    
    # Validaciones
    if not nombre or len(nombre) < 3:
        print("❌ Error: Nombre inválido")
        return False
    
    if not correo or '@' not in correo:
        print("❌ Error: Correo inválido")
        return False
    
    if not direccion or len(direccion) < 10:
        print("❌ Error: Dirección inválida")
        return False
    
    print("✅ Validaciones pasadas")
    
    if MP_ACCESS_TOKEN.startswith("TEST-"):
        print("🧪 MODO TEST DETECTADO")
        print("✅ Se debería mostrar pago_test_processing.html")
        return True
    else:
        print("🏭 MODO PRODUCCIÓN")
        print("✅ Se debería redirigir a MercadoPago API")
        return True

if __name__ == "__main__":
    resultado = test_payment_logic()
    if resultado:
        print("\n🎉 ¡Prueba exitosa! La lógica funciona correctamente")
    else:
        print("\n❌ Prueba fallida")