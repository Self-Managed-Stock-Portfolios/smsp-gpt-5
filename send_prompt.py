import os
import json
from datetime import datetime, date,timedelta
from dotenv import load_dotenv
from openai import OpenAI
from read_portfolio import get_portfolio_string
from read_stocks import get_stock_data_string

load_dotenv()

client = OpenAI(
    api_key=os.getenv('API_KEY'),
    base_url=None
)

def get_prompt_type():
    while True:
        user_input = input("Enter prompt type (f for first timer, d for daily, t for weekend training): ").strip().lower()
        if user_input in ['f', 'd', 't']:
            return user_input
        print("Invalid input. Please enter 'f', 'd', or 't'.")

def load_prompt(prompt_type, date_input):
    prompt_files = {
        'f': 'first_timer_prompt.txt',
        'd': 'daily_prompt.txt',
        't': 'training_prompt.txt'
    }
    file_path = prompt_files.get(prompt_type)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file '{file_path}' not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        prompt = f.read().strip()
    
    if prompt_type in ['d', 't']:
        portfolio_str = get_portfolio_string(date_input)
        prompt = prompt.replace("[Portfolio String]", portfolio_str)
    
    if prompt_type == 't':
        try:
            target_date = datetime.strptime(date_input, '%Y-%m-%d')
            stock_data = ""
            for i in range(5):
                past_date = (target_date - timedelta(days=i)).strftime('%Y-%m-%d')
                stock_data += get_stock_data_string(past_date) + "\n"
        except ValueError as e:
            raise ValueError(f"Error processing stock data: {e}")
        prompt = prompt.replace("[Stock Data]", stock_data)
        prior_signals = []
        signals_dir = os.path.join("Grok Daily Reviews", "Weekdays")
        for i in range(5):
            past_date = (target_date - timedelta(days=i)).strftime('%Y-%m-%d')
            signal_file = os.path.join(signals_dir, f"d_{past_date}.json")
            if os.path.exists(signal_file):
                with open(signal_file, 'r', encoding='utf-8') as f:
                    prior_signals.append(json.load(f))
        prompt = prompt.replace("[Prior Signals JSON]", json.dumps(prior_signals))
    else:
        stock_data = get_stock_data_string(date_input)
        prompt = prompt.replace("[Stock Data]", stock_data)
    
    return prompt

def is_weekday():
    today = date.today()
    return today.weekday() < 5

def save_response(response, prompt_type, date_input):
    base_dir = "Grok Daily Reviews"
    sub_dir = "Weekdays" if is_weekday() else "Weekends"
    os.makedirs(os.path.join(base_dir, sub_dir), exist_ok=True)
    
    date_str = datetime.strptime(date_input, '%Y-%m-%d').strftime('%Y-%m-%d')
    filename = f"{prompt_type}_{date_str}.json"
    filepath = os.path.join(base_dir, sub_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(response.model_dump(), f, indent=2)
    
    print(f"Response saved to: {filepath}")

if __name__ == "__main__":
    prompt_type = get_prompt_type()
    date_input = input("Enter the date (YYYY-MM-DD): ").strip()
    try:
        prompt = load_prompt(prompt_type, date_input)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        exit(1)
    
    temperature = 0.3 if prompt_type in ['f', 'd'] else 0.35
    print(prompt)
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    
    print("Grok Response:")
    print(response.choices[0].message.content)
    
    save_response(response, prompt_type, date_input)