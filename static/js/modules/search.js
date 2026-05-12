import { getLangPrefix } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('input[name="q"]');
    const searchBar = document.querySelector('.search-bar');
    const clearBtn = document.querySelector('.search-clear');
    const spinner = document.querySelector('.search-spinner');

    if (searchInput && searchBar) {
        const autocompleteContainer = document.createElement('div');
        autocompleteContainer.className = 'search-autocomplete';
        searchBar.appendChild(autocompleteContainer);

        let debounceTimer;
        let selectedIndex = -1;

        const updateClearButton = () => {
            if (clearBtn) {
                clearBtn.style.display = searchInput.value ? 'block' : 'none';
            }
        };

        const highlightMatch = (text, query) => {
            if (!query) return text;
            const regex = new RegExp(`(${query})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        };

        const updateSelection = (items) => {
            items.forEach((item, index) => {
                item.classList.toggle('active', index === selectedIndex);
            });
            if (selectedIndex !== -1) {
                items[selectedIndex].scrollIntoView({ block: 'nearest' });
            }
        };

        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();
            updateClearButton();
            
            if (query.length < 2) {
                autocompleteContainer.style.display = 'none';
                if (spinner) spinner.style.display = 'none';
                return;
            }

            if (spinner) spinner.style.display = 'block';
            selectedIndex = -1;

            debounceTimer = setTimeout(() => {
                fetch(`${getLangPrefix()}/api/search-autocomplete/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (spinner) spinner.style.display = 'none';
                        if (data.results && data.results.length > 0) {
                            autocompleteContainer.innerHTML = '';
                            data.results.forEach(res => {
                                const item = document.createElement('a');
                                item.href = res.url;
                                item.className = 'autocomplete-item';
                                item.innerHTML = `
                                    <img src="${res.image}" alt="">
                                    <div>
                                        <div class="name">${highlightMatch(res.name, query)}</div>
                                        <div class="price">${res.price}</div>
                                    </div>
                                `;
                                autocompleteContainer.appendChild(item);
                            });
                            autocompleteContainer.style.display = 'block';
                        } else {
                            autocompleteContainer.style.display = 'none';
                        }
                    })
                    .catch(err => {
                        console.error('Search error:', err);
                        if (spinner) spinner.style.display = 'none';
                    });
            }, 300);
        });

        // Keyboard Navigation
        searchInput.addEventListener('keydown', (e) => {
            const items = autocompleteContainer.querySelectorAll('.autocomplete-item');
            
            if (autocompleteContainer.style.display === 'block') {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    selectedIndex = (selectedIndex + 1) % items.length;
                    updateSelection(items);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    selectedIndex = (selectedIndex - 1 + items.length) % items.length;
                    updateSelection(items);
                } else if (e.key === 'Enter' && selectedIndex !== -1) {
                    e.preventDefault();
                    items[selectedIndex].click();
                } else if (e.key === 'Escape') {
                    autocompleteContainer.style.display = 'none';
                }
            }
        });

        // Clear Button
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                searchInput.focus();
                updateClearButton();
                autocompleteContainer.style.display = 'none';
            });
        }

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!searchBar.contains(e.target)) {
                autocompleteContainer.style.display = 'none';
            }
        });

        // Initial clear button state
        updateClearButton();
    }
});
