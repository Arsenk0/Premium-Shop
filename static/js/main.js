document.addEventListener('DOMContentLoaded', () => {
    console.log('Premium Shop Phase 2 Loaded');

    // AJAX Add to Cart
    const addBtns = document.querySelectorAll('a[href*="/cart/add/"], #add-to-cart-btn');
    addBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            let url = btn.getAttribute('href');

            // Check for size selection
            const sizeInput = document.querySelector('input[name="size"]:checked');
            if (sizeInput) {
                url += `?size=${sizeInput.value}`;
            } else if (document.querySelector('input[name="size"]')) {
                showToast('⚠️ Будь ласка, оберіть розмір!');
                return;
            }

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        // Update badge
                        const cartCount = document.getElementById('cart-count');
                        if (cartCount) {
                            cartCount.innerText = data.cart_count;
                            cartCount.style.transform = 'scale(1.3)';
                            setTimeout(() => cartCount.style.transform = 'scale(1)', 200);
                        }
                        showToast(`🛍 Додано до кошика!`);
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
        const addBtn = control.querySelector('.qty-btn.add');
        const subBtn = control.querySelector('.qty-btn.subtract');
        const valSpan = control.querySelector('.qty-val');

        addBtn.addEventListener('click', () => updateQuantity(itemKey, 'add'));
        subBtn.addEventListener('click', () => updateQuantity(itemKey, 'subtract'));
    });

    const deleteBtns = document.querySelectorAll('.qty-btn.delete');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const itemKey = btn.dataset.itemKey;
            updateQuantity(itemKey, 'delete');
        });
    });

    function updateQuantity(itemKey, action) {
        const formData = new FormData();
        formData.append('action', action);

        const csrftoken = getCookie('csrftoken');

        fetch(`/cart/update/${itemKey}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Refresh to update all prices and totals reliably
                    location.reload();
                }
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
});
