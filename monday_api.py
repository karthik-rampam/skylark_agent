import requests
import pandas as pd

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYzMTAwMzU5NiwiYWFpIjoxMSwidWlkIjoxMDA4MTI0ODgsImlhZCI6IjIwMjYtMDMtMTBUMDU6MzA6NTAuMDkzWiIsInBlciI6Im1lOndyaXRlIiwiYWN0aWQiOjM0MTUzMjA4LCJyZ24iOiJhcHNlMiJ9.AZOk-IxPmlsSp5ST2gZMFGNrFbnx-cxacaq6Ted_H1o"

url = "https://api.monday.com/v2"

headers = {
    "Authorization": API_TOKEN
}

def get_board_data(board_id):

    query = f"""
    {{
      boards(ids: {board_id}) {{
        items {{
          name
          column_values {{
            title
            text
          }}
        }}
      }}
    }}
    """

    response = requests.post(url, json={'query': query}, headers=headers)

    data = response.json()

    rows = []

    items = data["data"]["boards"][0]["items"]

    for item in items:

        row = {"name": item["name"]}

        for col in item["column_values"]:
            row[col["title"]] = col["text"]

        rows.append(row)

    df = pd.DataFrame(rows)

    return df