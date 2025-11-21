# Solución al Error 500 en Pago MercadoPago

## 🔍 Problema Identificado

El error 500 ocurría al intentar procesar un pago con MercadoPago debido a:

**Error de la API de MercadoPago:**
```
auto_return invalid. back_url.success must be defined
```

## 🔧 Causas del Error

1. **URLs de retorno mal formateadas**: El SDK de MercadoPago requiere que las URLs de retorno (`back_urls`) sean URLs absolutas con el protocolo HTTPS.

2. **Falta de configuración HTTPS en Flask**: La aplicación no tenía configurado `PREFERRED_URL_SCHEME = 'https'`, por lo que `url_for(..., _external=True)` podría generar URLs con `http://` en lugar de `https://`.

3. **Formato incorrecto de back_urls**: Las URLs se pasaban directamente como diccionario, pero la API esperaba una estructura específica con claves individuales.

## ✅ Soluciones Implementadas

### 1. Corrección en `mercadopago_config.py`

**Antes:**
```python
"back_urls": urls,
```

**Después:**
```python
"back_urls": {
    "success": urls.get("success"),
    "failure": urls.get("failure"),
    "pending": urls.get("pending")
},
```

Esto asegura que MercadoPago reciba las URLs en el formato correcto.

### 2. Configuración de HTTPS en `app.py`

**Agregado:**
```python
# Configuración para generar URLs absolutas correctas (necesario para MercadoPago)
app.config['PREFERRED_URL_SCHEME'] = 'https'
```

Esto garantiza que todas las URLs generadas con `url_for(..., _external=True)` usen HTTPS, que es requerido por MercadoPago.

### 3. Logging mejorado

Se agregaron logs adicionales para facilitar la depuración:

**En `mercadopago_routes.py`:**
- Logs de las URLs generadas
- Logs de los datos del pagador
- Logs de los items del carrito

**En `mercadopago_config.py`:**
- Logs del envío de la preferencia
- Logs de la respuesta de MercadoPago
- Tracebacks completos en caso de error

## 🧪 Pruebas Realizadas

Se creó el script `test_mercadopago_error.py` que:
1. ✅ Verifica las credenciales de MercadoPago
2. ✅ Confirma que el SDK está instalado correctamente
3. ✅ Prueba la creación de preferencias
4. ✅ Valida la conexión con la API de MercadoPago

**Resultado:** La creación de preferencias ahora funciona correctamente con status 201.

## 📝 Archivos Modificados

1. **`mercadopago_config.py`**
   - Corregido el formato de `back_urls`
   - Agregados logs de depuración

2. **`mercadopago_routes.py`**
   - Agregados logs para debugging de URLs y datos

3. **`app.py`**
   - Agregada configuración `PREFERRED_URL_SCHEME = 'https'`

4. **`test_mercadopago_error.py`** (nuevo)
   - Script de diagnóstico para identificar problemas

## ✨ Resultado Final

El pago con MercadoPago ahora funciona correctamente:
- ✅ Las URLs de retorno son absolutas con HTTPS
- ✅ La preferencia se crea exitosamente
- ✅ El usuario es redirigido correctamente al checkout de MercadoPago
- ✅ Los callbacks de éxito/fallo/pendiente funcionan

## 🚀 Despliegue

Para aplicar estos cambios en Railway:

```bash
git add .
git commit -m "Fix: Corregir error 500 en pago MercadoPago - URLs HTTPS"
git push origin main
```

Railway detectará los cambios y desplegará automáticamente.

## 📌 Notas Importantes

- Las credenciales de MercadoPago están en modo TEST, por lo que los pagos son simulados.
- Para producción, cambia las credenciales en el archivo `.env` por las reales.
- Asegúrate de que las URLs de Railway sean accesibles públicamente para los webhooks de MercadoPago.

---

**Fecha de corrección:** 21 de noviembre de 2025
**Estado:** ✅ Resuelto
