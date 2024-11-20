from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf

app = Flask(__name__)

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

@app.route('/stock', methods=['POST'])
def stock():
    stock_ticker = request.form.get('stock_ticker')
    stock_data = {}
    if stock_ticker:
        try:
            ticker = yf.Ticker(stock_ticker)
            info = ticker.info

            # Check if longName exists
            if not info.get('longName'):
                return render_template('stock.html', error="Stock doesn't exist in our database")

            # Extract the requested fields
            stock_data = {
                "short_name": info.get('shortName', 'Unknown'),
                "long_name": info.get('longName', 'Unknown'),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "country": info.get('country', 'Unknown'),
                "market_cap": info.get('marketCap', 'Unknown'),
                "total_revenue": info.get('totalRevenue', 'Unknown'),
                "gross_profit": info.get('grossProfits', 'Unknown'),
                "current_price": info.get('currentPrice', 'Unknown'),
                "day_high": info.get('dayHigh', 'Unknown'),
                "day_low": info.get('dayLow', 'Unknown'),
                "dividend_rate": info.get('dividendRate', 'Unknown'),
            }
        except Exception as e:
            return render_template('stock.html', error=f"Error fetching stock data: {e}")
    else:
        return render_template('stock.html', error="No stock ticker provided.")

    return render_template('stock.html', stock_data=stock_data)



@app.route('/stockfinder')
def stockfinder():
    return render_template('stockfinder.html')




if __name__ == '__main__':
    app.run(debug=True)