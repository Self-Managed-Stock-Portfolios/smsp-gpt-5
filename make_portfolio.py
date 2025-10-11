import json
import pandas as pd

def update_portfolio(input_date, output_date):
    json_path = f"GPT Daily Reviews/Weekends/t_{input_date}.json"
    csv_input_path = f"Portfolio Files/{input_date}.csv"
    csv_output_path = f"Portfolio Files/{output_date}.csv"

    with open(json_path, 'r') as f:
        outer_data = json.load(f)

    content = outer_data['choices'][0]['message']['content']
    inner_data = json.loads(content)

    trades = inner_data['trades']

    df = pd.read_csv(csv_input_path)

    # Handle cash row
    cash_row = df[df['Holding Name'] == 'Cash']
    if cash_row.empty:
        cash = 0.0
    else:
        cash = cash_row['Total Amount'].values[0]
        df = df[df['Holding Name'] != 'Cash']

    # Process each trade
    for trade in trades:
        action = trade['action']
        symbol = trade['symbol']
        shares = trade['shares']

        # Skip 'remove' trades
        if action == 'remove':
            continue

        if action == 'sell':
            amount = round(trade['amount'], 2)
            price = round(amount / shares, 2)
            cash += amount
            idx = df[df['Holding Name'] == symbol].index
            if not idx.empty:
                current_units = df.at[idx[0], 'Number of Units']
                new_units = current_units - shares
                if new_units > 0:
                    df.at[idx[0], 'Number of Units'] = new_units
                    df.at[idx[0], 'Current Price'] = price
                    df.at[idx[0], 'Total Amount'] = round(price * new_units, 2)
                    buying_price = df.at[idx[0], 'Buying Price']
                    df.at[idx[0], 'Perct Change'] = round(((price - buying_price) / buying_price) * 100, 2)
                else:
                    df = df.drop(idx[0])

        elif action == 'buy':
            amount = round(trade['amount'], 2)
            price = round(amount / shares, 2)
            cash -= amount
            idx = df[df['Holding Name'] == symbol].index
            if not idx.empty:
                old_units = df.at[idx[0], 'Number of Units']
                old_buy = df.at[idx[0], 'Buying Price']
                old_cost = round(old_buy * old_units, 2)
                new_cost = amount
                new_units = old_units + shares
                new_buy = round((old_cost + new_cost) / new_units, 2)
                df.at[idx[0], 'Buying Price'] = new_buy
                df.at[idx[0], 'Current Price'] = price
                df.at[idx[0], 'Number of Units'] = new_units
                df.at[idx[0], 'Total Amount'] = round(price * new_units, 2)
                df.at[idx[0], 'Perct Change'] = round(((price - new_buy) / new_buy) * 100, 2)
            else:
                new_row = {
                    'Holding Name': symbol,
                    'Buying Price': price,
                    'Current Price': price,
                    'Number of Units': shares,
                    'Total Amount': amount,
                    'Perct Change': 0.00
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Add cash back
    cash = round(cash, 2)
    cash_row = pd.DataFrame({
        'Holding Name': ['Cash'],
        'Buying Price': [cash],
        'Current Price': [cash],
        'Number of Units': [1],
        'Total Amount': [cash],
        'Perct Change': [0.00]
    })
    df = pd.concat([df, cash_row], ignore_index=True)

    # Round all numeric values
    df['Buying Price'] = df['Buying Price'].round(2)
    df['Current Price'] = df['Current Price'].round(2)
    df['Total Amount'] = df['Total Amount'].round(2)
    df['Perct Change'] = df['Perct Change'].round(2)

    # Save updated file
    df.to_csv(csv_output_path, index=False)
    print(f"✅ Updated portfolio saved to {csv_output_path}")

if __name__ == "__main__":
    input_date = input("Enter date for JSON and CSV input (YYYY-MM-DD): ")
    output_date = input("Enter date for CSV output (YYYY-MM-DD): ")
    update_portfolio(input_date, output_date)
