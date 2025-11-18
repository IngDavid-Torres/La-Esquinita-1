"""
Guía para ver los logs de Railway y diagnosticar el problema

OPCIÓN 1: Ver logs directamente en Railway Dashboard
====================================================
1. Ve a: https://railway.app/
2. Ingresa a tu proyecto "La Esquinita"
3. Click en el servicio (deployment)
4. Click en "Deployments" tab
5. Click en el deployment más reciente (debería decir "a546fd7")
6. Click en "View Logs"
7. **Busca estos mensajes cuando intentes hacer login:**
   - "🚀 INICIO DE PROCESO DE LOGIN"
   - "✅ ADMIN ENCONTRADO"
   - "📝 Session configurada"
   - "🎯 PANEL_ADMIN ACCEDIDO"
   - "🔍 Session actual COMPLETA"


OPCIÓN 2: Usar Railway CLI para ver logs en tiempo real
========================================================
En PowerShell, ejecuta:

1. Instalar Railway CLI (si no lo tienes):
   npm install -g @railway/cli

2. Login:
   railway login

3. Link al proyecto:
   railway link

4. Ver logs en tiempo real:
   railway logs


QUÉS BUSCAR EN LOS LOGS
=========================
Cuando intentes hacer login con admin@laesquinita.com, deberías ver:

✅ SI FUNCIONA:
   🚀 INICIO DE PROCESO DE LOGIN
   📧 Email recibido: 'admin@laesquinita.com'
   🔑 Password recibido: 'admin123'
   🔍 Buscando admin en base de datos...
   ✅ ADMIN ENCONTRADO: Admin (ID: 1)
   📝 Session configurada: {'usuario_id': 1, 'usuario_nombre': 'Admin', 'tipo_usuario': 'Administrador', '_permanent': True}
   📤 ENVIANDO REDIRECT A PANEL_ADMIN
   🎯 PANEL_ADMIN ACCEDIDO
   🔍 Session actual COMPLETA: {'usuario_id': 1, 'tipo_usuario': 'Administrador', ...}
   ✅ Admin autenticado accediendo a panel: Admin

❌ SI FALLA (sesión no persiste):
   🚀 INICIO DE PROCESO DE LOGIN
   ✅ ADMIN ENCONTRADO
   📝 Session configurada: {...}
   🎯 PANEL_ADMIN ACCEDIDO
   🔍 Session actual COMPLETA: {}  ← VACÍA!
   ⚠️ ACCESO DENEGADO a panel_admin


POSIBLES PROBLEMAS Y SOLUCIONES
================================

PROBLEMA 1: Session vacía en panel_admin
CAUSA: SECRET_KEY no configurada o diferente
SOLUCIÓN: Configurar SECRET_KEY en Railway:
   1. Ve a tu proyecto en Railway
   2. Click en "Variables"
   3. Agrega: SECRET_KEY = [tu_clave_secreta_super_larga]
   4. Redeploy

PROBLEMA 2: Cookies no se guardan
CAUSA: SESSION_COOKIE_SECURE = True pero usando HTTP
SOLUCIÓN: Railway usa HTTPS, debería funcionar
   Verificar que la URL sea https://...

PROBLEMA 3: SameSite=Lax bloquea cookies
CAUSA: Configuración de cookies muy restrictiva
SOLUCIÓN: Ya está configurada correctamente en app.py


PRUEBA RÁPIDA
=============
Para verificar que Railway deployó correctamente:

python -c "import requests; r = requests.get('https://web-production-adfd.up.railway.app/health'); print(r.json() if r.status_code == 200 else f'Error: {r.status_code}')"

Debería responder: {'status': 'healthy'}
"""

print(__doc__)
