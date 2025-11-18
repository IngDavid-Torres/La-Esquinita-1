# Diagnóstico: CAPTCHA Retorna NULL en Railway

## Problema Identificado

La URL `https://web-production-adfd.up.railway.app/generate_captcha` retorna:
```json
{"success": true, "image": null}
```

## Causa Más Probable

**Problema con las sesiones de Flask en Railway:**
- El CAPTCHA se genera correctamente (success: true)
- Pero el `data_uri` no llega al JSON response
- Localmente funciona perfectamente ✅

## Posibles Causas

### 1. SECRET_KEY no configurada o inconsistente ⚠️
Railway puede estar usando un SECRET_KEY diferente o regenerándola en cada deploy.

**Solución:**
```bash
# En Railway Dashboard → Variables
SECRET_KEY=tu_clave_secreta_fija_y_larga_minimo_32_caracteres
```

### 2. Múltiples workers compartiendo sesiones
Si Railway usa múltiples workers de Gunicorn sin un backend de sesiones compartido.

**Solución:** Usar Redis para sesiones compartidas (avanzado)

### 3. Problema con codificación base64
Aunque poco probable, podría haber un problema con la codificación en el entorno de Railway.

## Cambios Implementados

### 1. Limpieza del código de generate_captcha
- Eliminadas líneas vacías sospechosas
- Agregado más logging
- Docstring añadido

```python
@app.route('/generate_captcha')
def generate_captcha():
    """Genera un CAPTCHA SVG y lo guarda en la sesión"""
    try:
        code = generate_captcha_code()
        session['captcha_code'] = code
        logger.info(f"📝 Código guardado: {code}")
        
        # ... generación SVG ...
        
        logger.info(f"✅ CAPTCHA generado. Longitud: {len(data_uri)}")
        response = jsonify({'success': True, 'image': data_uri})
        logger.info("✅ Respuesta JSON creada")
        return response
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Pasos para Resolver

### Paso 1: Verificar SECRET_KEY en Railway

1. Ir a: Railway Dashboard → Tu Proyecto → Variables
2. Buscar: `SECRET_KEY`
3. Si NO existe, crear:
   ```
   SECRET_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```
   (Generar una clave larga y aleatoria)

4. Si existe, asegurar que sea la MISMA en todos los deploys

### Paso 2: Verificar logs de Railway

```bash
railway logs
```

Buscar:
- `✅ CAPTCHA SVG generado`
- `✅ Respuesta JSON creada`
- Cualquier error o warning

### Paso 3: Solución temporal si persiste

Modificar el login para NO requerir CAPTCHA (temporalmente):

```python
# En app.py, comentar validación CAPTCHA:
# if not validate_captcha_session(session, captcha_input):
#     flash('Código CAPTCHA incorrecto.')
#     return render_template('login.html')
```

## Verificación Post-Deploy

```bash
# Verificar que el endpoint funciona:
curl https://web-production-adfd.up.railway.app/generate_captcha

# Debería retornar:
# {"success": true, "image": "data:image/svg+xml;base64,PHN2Zy..."}
```

## Deploy de Cambios

```bash
git add app.py
git commit -m "Fix CAPTCHA generation: limpieza de código y más logging"
git push origin main
```

Railway hará auto-deploy. Esperar 1-2 minutos y volver a probar.

## Si el Problema Persiste

**Opción A: Deshabilitar CAPTCHA temporalmente**
- Comentar validación de CAPTCHA en login
- Solo para admin (ya implementado)

**Opción B: Usar CAPTCHA más simple**
- Cambiar de SVG a imagen PNG estática
- O usar texto plano sin encoding

**Opción C: Implementar sesiones con Redis**
- Requiere configurar Redis en Railway
- Usar Flask-Session con RedisSessionInterface

## Estado Actual

✅ Código limpiado y mejorado  
⏳ Pendiente: verificar SECRET_KEY en Railway  
⏳ Pendiente: revisar logs después del deploy  
✅ Admin puede hacer login sin CAPTCHA (bypass implementado)  
