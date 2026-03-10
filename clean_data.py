import pandas as pd
import numpy as np
import os

def clean_deals(file_path):
    df = pd.read_csv(file_path)
    # Remove rows that are headers repeated in data (like line 52)
    df = df[df['Deal Name'] != 'Deal Name']
    df = df[df['Deal Name'].notna()]
    
    # Normalize dates
    date_cols = ['Close Date (A)', 'Tentative Close Date', 'Created Date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Clean numeric values
    df['Masked Deal value'] = pd.to_numeric(df['Masked Deal value'], errors='coerce').fillna(0)
    
    return df

def clean_work_orders(file_path):
    # CSV has empty first line
    df = pd.read_csv(file_path, skiprows=1)
    df = df[df['Deal name masked'].notna()]
    
    # Normalize dates
    date_cols = ['Data Delivery Date', 'Date of PO/LOI', 'Probable Start Date', 'Probable End Date', 'Last invoice date', 'Collection Date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
    # Clean numeric values
    numeric_cols = ['Amount in Rupees (Excl of GST) (Masked)', 'Amount in Rupees (Incl of GST) (Masked)', 
                    'Billed Value in Rupees (Excl of GST.) (Masked)', 'Billed Value in Rupees (Incl of GST.) (Masked)',
                    'Collected Amount in Rupees (Incl of GST.) (Masked)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

if __name__ == "__main__":
    deals_path = r'C:\Users\Rampam Karthik\Downloads\Deal_funnel_Data.csv'
    wo_path = r'C:\Users\Rampam Karthik\Downloads\Work_Order_Tracker_Data.csv'
    
    deals_df = clean_deals(deals_path)
    wo_df = clean_work_orders(wo_path)
    
    deals_df.to_csv('cleaned_deals.csv', index=False)
    wo_df.to_csv('cleaned_work_orders.csv', index=False)
    
    print(f"Cleaned {len(deals_df)} deals and {len(wo_df)} work orders.")
