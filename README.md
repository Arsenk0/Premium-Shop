# Premium Shop 👟✨

A modern, high-performance Django e-commerce platform designed for selling premium footwear and apparel. This project features a sleek UI, robust checkout flow, and seamless integration with the Nova Poshta API.

## 🚀 Key Features

*   **Premium UI/UX**: Designed with a focus on aesthetics, featuring glassmorphism, smooth animations, and a responsive layout.
*   **Multi-language Support**: Full localization for **Ukrainian**, **English**, and **Czech** languages.
*   **Real-time Search**: Instant product search with autocomplete functionality.
*   **AJAX Filtering & Sorting**: Smooth, non-reloading product filtering (by price, size, stock) and sorting.
*   **Smart Cart & Sidebar**: Real-time cart updates with a sleek sidebar for easy access and session management.
*   **Wishlist**: Integrated wishlist for authenticated users to save favorite products.
*   **User Dashboard**: Personal profile with order statistics and recent activity tracking.
*   **Nova Poshta Integration**: Automatic city search (autocomplete) and dynamic warehouse selection for reliable shipping in Ukraine.
*   **Secure Checkout**: Implementation of the PRG (Post/Redirect/Get) pattern to prevent duplicate orders.
*   **Dynamic Size Selection**: Enforced size selection supporting both footwear and apparel.
*   **Product Reviews**: Integrated rating system (1-5 stars) with user comments.
*   **Async Task Processing**: Celery & Redis integration for background tasks like order confirmation and welcome emails.

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, Django 6.0.2
*   **Database**: SQLite (Development)
*   **Async/Tasks**: Celery, Redis
*   **Internationalization**: `django-modeltranslation`, `gettext`
*   **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+, AJAX)
*   **API**: Nova Poshta JSON-RPC 2.0
*   **Icons**: FontAwesome 6+
*   **Typography**: Inter (Google Fonts)

## 📦 Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Arsenk0/Premium-Shop.git
    cd Premium-Shop
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    DJANGO_SECRET_KEY=your_secret_key
    NOVA_POSHTA_API_KEY=your_api_key
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    ```

5.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Compile Translations**:
    ```bash
    python manage.py compilemessages
    ```

## 🚀 Running the Project

To ensure all features work correctly, you need to run the following services in separate windows:

1.  **Redis Server** (Required for Celery)
    ```bash
    redis-server
    ```

2.  **Celery Worker**
    ```bash
    celery -A shop_project worker --loglevel=info
    ```

3.  **Django Development Server**
    ```bash
    python manage.py runserver
    ```

---
> [!IMPORTANT]
> Ensure Redis is running before starting the Celery worker for email notifications to function.

## 📝 Configuration

Key environment variables in `.env`:
- `DEBUG`: Toggle development mode.
- `NOVA_POSHTA_API_KEY`: Required for shipping lookups.
- `CELERY_BROKER_URL`: Connection string for Redis.
- Email settings (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) for order notifications.

---
*Created with ❤️ by Arsen Khomiak*

## 📜 Personal Project

This project is developed by Arsen Khomiak for personal use. You can explore the code and use it as a basis for your own boutique store.

## 🤝 Fork and Build

We do not accept contributions to this repository. Please see our [Fork Guide](FORK_GUIDE.md) for instructions on how to create your own copy and build something unique!
