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
