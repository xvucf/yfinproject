from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf

app = Flask(__name__)

# In-memory storage for wallet and portfolio
user_data = {
    "wallet": 0,  # Initial cash amount
    "portfolio": []  # List of owned stocks
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/greet', methods=['POST'])
def greet():
    username = request.form.get('username')
    return render_template('greet.html', username=username)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/buildyourportfolio')
def home():
    return render_template('buildyourportfolio.html')

@app.route('/set_wallet', methods=['POST'])
def set_wallet():
    # Set the initial amount of money in the wallet
    amount = float(request.form.get('amount', 0))
    user_data['wallet'] = amount
    return redirect(url_for('stockfinder'))

@app.route('/stockfinder')
def stockfinder():
    return render_template('stockfinder.html')

@app.route('/stock', methods=['POST'])
def stock():
    # Get the stock ticker from the form
    stock_ticker = request.form.get('stock_ticker')
    try:
        ticker = yf.Ticker(stock_ticker)
        info = ticker.info

        # Check if stock name is available
        if not info.get('shortName'):
            return render_template('stock.html', error="Stock not found. Please try another ticker.")

        # Extract key stock information
        stock_data = {
            "ticker": stock_ticker.upper(),
            "short_name": info.get('shortName'),
            "current_price": info.get('currentPrice', 0)
        }
        return render_template('stock.html', stock_data=stock_data)
    except Exception as e:
        return render_template('stock.html', error=f"Error fetching stock data: {e}")

@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    # Process stock purchase
    stock_ticker = request.form.get('stock_ticker')
    quantity = int(request.form.get('quantity', 0))
    price = float(request.form.get('price', 0))
    total_cost = quantity * price

    if total_cost > user_data['wallet']:
        return render_template('stock.html', error="Insufficient funds!", stock_data={
            "ticker": stock_ticker,
            "current_price": price
        })

    # Deduct from wallet and add to portfolio
    user_data['wallet'] -= total_cost
    user_data['portfolio'].append({
        "ticker": stock_ticker,
        "quantity": quantity,
        "price": price,  # Cost per share
        "total_cost": total_cost  # Total spent on this stock
    })
    return redirect(url_for('portfolio'))


@app.route('/portfolio')
def portfolio():
    # Calculate current portfolio value and profit/loss
    portfolio_data = []
    for stock in user_data['portfolio']:
        ticker = yf.Ticker(stock['ticker'])
        current_price = ticker.info.get('currentPrice', 0)
        current_value = stock['quantity'] * current_price
        profit_loss = current_value - stock['total_cost']

        portfolio_data.append({
            "ticker": stock['ticker'],
            "quantity": stock['quantity'],
            "cost_basis": stock['total_cost'],
            "current_value": current_value,
            "profit_loss": profit_loss
        })

    return render_template('portfolio.html', wallet=user_data['wallet'], portfolio=portfolio_data)


if __name__ == '__main__':
    app.run(debug=True)
