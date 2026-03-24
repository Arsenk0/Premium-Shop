// /static/js/main.js
// Main entry point for frontend scripts
import './modules/utils.js';
import './modules/ui.js';
import './modules/cart.js';
import './modules/wishlist.js';
import './modules/search.js';
import './modules/filters.js';

import { initTheme } from './modules/theme.js';

initTheme();
console.log('App modules loaded successfully.');
