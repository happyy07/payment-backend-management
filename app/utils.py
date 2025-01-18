from datetime import datetime
import pandas as pd

def normalize_csv_data(df: pd.DataFrame) -> list:
    # Convert dates to proper format
    df['payee_added_date_utc'] = pd.to_datetime(df['payee_added_date_utc'])
    df['payee_due_date'] = pd.to_datetime(df['payee_due_date']).dt.date
    
    # Convert to proper types
    df['discount_percent'] = pd.to_numeric(df['discount_percent'], errors='coerce')
    df['tax_percent'] = pd.to_numeric(df['tax_percent'], errors='coerce')
    df['due_amount'] = pd.to_numeric(df['due_amount'], errors='coerce')
    
    # Fill NA values
    df['payee_country'].fillna('', inplace=True)
    df['payee_address_line_2'].fillna('', inplace=True)
    df['payee_province_or_state'].fillna('', inplace=True)
    df['discount_percent'].fillna(0, inplace=True)
    df['tax_percent'].fillna(0, inplace=True)
    
    return df.to_dict('records')

def calculate_total_due(due_amount: float, discount_percent: float = 0, tax_percent: float = 0) -> float:
    amount_after_discount = due_amount * (1 - (discount_percent or 0) / 100)
    total = amount_after_discount * (1 + (tax_percent or 0) / 100)
    return round(total, 2) 