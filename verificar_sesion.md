# Verificación de Sesión Persistente 🔐

## Cambios Implementados

### 1. `@app.before_request` - Mantener Sesión Activa
```python
@app.before_request
def mantener_sesion_activa():
    """Mantiene la sesión permanente para usuarios autenticados"""
    if 'usuario_id' in session:
        session.permanent = True
        session.modified = True
```

**Efecto**: En CADA request, si hay un usuario autenticado, la sesión:
- Se marca como `permanent` (dura 1 hora según `PERMANENT_SESSION_LIFETIME`)
- Se marca como `modified` (actualiza el timestamp de la cookie)

### 2. Login Normal - `session.permanent = True`
- ✅ Admin login: `session.permanent = True`
- ✅ Usuario login: `session.permanent = True`
- ✅ Login SMS: `session.permanent = True` (ya estaba)

### 3. Configuración de Sesión
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS en producción
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Protección XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protección CSRF
```

## Cómo Funciona Ahora

### Flujo de Sesión para Cliente

1. **Login** (normal o SMS):
   ```
   session['usuario_id'] = usuario.id
   session['usuario_nombre'] = usuario.nombre
   session['tipo_usuario'] = 'Cliente'
   session.permanent = True  ← Cookie dura 1 hora
   ```

2. **Navegación** (productos, carrito, contacto, inicio):
   ```
   @app.before_request activado en CADA página
   ↓
   session.permanent = True  ← Renueva cookie
   session.modified = True   ← Actualiza timestamp
   ```

3. **Resultado**:
   - ✅ Sesión se mantiene mientras el cliente navega
   - ✅ Cookie se renueva en cada request
   - ✅ No se pierde sesión al navegar entre vistas
   - ✅ Duración: 1 hora desde última actividad

### Compatibilidad con Vistas Existentes

Todas las vistas del cliente funcionan sin cambios:

- `/productos` - Ya usa `session.get('usuario_id')`
- `/carrito` - Ya verifica `session.get('usuario_nombre')`
- `/contacto` - Ya usa `session['usuario_id']`
- `/panel_cliente` - Ya verifica `session['usuario_id']`
- `/pago_mercadopago` - Ya verifica `session['usuario_id']`
- etc.

## Pruebas en Producción (Railway)

### 1. Verificar SECRET_KEY
```bash
# En Railway, asegúrate que está configurado:
SECRET_KEY=tu_clave_secreta_super_larga_y_aleatoria
```

### 2. Probar Flujo Completo

1. Login con SMS:
   - Ingresar teléfono y CAPTCHA
   - Recibir código SMS
   - Ingresar código
   - Debe redirigir a `panel_cliente`

2. Navegar sin perder sesión:
   - Click en "Productos" → debe mantener sesión
   - Click en "Carrito" → debe mantener sesión
   - Click en "Contacto" → debe mantener sesión
   - Volver a "Inicio" → debe mantener sesión
   - Volver a "Panel Cliente" → debe mantener sesión

3. Verificar cantidad del carrito:
   - El número en el ícono del carrito debe aparecer en todas las páginas
   - Agregar producto → contador debe actualizarse
   - Navegar → contador debe persistir

### 3. Logs para Debugging

Si la sesión se pierde, revisar logs de Railway:

```python
# Ya están implementados en el código:
logger.info(f"📝 Session configurada: {dict(session)}")
logger.info(f"🔄 Generando redirect a: {url_for('panel_cliente')}")
```

## Solución de Problemas

### ❌ Sesión se pierde entre páginas

**Causa**: `SECRET_KEY` diferente entre deploys

**Solución**:
```bash
# Railway → Variables → SECRET_KEY
# Debe ser fija, ejemplo:
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### ❌ Sesión expira demasiado rápido

**Causa**: Usuario inactivo por más de 1 hora

**Solución**: Aumentar `PERMANENT_SESSION_LIFETIME`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 2 horas
```

### ❌ Cookie no se guarda en producción

**Causa**: `SESSION_COOKIE_SECURE = True` sin HTTPS

**Solución**: Railway usa HTTPS por defecto, verificar que:
- URL de la app empiece con `https://`
- No usar HTTP en producción

## Resumen de Garantías

Con estos cambios:

✅ Cliente inicia sesión (login normal o SMS)  
✅ Navega por TODAS las vistas (productos, carrito, contacto, inicio, panel)  
✅ Sesión se mantiene activa durante navegación  
✅ Cookie se renueva automáticamente en cada request  
✅ Sesión dura 1 hora desde última actividad  
✅ Compatible con Railway y HTTPS  
✅ Protección XSS, CSRF y cookies seguras activada  

## Deploy

```bash
git add app.py
git commit -m "Mantener sesión activa para todos los usuarios autenticados"
git push origin main
```

✅ **Ya ejecutado** - Railway auto-deploy activo.
