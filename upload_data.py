import requests
import json
import pandas as pd
import time

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYzMTAwMzU5NiwiYWFpIjoxMSwidWlkIjoxMDA4MTI0ODgsImlhZCI6IjIwMjYtMDMtMTBUMDU6MzA6NTAuMDkzWiIsInBlciI6Im1lOndyaXRlIiwiYWN0aWQiOjM0MTUzMjA4LCJyZ24iOiJhcHNlMiJ9.AZOk-IxPmlsSp5ST2gZMFGNrFbnx-cxacaq6Ted_H1o"
URL = "https://api.monday.com/v2"
HEADERS = {"Authorization": API_TOKEN, "Content-Type": "application/json"}

DEALS_BOARD_ID = "5027108399"
WO_BOARD_ID = "5027108604"

def query_monday(query, variables=None):
    payload = {'query': query}
    if variables:
        payload['variables'] = variables
    response = requests.post(URL, json=payload, headers=HEADERS)
    return response.json()

def clear_board(board_id):
    print(f"Clearing board {board_id}...")
    query = f"{{ boards(ids: [{board_id}]) {{ items_page {{ items {{ id }} }} }} }}"
    res = query_monday(query)
    items = res['data']['boards'][0]['items_page']['items']
    for item in items:
        del_query = f"mutation {{ delete_item (item_id: {item['id']}) {{ id }} }}"
        query_monday(del_query)

def add_item(board_id, item_name, column_values):
    query = """
    mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
        create_item (board_id: $boardId, item_name: $itemName, column_values: $columnValues) {
            id
        }
    }
    """
    vars = {
        "boardId": board_id,
        "itemName": str(item_name),
        "columnValues": json.dumps(column_values)
    }
    return query_monday(query, vars)

def upload_data():
    deals_df = pd.read_csv('cleaned_deals.csv')
    wo_df = pd.read_csv('cleaned_work_orders.csv')
    
    # Filter out potential repeated headers
    deals_df = deals_df[deals_df['Deal Name'] != 'Deal Name']
    wo_df = wo_df[wo_df['Deal name masked'] != 'Deal name masked']
    
    # Precise Mappings from debug_columns.json
    deal_map = {
        "Owner": "text_mm1ayw2q",
        "Status": "text_mm1aqmsz",
        "Value": "numeric_mm1arewa",
        "Sector": "text_mm1a8e35",
        "Stage": "text_mm1aetbs",
        "Close Date": "date_mm1a40j0"
    }
    
    wo_map = {
        "Customer": "text_mm1avayg",
        "Status": "status", # Map to the actual 'status' column type for colors
        "Sector": "text_mm1anya3",
        "Amount": "numeric_mm1apzpt",
        "End Date": "date_mm1arma8"
    }
    
    # Clear boards first
    clear_board(DEALS_BOARD_ID)
    clear_board(WO_BOARD_ID)
    
    print("Uploading deals...")
    for _, row in deals_df.head(100).iterrows(): # Upload 100 for better demo
        vals = {
            deal_map["Owner"]: str(row["Owner code"]),
            deal_map["Status"]: str(row["Deal Status"]),
            deal_map["Value"]: float(row["Masked Deal value"]),
            deal_map["Sector"]: str(row["Sector/service"]),
            deal_map["Stage"]: str(row["Deal Stage"])
        }
        if pd.notna(row["Close Date (A)"]): 
            vals[deal_map["Close Date"]] = {"date": str(row["Close Date (A)"])}
        add_item(DEALS_BOARD_ID, row["Deal Name"], vals)

    print("Uploading work orders...")
    for _, row in wo_df.head(100).iterrows():
        vals = {
            wo_map["Customer"]: str(row["Customer Name Code"]),
            wo_map["Sector"]: str(row["Sector"]),
            wo_map["Amount"]: float(row["Amount in Rupees (Excl of GST) (Masked)"])
        }
        
        # Mapping status to Monday's status column might require label matching, 
        # but let's try setting text first. If it's a 'status' type, it might need 'label'.
        # For 'status' type column, we usually set the index or label.
        vals[wo_map["Status"]] = {"label": str(row["Execution Status"])}
        
        if pd.notna(row["Probable End Date"]):
            vals[wo_map["End Date"]] = {"date": str(row["Probable End Date"])}
            
        add_item(WO_BOARD_ID, row["Deal name masked"], vals)

if __name__ == "__main__":
    # setup_boards() # Run this once manually if needed
    upload_data()
