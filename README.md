# Premium Shop 👟✨

A modern, high-performance Django e-commerce platform designed for selling premium footwear and apparel. This project features a sleek UI, robust checkout flow, advanced analytics, and seamless integration with the Nova Poshta API and Telegram.

## 🚀 Key Features

*   **Premium UI/UX**: Designed with a focus on aesthetics, featuring glassmorphism, smooth animations, and a responsive layout with full **Dark/Light mode** support.
*   **Advanced Telegram Bot**: Interactive bot with persistent menu, account linking via OTP, profile management, and real-time order tracking.
*   **6-Tier Loyalty Program**: A sophisticated gamified system with 6 tiers (**Bronze** to **Elite**), point accrual for purchases and reviews, and a conversion system for discount coupons.
*   **Professional Admin Panel**: Powered by `django-jazzmin` with a custom analytics dashboard for streamlined management.
*   **Multi-language Support**: Full localization for **Ukrainian (uk)**, **English (en)**, and **Czech (cs)**.
*   **Real-time Search & Filtering**: Instant product search with autocomplete and non-reloading AJAX filtering.
*   **Nova Poshta Integration**: Automatic city search (autocomplete) and dynamic warehouse selection for reliable shipping.
*   **Smart Cart & Wishlist**: Real-time cart updates with a sleek sidebar and personal wishlist for authenticated users.
*   **Dynamic Order Tracking**: Interactive success page with real-time status updates from the database.
*   **Async Task Processing**: Celery & Redis integration for background tasks like order confirmation and welcome emails.

## 🤖 Telegram Bot Features

The integrated Telegram bot (@PremiumShopBot) provides:
- **Persistent Keyboard**: Easy navigation between Profile, Loyalty info, and Support.
- **Order Tracking**: Get instant updates when your order status changes.
- **Account Linking**: Securely link your website account using a one-time password (OTP).
- **Interactive Commands**: `/start`, `/profile`, `/loyalty`, and status checks directly from Telegram.

## 📊 Loyalty & Rewards

Our custom loyalty system rewards active customers through 6 tiers:
1.  **🥉 Bronze**: Entry level (0+ points)
2.  **🥈 Silver**: 5% discount (200+ points)
3.  **🥇 Gold**: 7% discount (500+ points)
4.  **💎 Platinum**: 10% discount (1000+ points)
5.  **💠 Diamond**: 12% discount (2000+ points)
6.  **👑 Elite**: 15% discount (5000+ points)

*Points are earned for registration, purchases, and writing product reviews.*

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, Django 6.0.2
*   **Bot**: Python Telegram Bot (PTB) 22.7
*   **Database**: SQLite (Development) / PostgreSQL (Production ready)
*   **Async/Tasks**: Celery, Redis
*   **Admin UI**: Django Jazzmin (Customized)
*   **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+, AJAX)
*   **API**: Nova Poshta JSON-RPC 2.0
*   **PDF Generation**: WeasyPrint
*   **Internationalization**: `django-modeltranslation`, `gettext`

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
    Create a `.env` file in the root directory (see `.env.example`):
    ```env
    DJANGO_SECRET_KEY=your_secret_key
    NOVA_POSHTA_API_KEY=your_api_key
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_BOT_USERNAME=PremiumShopBot
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

3.  **Telegram Bot**
    ```bash
    python manage.py run_telegram_bot
    ```

4.  **Django Development Server**
    ```bash
    python manage.py runserver
    ```

---
> [!IMPORTANT]
> Ensure Redis is running before starting the Celery worker and the Telegram bot for full functionality.

## 📝 Configuration

Key environment variables in `.env`:
- `DEBUG`: Toggle development mode.
- `NOVA_POSHTA_API_KEY`: Required for shipping lookups.
- `TELEGRAM_BOT_TOKEN`: Token from BotFather for the shop bot.
- `CELERY_BROKER_URL`: Connection string for Redis.
- Email settings for order notifications and OTP delivery.

---
*Created with ❤️ by Arsen Khomiak*

## 📜 Personal Project

This project is developed by Arsen Khomiak for personal use. You can explore the code and use it as a basis for your own boutique store.

## 🤝 Fork and Build

We do not accept contributions to this repository. Please see our [Fork Guide](FORK_GUIDE.md) for instructions on how to create your own copy and build something unique!
