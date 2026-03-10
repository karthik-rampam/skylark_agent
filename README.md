# Skylark BI Agent

An AI-powered Business Intelligence Agent that integrates with Monday.com to answer founder-level queries across Deals and Work Orders.

## Architecture Overview
- **Backend**: Python/Flask server.
- **BI Engine**: Custom logic to process and aggregate business metrics from Monday.com boards.
- **Frontend**: Premium HTML/CSS/JS chat interface.
- **Integration**: Monday.com GraphQL API.

## Setup Instructions

### 1. Monday.com Configuration
- Ensure you have a Monday.com API Token.
- The agent expects two boards:
    - **Deals**: IDs included in `app.py`.
    - **Work Orders**: IDs included in `app.py`.
- Run `upload_data.py` to clean the CSVs and populate the boards with the required schema.

### 2. Local Installation
1. Install dependencies:
   ```bash
   pip install flask pandas requests
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Access the agent at `http://localhost:5000`.

## Sample Queries
- "How's our pipeline looking for energy sector?"
- "What is the total revenue from work orders?"
- "Give me a summary of our operational metrics."
- "Show me deal stages for the mining sector."
