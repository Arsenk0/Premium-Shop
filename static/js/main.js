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
    const isUserAuthenticated = body.dataset.authenticated === 'true';
    if (isUserAuthenticated === false) {
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

    // --- Helpers ---
    function getLangPrefix() {
        const lang = document.documentElement.lang || 'uk';
        return `/${lang}`;
    }

    // --- AJAX Filtering Logic ---
    const filterForm = document.getElementById('filter-form');
    const productListContainer = document.getElementById('product-list-container');

    if (filterForm && productListContainer) {
        filterForm.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => {
                applyFilters();
            });
        });

        filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            applyFilters();
        });
    }

    function applyFilters() {
        if (!filterForm || !productListContainer) return;

        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData).toString();
        const url = `${window.location.pathname}?${params}`;

        // Show loading state
        productListContainer.style.opacity = '0.5';

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            productListContainer.innerHTML = html;
            productListContainer.style.opacity = '1';

            // Update URL without reloading
            window.history.pushState({}, '', url);

            // Re-rebind wishlist buttons and animations
            rebindWishlistButtons();
            const newFadeElems = productListContainer.querySelectorAll('.fade-in');
            newFadeElems.forEach(elem => observer.observe(elem));
        })
        .catch(err => {
            console.error('Filter error:', err);
            productListContainer.style.opacity = '1';
        });
    }

    // --- Wishlist Toggle Logic ---
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
            showLoginModal('wishlist');
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
                    showToast('💖 ' + (body.dataset.toastWishlistAdded || 'Додано до списку бажань!'));
                } else {
                    btn.classList.remove('active');
                    showToast('💔 ' + (body.dataset.toastWishlistRemoved || 'Видалено зі списку бажань'));
                    
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

    // --- Search Autocomplete ---
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        const autocompleteContainer = document.createElement('div');
        autocompleteContainer.className = 'search-autocomplete';
        searchInput.parentNode.appendChild(autocompleteContainer);

        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();
            
            if (query.length < 2) {
                autocompleteContainer.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`${getLangPrefix()}/api/search-autocomplete/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            autocompleteContainer.innerHTML = '';
                            data.results.forEach(res => {
                                const item = document.createElement('a');
                                item.href = res.url;
                                item.className = 'autocomplete-item';
                                item.innerHTML = `
                                    <img src="${res.image}" alt="">
                                    <div>
                                        <div class="name">${res.name}</div>
                                        <div class="price">${res.price} ₴</div>
                                    </div>
                                `;
                                autocompleteContainer.appendChild(item);
                            });
                            autocompleteContainer.style.display = 'block';
                        } else {
                            autocompleteContainer.style.display = 'none';
                        }
                    })
                    .catch(err => console.error('Search error:', err));
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !autocompleteContainer.contains(e.target)) {
                autocompleteContainer.style.display = 'none';
            }
        });
    }

    // Global Modal Functions
    window.showLoginModal = function (context = 'cart') {
        const modal = document.getElementById('login-modal');
        const titleEl = document.getElementById('login-modal-title');
        const descEl = document.getElementById('login-modal-desc');

        if (modal && titleEl && descEl) {
            if (context === 'wishlist') {
                titleEl.textContent = body.dataset.modalWishlistTitle || 'Бажаєте додати в список бажань? 😉';
                descEl.textContent = body.dataset.modalWishlistDesc || 'Увійдіть або зареєструйтесь, щоб ваші улюблені товари завжди були під рукою!';
            } else {
                titleEl.textContent = body.dataset.modalCartTitle || 'Бажаєте додати в кошик? 😉';
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
            closeLoginModal();
        }
    };
});
