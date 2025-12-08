// --- ACCESIBILIDAD GLOBAL CON PERSISTENCIA ---

// --- MANEJO DEL BOTÓN TOGGLE ---
window.addEventListener('load', function() {
  const toggleBtn = document.getElementById('accesibilidadToggle');
  const accesBar = document.querySelector('.accesibilidad-bar');
  
  if(toggleBtn && accesBar) {
    // CRÍTICO: Evitar que clicks dentro del panel lo cierren
    accesBar.addEventListener('click', function(e) {
      e.stopPropagation();
    });
    accesBar.addEventListener('mousedown', function(e) {
      e.stopPropagation();
    });
    accesBar.addEventListener('touchstart', function(e) {
      e.stopPropagation();
    });
    
    // Prevenir scroll cuando se interactúa con el panel
    accesBar.addEventListener('wheel', function(e) {
      e.stopPropagation();
    });
    
    // Cargar estado del panel
    const panelVisible = localStorage.getItem('acc_panelVisible') === 'true';
    if(panelVisible) {
      accesBar.classList.add('show');
      toggleBtn.classList.add('active');
    }
    
    toggleBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      const isVisible = accesBar.classList.toggle('show');
      this.classList.toggle('active');
      localStorage.setItem('acc_panelVisible', isVisible);
    });
  }
});

// Esperar a que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  const root = document.documentElement;
  const body = document.body;

  // Cargar configuración guardada (MEJORADO con contrasteValor)
  let config = {
    fontSize: parseFloat(localStorage.getItem('acc_fontSize')) || 1,
    modoNocturno: localStorage.getItem('acc_modoNocturno') === 'true',
    contraste: localStorage.getItem('acc_contraste') === 'true',
    contrasteValor: parseFloat(localStorage.getItem('acc_contrasteValor')) || 1,
    grises: localStorage.getItem('acc_grises') === 'true',
    guiaLectura: false, // NO persistir guía de lectura
    tipografia: localStorage.getItem('acc_tipografia') || 'default'
  };

  // Guardar configuración (MEJORADO con contrasteValor)
  function guardarConfig() {
    localStorage.setItem('acc_fontSize', config.fontSize);
    localStorage.setItem('acc_modoNocturno', config.modoNocturno);
    localStorage.setItem('acc_contraste', config.contraste);
    localStorage.setItem('acc_contrasteValor', config.contrasteValor);
    localStorage.setItem('acc_grises', config.grises);
    localStorage.setItem('acc_tipografia', config.tipografia);
    // guiaLectura NO se guarda (es temporal)
  }

  // Aplicar tipografía
  function aplicarTipografia(tipo) {
    switch(tipo) {
      case 'arial': body.style.fontFamily = 'Arial, sans-serif'; break;
      case 'verdana': body.style.fontFamily = 'Verdana, Geneva, sans-serif'; break;
      case 'comic': body.style.fontFamily = 'Comic Sans MS, Comic Sans, cursive'; break;
      case 'open': body.style.fontFamily = 'OpenDyslexic, Arial, sans-serif'; break;
      default: body.style.fontFamily = '';
    }
  }

  // Aplicar modo nocturno
  function aplicarModoNocturno(activar) {
    const mainContent = document.querySelector('.dashboard-main');
    const container = document.querySelector('.dashboard-container');
    const cards = document.querySelectorAll('.card');
    const actions = document.querySelectorAll('.action-box');
    const graphs = document.querySelectorAll('.graph-box');
    const dashboardHeader = document.querySelector('.dashboard-header');
    const footer = document.querySelector('footer');
    const accesBar = document.querySelector('.accesibilidad-bar');
    
    if(activar) {
      body.classList.add('night-mode');
      body.style.background = '#181818';
      body.style.color = '#fff';
      
      // Aplicar a elementos específicos del dashboard si existen
      if(mainContent) mainContent.classList.add('night-mode');
      if(container) container.classList.add('night-mode');
      cards.forEach(e => e.classList.add('night-mode'));
      actions.forEach(e => e.classList.add('night-mode'));
      graphs.forEach(e => e.classList.add('night-mode'));
      if(dashboardHeader) dashboardHeader.classList.add('night-mode');
      if(footer) footer.classList.add('night-mode');
      if(accesBar) accesBar.classList.add('night-mode');
    } else {
      body.classList.remove('night-mode');
      body.style.background = '';
      body.style.color = '';
      
      if(mainContent) mainContent.classList.remove('night-mode');
      if(container) container.classList.remove('night-mode');
      cards.forEach(e => e.classList.remove('night-mode'));
      actions.forEach(e => e.classList.remove('night-mode'));
      graphs.forEach(e => e.classList.remove('night-mode'));
      if(dashboardHeader) dashboardHeader.classList.remove('night-mode');
      if(footer) footer.classList.remove('night-mode');
      if(accesBar) accesBar.classList.remove('night-mode');
    }
  }

  // Función para actualizar filtros combinados (MEJORADO)
  function actualizarFiltros() {
    let filtros = [];
    if(config.contraste) filtros.push(`contrast(${config.contrasteValor})`);
    if(config.grises) filtros.push('grayscale(1)');
    
    const filtroFinal = filtros.join(' ');
    
    // Aplicar al html y body con !important
    if(filtroFinal) {
      document.documentElement.style.setProperty('filter', filtroFinal, 'important');
      body.style.setProperty('filter', filtroFinal, 'important');
    } else {
      document.documentElement.style.removeProperty('filter');
      body.style.removeProperty('filter');
    }
  }

  // Aplicar configuración al cargar la página (MEJORADO)
  function aplicarConfiguracion() {
    // Tamaño de letra
    body.style.fontSize = config.fontSize + 'em';
    
    // Modo nocturno
    if(config.modoNocturno) {
      aplicarModoNocturno(true);
      const btnNocturno = document.getElementById('modoNocturnoBtn');
      if(btnNocturno) btnNocturno.classList.add('active');
    }
    
    // Contraste (MEJORADO con range value)
    if(config.contraste) {
      const btnContraste = document.getElementById('contrasteBtn');
      const contrasteRange = document.getElementById('contrasteRange');
      if(btnContraste) btnContraste.classList.add('active');
      if(contrasteRange) {
        contrasteRange.disabled = false;
        contrasteRange.value = config.contrasteValor;
      }
    }
    
    // Escala de grises
    if(config.grises) {
      const btnGrises = document.getElementById('grisesBtn');
      if(btnGrises) btnGrises.classList.add('active');
    }
    
    // Aplicar filtros combinados
    actualizarFiltros();
    
    // Guía de lectura (NO se carga porque no se persiste)
    
    // Tipografía
    aplicarTipografia(config.tipografia);
    const selectTipo = document.getElementById('tipografiaSelect');
    if(selectTipo) selectTipo.value = config.tipografia;
  }

  // Event Listeners

  // Aumentar letra
  const btnAumentar = document.getElementById('aumentarLetraBtn');
  if(btnAumentar) {
    btnAumentar.onclick = () => {
      config.fontSize = Math.max(0.7, Math.min(2.2, config.fontSize * 1.15));
      body.style.fontSize = config.fontSize + 'em';
      guardarConfig();
    };
  }

  // Disminuir letra
  const btnDisminuir = document.getElementById('disminuirLetraBtn');
  if(btnDisminuir) {
    btnDisminuir.onclick = () => {
      config.fontSize = Math.max(0.7, Math.min(2.2, config.fontSize * 0.87));
      body.style.fontSize = config.fontSize + 'em';
      guardarConfig();
    };
  }

  // Modo nocturno
  const btnNocturno = document.getElementById('modoNocturnoBtn');
  if(btnNocturno) {
    btnNocturno.onclick = function() {
      config.modoNocturno = !config.modoNocturno;
      aplicarModoNocturno(config.modoNocturno);
      
      if(config.modoNocturno) {
        this.classList.add('active');
      } else {
        this.classList.remove('active');
      }
      
      guardarConfig();
    };
  }
  // Contraste alto con range
  const btnContraste = document.getElementById('contrasteBtn');
  const contrasteRange = document.getElementById('contrasteRange');
  
  if(btnContraste && contrasteRange) {
    btnContraste.onclick = function(e) {
      e.stopPropagation();
      config.contraste = !config.contraste;
      
      if(config.contraste) {
        config.contrasteValor = parseFloat(contrasteRange.value);
        contrasteRange.disabled = false;
        this.classList.add('active');
      } else {
        contrasteRange.disabled = true;
        this.classList.remove('active');
      }
      
      actualizarFiltros();
      guardarConfig();
    };
    
    contrasteRange.oninput = function(e) {
      e.stopPropagation();
      config.contrasteValor = parseFloat(this.value);
      if(config.contraste) {
        actualizarFiltros();
        guardarConfig();
      }
    };
    
    contrasteRange.onmousedown = function(e) {
      e.stopPropagation();
    };
    
    contrasteRange.ontouchstart = function(e) {
      e.stopPropagation();
    };
    
    // Restaurar estado del contraste
    if(config.contraste) {
      contrasteRange.disabled = false;
      btnContraste.classList.add('active');
      contrasteRange.value = config.contrasteValor;
    } else {
      contrasteRange.disabled = true;
    }
  }

  // Escala de grises
  const btnGrises = document.getElementById('grisesBtn');
  if(btnGrises) {
    btnGrises.onclick = function() {
      config.grises = !config.grises;
      this.classList.toggle('active', config.grises);
      actualizarFiltros();
      guardarConfig();
    };
    
    // Restaurar estado
    if(config.grises) {
      btnGrises.classList.add('active');
    }
  }

  // Guía de lectura (NO se persiste, es temporal por sesión)
  const btnGuia = document.getElementById('guiaLecturaBtn');
  if(btnGuia) {
    btnGuia.onclick = function() {
      config.guiaLectura = !config.guiaLectura;
      let contenido = document.querySelector('.dashboard-main') || document.getElementById('contenido-principal') || document.body;
      
      if(config.guiaLectura) {
        contenido.style.boxShadow = '0 0 0 9999px rgba(0,0,0,0.7)';
        contenido.style.background = '#fffbe7';
        if(contenido.scrollIntoView) {
          contenido.scrollIntoView({behavior:'smooth', block:'center'});
        }
        this.classList.add('active');
      } else {
        contenido.style.boxShadow = '';
        contenido.style.background = '';
        this.classList.remove('active');
      }
      
      // NO guardamos guiaLectura (es intencional que sea temporal)
    };
  }

  // Cambiar tipografía
  const selectTipo = document.getElementById('tipografiaSelect');
  if(selectTipo) {
    selectTipo.onchange = function() {
      config.tipografia = this.value;
      aplicarTipografia(config.tipografia);
      guardarConfig();
    };
  }

  // Lector de pantalla (no se guarda porque es temporal)
  const btnLector = document.getElementById('lectorPantallaBtn');
  if(btnLector) {
    btnLector.onclick = function() {
      let lectorActivo = this.classList.contains('active');
      lectorActivo = !lectorActivo;
      let contenido = document.querySelector('.dashboard-main') || document.getElementById('contenido-principal') || document.body;
      
      if(lectorActivo) {
        this.classList.add('active');
        let texto = contenido.innerText;
        if('speechSynthesis' in window) {
          let utter = new SpeechSynthesisUtterance(texto);
          utter.lang = 'es-MX';
          window.speechSynthesis.speak(utter);
        } else {
          alert('Lector de pantalla no soportado en este navegador.');
        }
      } else {
        this.classList.remove('active');
        if('speechSynthesis' in window) window.speechSynthesis.cancel();
      }
    };
  }

  // Aplicar configuración guardada al cargar
  aplicarConfiguracion();
});