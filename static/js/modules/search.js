import { getLangPrefix } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    // Search Autocomplete
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
});
