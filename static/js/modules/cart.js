import { TRANSLATIONS, showToast, getCookie, getLangPrefix } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;

    // AJAX Add to Cart
    const addBtns = document.querySelectorAll('a[href*="/cart/add/"], #add-to-cart-btn');
    addBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let url = btn.getAttribute('href');
            if (!url) {
                const form = btn.closest('form');
                if (form) url = form.getAttribute('action');
            }

            if (!url) return;

            const isUserAuthenticated = body.dataset.authenticated === 'true';
            if (isUserAuthenticated === false) {
                if(window.showLoginModal) window.showLoginModal('cart');
                return;
            }

            const sizeInput = document.querySelector('input[name="size"]:checked');
            if (sizeInput) {
                const cartUrl = new URL(url, window.location.origin);
                cartUrl.searchParams.set('size', sizeInput.value);
                url = cartUrl.toString();
            } else if (document.querySelector('input[name="size"]')) {
                showToast(`<i class="fas fa-exclamation-triangle" style="color: var(--accent);"></i> <span>${TRANSLATIONS.toastSelectSize}</span>`);
                return;
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err; });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'ok') {
                        const cartCount = document.getElementById('cart-count');
                        if (cartCount) {
                            cartCount.innerText = data.cart_count;
                            cartCount.style.transform = 'scale(1.3)';
                            setTimeout(() => cartCount.style.transform = 'scale(1)', 200);
                        }
                        showToast(`<i class="fas fa-shopping-bag"></i> <span>${TRANSLATIONS.toastAdded}</span>`);

                        const errorMsg = document.getElementById('size-error');
                        if (errorMsg) errorMsg.style.display = 'none';
                    }
                })
                .catch(err => {
                    if (err.message) {
                        showToast(`<i class="fas fa-exclamation-circle" style="color: var(--accent);"></i> <span>${err.message}</span>`);
                        const errorMsg = document.getElementById('size-error');
                        if (errorMsg) errorMsg.style.display = 'block';
                    }
                });
        });
    });

    // Cart Quantity Updates
    const qtyControls = document.querySelectorAll('.quantity-controls');
    qtyControls.forEach(control => {
        const itemKey = control.dataset.itemKey;
        const url = control.dataset.url;
        const addBtn = control.querySelector('.qty-btn.add');
        const subBtn = control.querySelector('.qty-btn.subtract');

        if (addBtn) addBtn.addEventListener('click', () => updateQuantity(itemKey, 'add', url));
        if (subBtn) subBtn.addEventListener('click', () => updateQuantity(itemKey, 'subtract', url));
    });

    const deleteBtns = document.querySelectorAll('.qty-btn.delete');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const itemKey = btn.dataset.itemKey;
            const url = btn.dataset.url;
            updateQuantity(itemKey, 'delete', url);
        });
    });

    function updateQuantity(itemKey, action, url) {
        const actionUrl = url || `${getLangPrefix()}/cart/update/${itemKey}/`;
        const formData = new FormData();
        formData.append('action', action);

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.status === 'ok') {
                    location.reload();
                } else if (data.status === 'error' && data.message) {
                    showToast(`<i class="fas fa-exclamation-circle" style="color: var(--accent);"></i> <span>${data.message}</span>`);
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
                showToast(`<i class="fas fa-exclamation-triangle" style="color: var(--accent);"></i> <span>${TRANSLATIONS.toastError}</span>`);
            });
    }
});
