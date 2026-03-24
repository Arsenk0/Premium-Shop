document.addEventListener('DOMContentLoaded', () => {
    // AJAX Filtering Logic
    const filterForm = document.getElementById('filter-form');
    const productListContainer = document.getElementById('product-list-container');

    if (filterForm && productListContainer) {
        filterForm.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => {
                input.blur(); // Force loss of focus to close native dropdowns immediately
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
            if (window.rebindWishlistButtons) {
                window.rebindWishlistButtons();
            }

            const newFadeElems = productListContainer.querySelectorAll('.fade-in');
            if (newFadeElems.length > 0) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('visible');
                        }
                    });
                }, { threshold: 0 });
                newFadeElems.forEach(elem => observer.observe(elem));
            }
        })
        .catch(err => {
            console.error('Filter error:', err);
            productListContainer.style.opacity = '1';
        });
    }
});
