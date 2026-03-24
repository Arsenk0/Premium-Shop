import { TRANSLATIONS } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    // Scroll Animations
    const fadeElems = document.querySelectorAll('.fade-in');
    if (fadeElems.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0 });

        fadeElems.forEach(elem => observer.observe(elem));
    }

    // Global Modal Functions
    const body = document.body;
    window.showLoginModal = function (context = 'cart') {
        const modal = document.getElementById('login-modal');
        const titleEl = document.getElementById('login-modal-title');
        const descEl = document.getElementById('login-modal-desc');

        if (modal && titleEl && descEl) {
            if (context === 'wishlist') {
                titleEl.innerHTML = body.dataset.modalWishlistTitle || 'Бажаєте додати в список бажань? <i class="fas fa-smile-wink" style="color: var(--accent);"></i>';
                descEl.textContent = body.dataset.modalWishlistDesc || 'Увійдіть або зареєструйтесь, щоб ваші улюблені товари завжди були під рукою!';
            } else {
                titleEl.innerHTML = body.dataset.modalCartTitle || 'Бажаєте додати в кошик? <i class="fas fa-smile-wink" style="color: var(--accent);"></i>';
                descEl.textContent = body.dataset.modalCartDesc || 'Увійдіть або зареєструйтесь, щоб ваші товари зберігалися в особистому кабінеті та ви отримували бонуси!';
            }
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeLoginModal = function () {
        const modal = document.getElementById('login-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    };

    // Close modal on click outside
    window.onclick = function (event) {
        const modal = document.getElementById('login-modal');
        if (event.target == modal) {
            window.closeLoginModal();
        }
    };
});
