# Premium Shop 👟✨

A modern, high-performance Django e-commerce platform designed for selling premium footwear and apparel. This project features a sleek UI, robust checkout flow, and seamless integration with the Nova Poshta API.

## 🚀 Key Features

*   **Premium UI/UX**: Designed with a focus on aesthetics, featuring glassmorphism, smooth animations, and a responsive layout.
*   **Nova Poshta Integration**: Automatic city search (autocomplete) and dynamic warehouse selection for reliable shipping in Ukraine.
*   **Smart Cart System**: Real-time cart updates with session management and cross-validation against the database.
*   **Secure Checkout**: Implementation of the PRG (Post/Redirect/Get) pattern to prevent duplicate orders and ensure a smooth flow.
*   **Social Contact Methods**: integrated selection for Telegram, Instagram, and WhatsApp.
*   **Product Management**: Clean detail pages with size selection and availability tracking.

## 🛠️ Tech Stack

*   **Backend**: Python, Django 6.0
*   **Database**: SQLite (Development)
*   **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+)
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
    pip install django requests
    ```

4.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Start Development Server**:
    ```bash
    python manage.py runserver
    ```

## 📝 Configuration

To enable **Nova Poshta API**, add your API key in `store/services.py`:
```python
API_KEY = "your_nova_poshta_api_key_here"
```

---
*Created with ❤️ by Arsen Khomiak*
