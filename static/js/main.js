document.addEventListener('DOMContentLoaded', () => {
    console.log('Premium Shop Phase 2 Loaded');

    // Get translated strings from body data attributes
    const body = document.body;
    const TRANSLATIONS = {
        toastAdded: body.dataset.toastAdded || 'Додано до кошика!',
        toastError: body.dataset.toastError || 'Халепа, щось пішло не так!',
        toastSelectSize: body.dataset.toastSelectSize || 'Будь ласка, оберіть розмір!',
        loading: body.dataset.loading || 'Завантаження...',
        selectWarehouse: body.dataset.selectWarehouse || 'Оберіть відділення',
        noWarehouses: body.dataset.noWarehouses || 'Відділень не знайдено',
    };

    // AJAX Add to Cart
    const addBtns = document.querySelectorAll('a[href*="/cart/add/"], #add-to-cart-btn');
    addBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let url = btn.getAttribute('href');

            // Check for authentication
            if (window.isUserAuthenticated === false) {
                showLoginModal();
                return;
            }

            // Check for size selection
            const sizeInput = document.querySelector('input[name="size"]:checked');
            if (sizeInput) {
                url += `?size=${sizeInput.value}`;
            } else if (document.querySelector('input[name="size"]')) {
                showToast(`⚠️ ${TRANSLATIONS.toastSelectSize}`);
                return;
            }

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
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
                        // Update badge
                        const cartCount = document.getElementById('cart-count');
                        if (cartCount) {
                            cartCount.innerText = data.cart_count;
                            cartCount.style.transform = 'scale(1.3)';
                            setTimeout(() => cartCount.style.transform = 'scale(1)', 200);
                        }
                        showToast(`🛍 ${TRANSLATIONS.toastAdded}`);

                        // Clear error UI if present
                        const errorMsg = document.getElementById('size-error');
                        if (errorMsg) errorMsg.style.display = 'none';
                    }
                })
                .catch(err => {
                    if (err.message) {
                        showToast(`⚠️ ${err.message}`);
                        const errorMsg = document.getElementById('size-error');
                        if (errorMsg) errorMsg.style.display = 'block';
                    }
                });
        });
    });

    function showToast(message) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // Cart Quantity Updates
    const qtyControls = document.querySelectorAll('.quantity-controls');
    qtyControls.forEach(control => {
        const itemKey = control.dataset.itemKey;
        const url = control.dataset.url;
        const addBtn = control.querySelector('.qty-btn.add');
        const subBtn = control.querySelector('.qty-btn.subtract');
        const valSpan = control.querySelector('.qty-val');

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
        const actionUrl = url || `/${document.documentElement.lang || 'uk'}/cart/update/${itemKey}/`;
        const formData = new FormData();
        formData.append('action', action);

        const csrftoken = getCookie('csrftoken');

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'ok') {
                    // Refresh to update all prices and totals reliably
                    location.reload();
                } else if (data.status === 'error' && data.message) {
                    showToast(`⚠️ ${data.message}`);
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
                showToast(`⚠️ ${TRANSLATIONS.toastError}`);
            });
    }

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
        if (!cookieValue && name === 'csrftoken') {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta) cookieValue = meta.getAttribute('content');
        }
        return cookieValue;
    }

    // Scroll Animations
    const fadeElems = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    fadeElems.forEach(elem => observer.observe(elem));

    // Global Modal Functions
    window.showLoginModal = function () {
        const modal = document.getElementById('login-modal');
        if (modal) {
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
            closeLoginModal();
        }
    };
});
