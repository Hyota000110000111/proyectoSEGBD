/**
 * FarmaSegura - Script principal
 * Funcionalidades: sidebar responsive, modo oscuro, tooltips, confirmaciones, etc.
 */

// ========================================================
// 1. Sidebar toggle para dispositivos móviles
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebar.classList.toggle('show');
      }
    });
  }
});

// ========================================================
// 2. Modo oscuro persistente (con localStorage y compatibilidad)
// ========================================================
// Modo oscuro persistente
(function() {
  const savedTheme = localStorage.getItem('fcTheme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-bs-theme', initialTheme);
  const themeIcon = document.getElementById('theme-icon');
  if (themeIcon) {
    themeIcon.className = initialTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const current = document.documentElement.getAttribute('data-bs-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-bs-theme', next);
      localStorage.setItem('fcTheme', next);
      if (themeIcon) {
        themeIcon.className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
    });
  }
})();

// ========================================================
// 3. Inicializar tooltips de Bootstrap (con data-bs-toggle="tooltip")
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// ========================================================
// 4. Confirmación personalizada para formularios de eliminación
//    Busca cualquier formulario con clase 'confirm-delete' o data-confirm
//    También maneja el modal global de eliminación (deleteModal)
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
  // Confirmación simple con confirm nativo (para enlaces o formularios)
  const deleteButtons = document.querySelectorAll('[data-confirm]');
  deleteButtons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      const message = this.getAttribute('data-confirm') || '¿Estás seguro?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });
  
  // Manejo del modal genérico de eliminación (si existe)
  const deleteModal = document.getElementById('deleteModal');
  if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const nombre = button.getAttribute('data-nombre') || '';
      const url = button.getAttribute('data-url');
      const deleteForm = document.getElementById('deleteForm');
      if (deleteForm) {
        deleteForm.action = url;
        const nombreSpan = document.getElementById('deleteNombre');
        if (nombreSpan) nombreSpan.innerText = nombre;
      }
    });
  }
});

// ========================================================
// 5. Resaltado de enlace activo en el sidebar (opcional)
//    Ya se puede hacer con clases en el HTML usando request.endpoint,
//    este script lo refuerza comparando la URL actual.
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
  const currentUrl = window.location.pathname;
  const navLinks = document.querySelectorAll('.sidebar .nav-link');
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && currentUrl === href) {
      link.classList.add('active');
    } else if (href && href !== '#' && currentUrl.startsWith(href) && href !== '/') {
      // Para rutas con subrutas, ej: /admin/empleados coincide con /admin
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
});

// ========================================================
// 6. Cierre automático de mensajes flash (alertas de Bootstrap)
//    Opcional: desaparecen después de 5 segundos
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      // Añadir clase fade y luego eliminar del DOM después de la transición
      alert.classList.add('fade');
      setTimeout(() => {
        if (alert.parentNode) alert.remove();
      }, 300);
    }, 5000);
  });
});

// ========================================================
// 7. Funciones auxiliares (puedes agregar más según necesites)
// ========================================================
window.fs = window.fs || {};
window.fs.showToast = function(message, type = 'success') {
  // Implementar un sistema de toasts si lo deseas
  console.log(`[${type}] ${message}`);
};