function destructiveLogout(userType = 'general') {
    const confirmMessage = userType === 'admin' 
        ? '🔐 ¿Confirmar cierre TOTAL de sesión de Administrador?\n\nEsto eliminará:\n• Todos los datos de sesión\n• Cookies de autenticación\n• Caché del navegador\n• Datos temporales\n\n⚠️ Acción irreversible'
        : userType === 'cliente'
        ? '🛒 ¿Confirmar cierre TOTAL de sesión de Cliente?\n\nEsto eliminará:\n• Carrito de compras temporal\n• Datos de sesión\n• Información de pago guardada\n• Preferencias temporales\n\n⚠️ Tendrás que volver a iniciar sesión'
        : '💥 ¿Confirmar DESTRUCCIÓN TOTAL de sesión?\n\nEsto eliminará:\n• TODOS los datos de sesión\n• Todas las cookies\n• Todo el caché\n• Datos locales y temporales\n\n⚠️ Acción de máxima seguridad - irreversible';

    if (confirm(confirmMessage)) {
        clearAllBrowserData();
        
        let logoutUrl = '/logout';
        if (userType === 'admin') {
            logoutUrl = '/logout/admin';
        } else if (userType === 'cliente') {
            logoutUrl = '/logout/cliente';
        } else if (userType === 'force') {
            logoutUrl = '/logout/force';
        }
        
        window.location.href = logoutUrl;
    }
}

function clearAllBrowserData() {
    if (typeof(Storage) !== "undefined") {
        localStorage.clear();
        sessionStorage.clear();
    }
    
    if (navigator.serviceWorker) {
        navigator.serviceWorker.getRegistrations().then(function(registrations) {
            for(let registration of registrations) {
                registration.unregister();
            }
        });
    }
    
    if ('caches' in window) {
        caches.keys().then(function(names) {
            for (let name of names) {
                caches.delete(name);
            }
        });
    }
    
    document.cookie.split(";").forEach(function(c) { 
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
    });
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => form.reset());
    
    if (window.history && window.history.replaceState) {
        window.history.replaceState(null, null, window.location.pathname);
    }
}

function autoLogoutWarning(userType = 'general') {
    const warningTime = 25 * 60 * 1000;
    const logoutTime = 30 * 60 * 1000;
    
    setTimeout(() => {
        const warning = confirm('⏰ Tu sesión expirará en 5 minutos por inactividad.\n\n¿Deseas mantener tu sesión activa?');
        if (!warning) {
            destructiveLogout(userType);
        } else {
            fetch('/keep-alive', { method: 'POST' });
        }
    }, warningTime);
    
    setTimeout(() => {
        alert('🔒 Sesión cerrada automáticamente por inactividad por seguridad.');
        destructiveLogout('force');
    }, logoutTime);
}

function securePageUnload() {
    window.addEventListener('beforeunload', function() {
        if (sessionStorage.getItem('auto_logout_on_close') === 'true') {
            navigator.sendBeacon('/logout/force');
        }
    });
}

function enableAutoLogoutOnClose() {
    sessionStorage.setItem('auto_logout_on_close', 'true');
    securePageUnload();
}

function disableAutoLogoutOnClose() {
    sessionStorage.setItem('auto_logout_on_close', 'false');
}

document.addEventListener('DOMContentLoaded', function() {
    const userType = document.body.getAttribute('data-user-type') || 'general';
    
    const logoutButtons = document.querySelectorAll('[data-logout-type]');
    logoutButtons.forEach(button => {
        const logoutType = button.getAttribute('data-logout-type');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            destructiveLogout(logoutType);
        });
    });
    
    const autoLogoutEnabled = document.body.getAttribute('data-auto-logout') === 'true';
    if (autoLogoutEnabled) {
        autoLogoutWarning(userType);
    }
    
    const forceLogoutOnClose = document.body.getAttribute('data-force-logout-close') === 'true';
    if (forceLogoutOnClose) {
        enableAutoLogoutOnClose();
    }
});