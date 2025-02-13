# Finance Web Application

Finance is a web application that allows users to manage their stock portfolio seamlessly. Users can register, log in, and perform various financial operations such as quoting stock prices, buying, selling, viewing transaction history, and managing their stock portfolio with real-time price updates via API integration.

## Features

- **User Authentication** – Register and log in securely.
- **Stock Quoting** – Get real-time stock price quotes.
- **Buy & Sell Stocks** – Purchase and sell stocks based on market prices.
- **Transaction History** – View past transactions for tracking investments.
- **Portfolio Management** – Monitor and manage owned stocks with real-time price updates.
- **Real-Time Data** – Fetch stock prices dynamically using an external API.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQL (SQLite)
- **API Integration:** Real-time stock price retrieval

## Installation & Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/finance.git
   ```
2. Navigate to the project directory:
   ```sh
   cd finance
   ```
3. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
5. Set up the database:
   ```sh
   flask db upgrade  # If using Flask-Migrate for database migrations
   ```
6. Run the application:
   ```sh
   flask run
   ```

## Usage

1. Open the application in your browser at `http://localhost:5000/`.
2. Register or log in to your account.
3. Use the search feature to get stock quotes.
4. Buy and sell stocks with real-time price updates.
5. View transaction history and manage your stock portfolio.

## Contributing

We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`feature-branch-name`).
3. Make your modifications and commit changes.
4. Push to your fork and create a pull request.

## Contact

For any questions or suggestions, feel free to reach out:
- Email: your.email@example.com

Happy Trading!

