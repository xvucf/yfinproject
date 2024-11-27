from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf

app = Flask(__name__)


user_data = {
    "wallet": 0,
    "portfolio": []
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
    return render_template('buildyourportfolio.html', wallet=user_data['wallet'])


@app.route('/set_wallet', methods=['POST'])
def set_wallet():

    amount = float(request.form.get('amount', 0))
    user_data['wallet'] += amount
    return redirect(url_for('stockfinder'))


@app.route('/stockfinder')
def stockfinder():
    return render_template('stockfinder.html')

@app.route('/stock', methods=['POST'])
def stock():
    stock_ticker = request.form.get('stock_ticker')
    try:
        ticker = yf.Ticker(stock_ticker)
        info = ticker.info


        if not info.get('longName'):
            return render_template('stock.html', error="Stock not found. Please try another ticker.")


        stock_data = {
            "ticker": stock_ticker.upper(),
            "long_name": info.get('longName', 'Unknown'),
            "current_price": info.get('currentPrice', 'Unknown'),
            "day_low": info.get('dayLow', 'Unknown'),
            "day_high": info.get('dayHigh', 'Unknown'),
            "year_range": info.get('fiftyTwoWeekLow', 'Unknown'),  # 52-Week Low
            "year_high": info.get('fiftyTwoWeekHigh', 'Unknown'),  # 52-Week High
        }


        stock_data["year_range_formatted"] = f"${stock_data['year_range']} - ${stock_data['year_high']}"

        return render_template('stock.html', stock_data=stock_data, wallet=user_data['wallet'])
    except Exception as e:
        return render_template('stock.html', error=f"Error fetching stock data: {e}", wallet=user_data['wallet'])

@app.route('/buy_stock', methods=['POST'])
def buy_stock():

    stock_ticker = request.form.get('stock_ticker')
    quantity = int(request.form.get('quantity', 0))
    price = float(request.form.get('price', 0))
    total_cost = quantity * price

    if total_cost > user_data['wallet']:
        return render_template('stock.html', error="Insufficient funds!", stock_data={
            "ticker": stock_ticker,
            "current_price": price
        })


    user_data['wallet'] -= total_cost
    user_data['portfolio'].append({
        "ticker": stock_ticker,
        "quantity": quantity,
        "price": price,
        "total_cost": total_cost
    })
    return redirect(url_for('portfolio'))


@app.route('/portfolio')
def portfolio():

    portfolio_data = []
    for stock in user_data['portfolio']:
        ticker = yf.Ticker(stock['ticker'])
        current_price = ticker.info.get('currentPrice', 0)
        current_value = stock['quantity'] * current_price
        profit_loss = current_value - stock['total_cost']

        portfolio_data.append({
            "ticker": stock['ticker'],
            "quantity": stock['quantity'],
            "cost_basis": round(stock['total_cost'], 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2)
        })

    wallet_balance = round(user_data['wallet'], 2)  # Round wallet balance to 2 decimals
    return render_template('portfolio.html', wallet=wallet_balance, portfolio=portfolio_data)



if __name__ == '__main__':
    app.run(debug=True)
