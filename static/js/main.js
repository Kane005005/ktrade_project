// Fonctions utilitaires
function showAlert(message, type = 'info') {
    const alerts = document.getElementById('alerts-container');
    if (!alerts) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-message">${message}</span>
        <button class="close-alert" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alerts.appendChild(alert);
    
    // Auto-supprimer après 5 secondes
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// Formatage de prix
function formatPrice(amount, currency = 'USD') {
    const formatter = new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    return formatter.format(amount);
}

// Validation d'email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Debounce pour la recherche
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Menu mobile
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navOverlay = document.querySelector('.nav-overlay');
    const body = document.body;
    
    if (navLinks) {
        navLinks.classList.toggle('show');
        
        if (navLinks.classList.contains('show')) {
            body.style.overflow = 'hidden';
            mobileMenuBtn.innerHTML = '<i class="fas fa-times"></i>';
            if (navOverlay) navOverlay.classList.add('active');
        } else {
            body.style.overflow = '';
            mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            if (navOverlay) navOverlay.classList.remove('active');
        }
    }
}

// Fermer le menu mobile
function closeMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navOverlay = document.querySelector('.nav-overlay');
    const body = document.body;
    
    if (navLinks && navLinks.classList.contains('show')) {
        navLinks.classList.remove('show');
        body.style.overflow = '';
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        if (navOverlay) navOverlay.classList.remove('active');
    }
}

// Gestion des dropdowns sur mobile
function initMobileDropdowns() {
    const dropdowns = document.querySelectorAll('.nav-dropdown');
    
    dropdowns.forEach(dropdown => {
        const btn = dropdown.querySelector('.dropdown-btn');
        
        if (btn) {
            btn.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    e.stopPropagation();
                    dropdown.classList.toggle('active');
                }
            });
        }
    });
}

// Gestion des favoris
function toggleFavorite(productId, element) {
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    const icon = element.querySelector('i');
    
    if (favorites.includes(productId)) {
        favorites = favorites.filter(id => id !== productId);
        element.classList.remove('active');
        icon.classList.remove('fas');
        icon.classList.add('far');
        showAlert('Produit retiré des favoris', 'info');
    } else {
        favorites.push(productId);
        element.classList.add('active');
        icon.classList.remove('far');
        icon.classList.add('fas');
        showAlert('Produit ajouté aux favoris', 'success');
    }
    
    localStorage.setItem('favorites', JSON.stringify(favorites));
    
    // Synchroniser avec le serveur si l'utilisateur est connecté
    if (window.userLoggedIn) {
        fetch(`/marketplace/favorite/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        }).catch(error => console.error('Error:', error));
    }
}

// Récupérer le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Lazy loading des images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback pour les anciens navigateurs
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Tooltips personnalisés
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('mousemove', moveTooltip);
    });
}

function showTooltip(e) {
    const tooltipText = e.target.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    tooltip.id = 'current-tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let top = rect.top - tooltipRect.height - 10;
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    
    // Éviter que le tooltip sorte de l'écran
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    if (top < 10) top = rect.bottom + 10;
    
    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
}

function moveTooltip(e) {
    const tooltip = document.getElementById('current-tooltip');
    if (!tooltip) return;
    
    const rect = e.target.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = e.clientX - (tooltipRect.width / 2);
    
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    tooltip.style.left = left + 'px';
}

function hideTooltip() {
    const tooltip = document.getElementById('current-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Recherche en temps réel
function initLiveSearch() {
    const searchInput = document.querySelector('.nav-search .search-form input, .mobile-search .search-form input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.trim();
            if (query.length > 2) {
                fetchSearchResults(query);
            }
        }, 500));
    }
}

function fetchSearchResults(query) {
    // Implémenter l'appel API ici
    console.log('Recherche en cours:', query);
    // Exemple: window.location.href = `/search/?q=${encodeURIComponent(query)}`;
}

// Animation de scroll fluide
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Détection de la connexion internet
function initConnectionChecker() {
    window.addEventListener('online', () => {
        showAlert('Connexion rétablie', 'success');
    });
    
    window.addEventListener('offline', () => {
        showAlert('Connexion internet perdue', 'error');
    });
}

// Rendre les tableaux responsives
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Gestion des liens actifs
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('Ktrade Connect - Application chargée avec la palette Teal & Orange');
    
    // Menu mobile
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const navOverlay = document.querySelector('.nav-overlay');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }
    
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    if (navOverlay) {
        navOverlay.addEventListener('click', closeMobileMenu);
    }
    
    // Initialiser les dropdowns mobile
    initMobileDropdowns();
    
    // Fermeture des alertes
    document.querySelectorAll('.close-alert').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });
    
    // Lazy loading des images
    lazyLoadImages();
    
    // Initialiser les tooltips
    initTooltips();
    
    // Initialiser le scroll fluide
    initSmoothScroll();
    
    // Vérifier la connexion
    initConnectionChecker();
    
    // Rendre les tableaux responsives
    makeTablesResponsive();
    
    // Recherche en temps réel
    initLiveSearch();
    
    // Liens actifs
    setActiveNavLink();
    
    // Fermer le menu mobile lors du redimensionnement
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
    
    // Fermer le menu mobile avec la touche Echap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });
});

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showAlert,
        formatPrice,
        isValidEmail,
        debounce,
        toggleFavorite
    };
}