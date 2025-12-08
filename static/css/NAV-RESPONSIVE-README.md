# Guía de Uso: nav-responsive.css

## 📋 Descripción
Archivo CSS global que contiene todos los estilos estandarizados para el header, navegación y responsive de La Esquinita.

---

## 🚀 Cómo Implementar en un Archivo HTML

### Paso 1: Agregar el link al CSS en el `<head>`

```html
<head>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/nav-responsive.css') }}">
  <!-- Resto de tus estilos... -->
</head>
```

### Paso 2: Usar la estructura HTML estándar

```html
<header>
  <div class="logo">
    <img src="{{ url_for('static', filename='images/laesquinita.png') }}" alt="La Esquinita">
  </div>
  <nav>
    <!-- Tus enlaces aquí -->
    <a href="{{ url_for('inicio') }}">
      <img src="{{ url_for('static', filename='images/inicio.png') }}" alt="Inicio">
      Inicio
    </a>
    <a href="{{ url_for('productos') }}">
      <img src="{{ url_for('static', filename='images/esquite.png') }}" alt="Tienda">
      Tienda
    </a>
    <!-- Más enlaces... -->
  </nav>
</header>
```

### Paso 3: Eliminar estilos duplicados

Busca y **ELIMINA** de tu archivo HTML los siguientes estilos (ya están en nav-responsive.css):

❌ Eliminar:
- Estilos de `header { }`
- Estilos de `.logo { }`
- Estilos de `.logo img { }`
- Estilos de `nav { }`
- Estilos de `nav a { }`
- Estilos de `nav a img { }`
- Estilos de `nav a:hover { }`
- Media queries de header/nav (`@media(max-width:1024px)`, `768px`, `600px`, `480px`, `375px`, landscape)

---

## ✅ Archivos Ya Implementados

Los siguientes archivos **YA tienen** los estilos correctos y solo necesitan agregar el link al CSS:

1. ✅ inicio.html
2. ✅ productos.html
3. ✅ contacto.html
4. ✅ carrito.html
5. ✅ login.html
6. ✅ registro.html
7. ✅ actualizar_producto_admin.html
8. ✅ gestion_usuarios.html

---

## 📐 Especificaciones Técnicas

### Tamaños del Logo por Resolución:
- **Desktop (>1024px)**: 60px
- **Tablet (1024px)**: 50px
- **Tablet pequeña (768px)**: 46px
- **Móvil mediano (600px)**: 48px
- **Móvil pequeño (480px)**: 50px
- **iPhone SE (375px)**: 36px
- **Landscape**: 35px

### Tamaños de Iconos del Nav:
- **Desktop**: 26px × 26px
- **Tablet (1024px)**: 22px × 22px
- **Tablet pequeña (768px)**: 20px × 20px
- **Móvil (600px)**: 28px × 28px
- **Móvil pequeño (480px)**: 32px × 32px

### Márgenes Superiores para Contenido:

**Para elementos tipo .hero o .banner:**
- 768px: margin-top 140px
- 600px: margin-top 180px
- 480px: margin-top 220px
- 375px: margin-top 200px

**Para elementos tipo .container:**
- 1024px: margin-top 140px
- 768px: margin-top 160px
- 600px: margin-top 180px
- 480px: margin-top 230px
- 375px: margin-top 220px

**Landscape:** margin-top 60px (ambos tipos)

---

## 🎨 Variables CSS Requeridas

Asegúrate de tener estas variables CSS definidas en tu archivo:

```css
:root {
  --primary: #ffb300;
  --secondary: #2e7d32;
  --accent: #ff5722;
  --light: #fffdf7;
  --dark: #1c1c1c;
}
```

---

## 🔧 Ajustes Específicos por Página

Si tu página tiene necesidades específicas de margen, puedes agregar después del link:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/nav-responsive.css') }}">
<style>
  /* Ajustes específicos solo para esta página */
  @media(max-width:600px){
    .mi-contenedor-especial {
      margin-top: 200px; /* Ajuste personalizado */
    }
  }
</style>
```

---

## ⚠️ Importante

1. **Siempre incluir el link ANTES** de tus estilos personalizados
2. **No modificar** nav-responsive.css para cambios de una sola página
3. **Usar clases específicas** si necesitas sobrescribir estilos
4. El archivo funciona con la estructura `header > logo + nav`

---

## 🐛 Solución de Problemas

### El nav se ve diferente
- ✅ Verifica que el link al CSS esté correcto
- ✅ Asegúrate de haber eliminado estilos duplicados
- ✅ Revisa que uses la estructura HTML correcta

### El contenido queda cubierto
- ✅ Asegúrate de que tu contenedor principal tenga clase `.hero` o `.container`
- ✅ Verifica que no tengas `margin-top: 0` sobrescribiendo los estilos

### Los iconos se ven muy grandes/pequeños
- ✅ Verifica que las imágenes usen las clases correctas
- ✅ No agregues estilos inline de width/height a las imágenes

---

## 📞 Contacto

Para dudas o mejoras al sistema de navegación, consulta con el equipo de desarrollo.

**Última actualización:** Diciembre 2025
