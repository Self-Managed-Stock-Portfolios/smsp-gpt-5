import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

def update_portfolio(date_input: str) -> None:
    """Updates the 'Current Price', 'Total Amount', and 'Perct Change' columns in the portfolio CSV for the given date using yfinance data.
    
    Args:
        date_input (str): Date in YYYY-MM-DD format.
    
    Raises:
        ValueError: If date format is invalid.
        FileNotFoundError: If portfolio CSV does not exist.
        ValueError: If CSV is missing required columns.
    """
    try:
        target_date = datetime.strptime(date_input, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-09-24).")
    
    output_dir = "Portfolio Files"
    csv_file = os.path.join(output_dir, f"{target_date.strftime('%Y-%m-%d')}.csv")
    
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"No portfolio file found for {target_date.strftime('%Y-%m-%d')}. Please create it first.")
    
    df = pd.read_csv(csv_file)
    required_cols = ['Holding Name', 'Buying Price', 'Current Price', 'Number of Units', 'Total Amount', 'Perct Change']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("CSV missing required columns. Expected: Holding Name, Buying Price, Current Price, Number of Units, Total Amount, Perct Change")
    
    start_date = target_date
    end_date = target_date + timedelta(days=1)
    
    for index, row in df.iterrows():
        symbol = row['Holding Name']
        if symbol.lower() == 'cash':
            continue
        
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(start=start_date, end=end_date)
            if not hist.empty:
                close = hist['Close'].iloc[0]
                df.at[index, 'Current Price'] = round(close, 2)
                df.at[index, 'Total Amount'] = round(df.at[index, 'Current Price'] * df.at[index, 'Number of Units'], 2)
                df.at[index, 'Perct Change'] = round(((df.at[index, 'Current Price'] - df.at[index, 'Buying Price']) / df.at[index, 'Buying Price']) * 100, 2)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    df.to_csv(csv_file, index=False)
    print(f"Updated portfolio file: {csv_file}")

if __name__ == "__main__":
    date_input = input("Enter the date (YYYY-MM-DD): ").strip()
    try:
        update_portfolio(date_input)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")