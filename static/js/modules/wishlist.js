import { showToast, getCookie, getLangPrefix, TRANSLATIONS } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    function rebindWishlistButtons() {
        const wishlistBtns = document.querySelectorAll('.toggle-wishlist');
        wishlistBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleWishlist(btn);
            };
        });
    }

    function toggleWishlist(btn) {
        const productId = btn.dataset.productId;
        
        if (body.dataset.authenticated !== 'true') {
            if(window.showLoginModal) window.showLoginModal('wishlist');
            return;
        }

        fetch(`${getLangPrefix()}/wishlist/toggle/${productId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                if (data.action === 'added') {
                    btn.classList.add('active');
                    showToast(`<i class="fas fa-heart" style="color: var(--accent);"></i> <span>` + (body.dataset.toastWishlistAdded || 'Додано до списку бажань!') + `</span>`);
                } else {
                    btn.classList.remove('active');
                    showToast(`<i class="fas fa-heart-crack"></i> <span>` + (body.dataset.toastWishlistRemoved || 'Видалено зі списку бажань') + `</span>`);
                    
                    if (window.location.pathname.includes('/wishlist/')) {
                        const card = btn.closest('.product-card');
                        if (card) {
                            card.style.opacity = '0';
                            setTimeout(() => card.remove(), 500);
                        }
                    }
                }
            }
        })
        .catch(err => console.error('Wishlist error:', err));
    }

    rebindWishlistButtons();

    // Export so filter.js can re-call it after AJAX updates
    window.rebindWishlistButtons = rebindWishlistButtons;
});
