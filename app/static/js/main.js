/**
 * FarmaSegura - Script principal
 * Versión: 2.0 - Optimizado y mejorado
 * Funcionalidades: sidebar responsive, modo oscuro, tooltips, confirmaciones, notificaciones toasts, etc.
 */

// ========================================================
// 1. Esperar a que el DOM esté completamente cargado
// ========================================================
document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================================
    // 2. Sidebar toggle para dispositivos móviles
    // ========================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('show');
            
            // Cambiar ícono del botón (opcional)
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
        
        // Cerrar sidebar al hacer clic fuera (en móviles)
        document.addEventListener('click', function(event) {
            const isMobile = window.innerWidth < 992;
            if (isMobile && sidebar.classList.contains('show')) {
                if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                    sidebar.classList.remove('show');
                    const icon = sidebarToggle.querySelector('i');
                    if (icon) {
                        icon.classList.add('fa-bars');
                        icon.classList.remove('fa-times');
                    }
                }
            }
        });
    }

    // ========================================================
    // 3. Modo oscuro persistente (con localStorage y compatibilidad)
    // ========================================================
    (function initDarkMode() {
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
                
                // Emitir evento para que otros componentes puedan reaccionar
                window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: next } }));
            });
        }
    })();

    // ========================================================
    // 4. Inicializar tooltips de Bootstrap
    // ========================================================
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function(tooltipTriggerEl) {
            // Evitar duplicados
            if (!tooltipTriggerEl.hasAttribute('data-bs-original-title')) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }
            return null;
        });
    }
    initTooltips();

    // ========================================================
    // 5. Confirmación personalizada para eliminaciones
    // ========================================================
    function initDeleteConfirmation() {
        // Para elementos con data-confirm
        const deleteButtons = document.querySelectorAll('[data-confirm]');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm') || '¿Estás seguro de realizar esta acción?';
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
                const nombreSpan = document.getElementById('deleteNombre');
                
                if (deleteForm && url) {
                    deleteForm.action = url;
                }
                if (nombreSpan && nombre) {
                    nombreSpan.innerText = nombre;
                }
            });
        }
    }
    initDeleteConfirmation();

    // ========================================================
    // 6. Resaltado de enlace activo en el sidebar
    // ========================================================
    function highlightActiveSidebarLink() {
        const currentUrl = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#') {
                // Remover clase active de todos
                link.classList.remove('active');
                
                // Comparar URL exacta o si es subruta
                if (currentUrl === href || (href !== '/' && currentUrl.startsWith(href))) {
                    link.classList.add('active');
                }
            }
        });
    }
    highlightActiveSidebarLink();

    // ========================================================
    // 7. Cierre automático de mensajes flash (alertas)
    // ========================================================
    function initAutoCloseAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.classList.add('fade');
                setTimeout(() => {
                    if (alert.parentNode) alert.remove();
                }, 300);
            }, 5000);
        });
    }
    initAutoCloseAlerts();

    // ========================================================
    // 8. Sistema de Toasts (notificaciones flotantes)
    // ========================================================
    window.FarmaSegura = window.FarmaSegura || {};
    window.FarmaSegura.showToast = function(message, type = 'success', duration = 3000) {
        const toastContainer = document.querySelector('.toast-container') || (() => {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1100';
            document.body.appendChild(container);
            return container;
        })();
        
        const toastId = 'toast-' + Date.now();
        const icon = type === 'success' ? 'fa-check-circle' : (type === 'danger' ? 'fa-exclamation-triangle' : 'fa-info-circle');
        const bgClass = type === 'success' ? 'bg-success' : (type === 'danger' ? 'bg-danger' : 'bg-info');
        
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="${duration}">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${icon} me-2"></i> ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: duration });
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    };

    // ========================================================
    // 9. Función para recargar badges de notificaciones (AJAX)
    // ========================================================
    window.FarmaSegura.updateNotificationBadge = function() {
        fetch('/api/notificaciones/count')
            .then(response => response.json())
            .then(data => {
                const badge = document.querySelector('.fc-notif-badge');
                if (badge) {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.style.display = 'flex';
                    } else {
                        badge.style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error al actualizar notificaciones:', error));
    };

    // ========================================================
    // 10. Mejoras de accesibilidad y UX
    // ========================================================
    
    // Enfocar primer campo de formulario automáticamente
    const firstFormInput = document.querySelector('.modal.show input:not([type=hidden]), form:not(.no-autofocus) input:not([type=hidden]):first-of-type');
    if (firstFormInput) {
        firstFormInput.focus();
    }
    
    // Prevenir envío doble de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.classList.contains('btn')) {
                submitBtn.disabled = true;
                setTimeout(() => { submitBtn.disabled = false; }, 3000);
            }
        });
    });

    // ========================================================
    // 11. Manejo de errores de red (conexión perdida)
    // ========================================================
    window.addEventListener('offline', function() {
        window.FarmaSegura.showToast('Se perdió la conexión a Internet. Algunas funciones pueden no estar disponibles.', 'warning', 5000);
    });
    
    window.addEventListener('online', function() {
        window.FarmaSegura.showToast('Conexión restablecida correctamente.', 'success', 3000);
    });

}); // Fin DOMContentLoaded

// ========================================================
// 12. Precarga de preferencias antes del render (modo oscuro)
// ========================================================
(function preloadTheme() {
    const savedTheme = localStorage.getItem('fcTheme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }
})();