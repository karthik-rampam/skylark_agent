from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from bi_engine import BIEngine
from monday_service import get_live_data

app = Flask(__name__, static_folder='public')

# Initial load
try:
    deals_df, wo_df = get_live_data()
    bi_engine = BIEngine(deals_df, wo_df)
except Exception as e:
    print(f"Error loading initial data: {e}")
    deals_df = pd.read_csv('cleaned_deals.csv')
    wo_df = pd.read_csv('cleaned_work_orders.csv')
    bi_engine = BIEngine(deals_df, wo_df)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Fetch live data to ensure "real-time" response
    try:
        live_deals, live_wo = get_live_data()
        global bi_engine
        bi_engine = BIEngine(live_deals, live_wo)
    except Exception as e:
        print(f"Error fetching live data: {e}")
    
    result = bi_engine.answer_query(message)
    
    # Format the response
    if isinstance(result, dict):
        if "search_results" in result:
            results = result["search_results"]
            if isinstance(results, str):
                response_text = results
            else:
                response_text = f"### Search Results ({len(results)} found)\n\n"
                for i, res in enumerate(results, 1):
                    res_type = res.pop("type", "Record")
                    response_text += f"**{i}. {res_type}**\n"
                    for k, v in res.items():
                        response_text += f"• {k.capitalize()}: {v}\n"
                    response_text += "\n"
        else:
            response_text = "### Business Intelligence Summary\n"
            for key, val in result.items():
                display_name = key.replace('_', ' ').capitalize()
                if isinstance(val, dict):
                    response_text += f"**{display_name}**:\n"
                    for sub_key, sub_val in val.items():
                        response_text += f"• {sub_key}: {sub_val}\n"
                else:
                    response_text += f"**{display_name}**: {val}\n"
    else:
        response_text = result
        
    return jsonify({
        "response": response_text,
        "data": result if isinstance(result, dict) else None
    })

@app.route('/api/dashboard', methods=['GET'])
def dashboard_data():
    try:
        live_deals, live_wo = get_live_data()
        engine = BIEngine(live_deals, live_wo)
        
        # Aggregated data for charts
        pipeline_data = engine.deals.groupby('Sector/service')['Value'].sum().to_dict()
        ops_data = engine.wo['Execution Status'].value_counts().to_dict()
        
        return jsonify({
            "pipeline": pipeline_data,
            "ops": ops_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)