const body = document.body;

export const TRANSLATIONS = {
    toastAdded: body.dataset.toastAdded || 'Додано до кошика!',
    toastError: body.dataset.toastError || 'Халепа, щось пішло не так!',
    toastSelectSize: body.dataset.toastSelectSize || 'Будь ласка, оберіть розмір!',
    loading: body.dataset.loading || 'Завантаження...',
    selectWarehouse: body.dataset.selectWarehouse || 'Оберіть відділення',
    noWarehouses: body.dataset.noWarehouses || 'Відділень не знайдено',
};

export function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

export function getCookie(name) {
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

export function getLangPrefix() {
    const lang = document.documentElement.lang || 'uk';
    return `/${lang}`;
}
