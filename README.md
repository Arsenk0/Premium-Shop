# Premium Shop 👟✨

A modern, high-performance Django e-commerce platform designed for selling premium footwear and apparel. This project features a sleek UI, robust checkout flow, and seamless integration with the Nova Poshta API.

## 🚀 Key Features

*   **Premium UI/UX**: Designed with a focus on aesthetics, featuring glassmorphism, smooth animations, and a responsive layout.
*   **Nova Poshta Integration**: Automatic city search (autocomplete) and dynamic warehouse selection for reliable shipping in Ukraine.
*   **Smart Cart System**: Real-time cart updates with session management and cross-validation against the database.
*   **Secure Checkout**: Implementation of the PRG (Post/Redirect/Get) pattern to prevent duplicate orders and ensure a smooth flow.
*   **Dynamic Size Selection**: Enforced size selection for products (v1.1+), supporting both footwear and apparel.
*   **Product Reviews**: Integrated rating system (1-5 stars) with user comments for customer feedback.
*   **Async Task Processing**: Celery & Redis integration for background tasks like order confirmation emails.
*   **Social Contact Methods**: Integrated selection for Telegram, Instagram, and phone calls.
*   **Advanced Auth**: Seamless login and signup flow with email/username support.

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, Django 6.0
*   **Async/Tasks**: Celery, Redis
*   **Database**: SQLite (Development)
*   **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+)
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
    ```

5.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Start Services**:
    - **Redis** (required for Celery):
      ```bash
      redis-server
      ```
    - **Celery Worker**:
      ```bash
      celery -A shop_project worker --loglevel=info
      ```
    - **Django Server**:
      ```bash
      python manage.py runserver
      ```

## 📝 Configuration

Configuration is managed via environment variables in `.env`. Key settings include:
- `DEBUG`: Toggle development mode.
- `NOVA_POSHTA_API_KEY`: Required for shipping lookups.
- `CELERY_BROKER_URL`: Connection string for Redis.

---
*Created with ❤️ by Arsen Khomiak*
