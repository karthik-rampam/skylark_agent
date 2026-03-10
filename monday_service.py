import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")
URL = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WO_BOARD_ID = os.getenv("WO_BOARD_ID")

def fetch_board_data(board_id):
    query = f"""
    {{
      boards(ids: [{board_id}]) {{
        items_page (limit: 500) {{
          items {{
            name
            column_values {{
              id
              text
              type
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post(URL, json={'query': query}, headers=HEADERS)
    data = response.json()
    
    items = data['data']['boards'][0]['items_page']['items']
    rows = []
    for item in items:
        row = {'name': item['name']}
        for val in item['column_values']:
            row[val['id']] = val['text']
        rows.append(row)
    
    return pd.DataFrame(rows)

def get_live_data():
    print("Fetching live data from Monday.com...")
    deals_raw = fetch_board_data(DEALS_BOARD_ID)
    wo_raw = fetch_board_data(WO_BOARD_ID)
    
    deals_df = deals_raw.rename(columns={
        'name': 'Deal Name',
        'text_mm1ayw2q': 'Owner code',
        'text_mm1aqmsz': 'Deal Status',
        'numeric_mm1arewa': 'Masked Deal value',
        'text_mm1a8e35': 'Sector/service',
        'text_mm1aetbs': 'Deal Stage',
        'date_mm1a40j0': 'Close Date (A)'
    })
    
    wo_df = wo_raw.rename(columns={
        'name': 'Deal name masked',
        'text_mm1avayg': 'Customer Name Code',
        'status': 'Execution Status',
        'text_mm1anya3': 'Sector',
        'numeric_mm1apzpt': 'Amount in Rupees (Excl of GST) (Masked)',
        'date_mm1arma8': 'Probable End Date'
    })
    
    return deals_df, wo_df
