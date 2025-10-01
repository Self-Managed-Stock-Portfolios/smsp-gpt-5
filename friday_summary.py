import os
import json
from datetime import datetime, timedelta

def generate_weekly_string(friday_date: str) -> str:
    """Generates a formatted string from the last 5 daily JSON responses (Monday to Friday).
    
    Args:
        friday_date (str): Friday's date in YYYY-MM-DD format.
    
    Returns:
        str: Formatted weekly string.
    
    Raises:
        ValueError: If date format is invalid or not Friday.
        FileNotFoundError: If a JSON file is missing.
        json.JSONDecodeError: If JSON parsing fails.
    """
    try:
        target_date = datetime.strptime(friday_date, '%Y-%m-%d')
        if target_date.weekday() != 4:
            raise ValueError("Input date must be a Friday.")
    except ValueError as e:
        raise ValueError(f"Invalid date format or not Friday: {e}")
    
    weekly_str = ""
    signals_dir = os.path.join("Grok Daily Reviews", "Weekdays")
    for i in range(4, -1, -1):
        past_date = (target_date - timedelta(days=i)).strftime('%Y-%m-%d')
        day_name = datetime.strptime(past_date, '%Y-%m-%d').strftime('%A')
        found = False
        for prompt_type in ['d', 'f']:
            signal_file = os.path.join(signals_dir, f"{prompt_type}_{past_date}.json")
            if os.path.exists(signal_file):
                with open(signal_file, 'r', encoding='utf-8') as f:
                    signal_data = json.load(f)
                    text = signal_data['choices'][0]['message']['content']
                    text = text.strip()
                    if text.startswith('```json'):
                        text = text[7:].rstrip('```').strip()
                    signal_content = json.loads(text)
                weekly_str += f"{day_name} Summary: {signal_content.get('daily_summary', 'No summary')}\n"
                weekly_str += f"{day_name} Signals: {json.dumps(signal_content.get('top_signals', []))}\n\n"
                found = True
                break
        if not found:
            weekly_str += f"{day_name} Summary: No data\n"
            weekly_str += f"{day_name} Signals: []\n\n"
    
    return weekly_str

if __name__ == "__main__":
    friday_date = input("Enter Friday's date (YYYY-MM-DD): ").strip()
    try:
        weekly_string = generate_weekly_string(friday_date)
        print(weekly_string)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")