import json
import pandas as pd
from datetime import datetime

class BIEngine:
    def __init__(self, deals_df, wo_df):
        self.deals = deals_df
        self.wo = wo_df
        self._preprocess()

    def _preprocess(self):
        # Filter out rows that are actually repeated headers
        if 'Deal Name' in self.deals.columns:
            self.deals = self.deals[self.deals['Deal Name'] != 'Deal Name']
        if 'Sector/service' in self.deals.columns:
            self.deals = self.deals[self.deals['Sector/service'] != 'Sector/service']
        if 'Deal name masked' in self.wo.columns:
            self.wo = self.wo[self.wo['Deal name masked'] != 'Deal name masked']
            
        # Convert numeric columns
        if 'Value' not in self.deals.columns and 'Masked Deal value' in self.deals.columns:
            self.deals['Value'] = pd.to_numeric(self.deals['Masked Deal value'], errors='coerce').fillna(0)
        
        if 'Amount' not in self.wo.columns and 'Amount in Rupees (Excl of GST) (Masked)' in self.wo.columns:
            self.wo['Amount'] = pd.to_numeric(self.wo['Amount in Rupees (Excl of GST) (Masked)'], errors='coerce').fillna(0)
        
        # Convert dates
        if 'Created Date' in self.deals.columns:
            self.deals['Created Date'] = pd.to_datetime(self.deals['Created Date'], errors='coerce')
        if 'Probable End Date' in self.wo.columns:
            self.wo['Probable End Date'] = pd.to_datetime(self.wo['Probable End Date'], errors='coerce')

    def get_pipeline_summary(self, sector=None):
        df = self.deals
        if sector:
            # Semantic mapping for "energy"
            if sector.lower() == "energy":
                sector_query = "Renewables|Powerline"
            else:
                sector_query = sector
                
            sector_col = 'Sector/service' if 'Sector/service' in df.columns else 'Sector'
            if sector_col in df.columns:
                # Use regex for multi-sector "energy" mapping
                df = df[df[sector_col].str.contains(sector_query, case=False, na=False)]
        
        summary = {
            "total_deals": len(df),
            "total_value": f"INR {df['Value'].sum():,.2f}" if 'Value' in df.columns else "0",
            "avg_value": f"INR {df['Value'].mean():,.2f}" if 'Value' in df.columns and len(df) > 0 else "0",
            "stages": df['Deal Stage'].value_counts().to_dict() if 'Deal Stage' in df.columns else {},
            "status": df['Deal Status'].value_counts().to_dict() if 'Deal Status' in df.columns else {}
        }
        return summary

    def get_operational_metrics(self):
        summary = {
            "total_work_orders": len(self.wo),
            "total_revenue": f"INR {self.wo['Amount'].sum():,.2f}" if 'Amount' in self.wo.columns else "0",
            "status_distribution": self.wo['Execution Status'].value_counts().to_dict() if 'Execution Status' in self.wo.columns else {},
            "sector_performance": {k: f"INR {v:,.2f}" for k, v in self.wo.groupby('Sector')['Amount'].sum().to_dict().items()} if 'Sector' in self.wo.columns and 'Amount' in self.wo.columns else {}
        }
        return summary

    def lookup_record(self, search_term):
        results = []
        search_term = search_term.lower()
        
        # Search in Deals
        deals_match = self.deals[
            self.deals['Deal Name'].str.contains(search_term, case=False, na=False) |
            self.deals['Owner code'].str.contains(search_term, case=False, na=False)
        ]
        
        for _, row in deals_match.head(5).iterrows():
            results.append({
                "type": "Deal",
                "name": row['Deal Name'],
                "status": row['Deal Status'],
                "value": f"INR {row['Value']:,.2f}",
                "stage": row.get('Deal Stage', 'N/A')
            })
            
        # Search in Work Orders
        wo_match = self.wo[
            self.wo['Deal name masked'].str.contains(search_term, case=False, na=False) |
            self.wo['Customer Name Code'].str.contains(search_term, case=False, na=False)
        ]
        
        for _, row in wo_match.head(5).iterrows():
            results.append({
                "type": "Work Order",
                "customer": row['Customer Name Code'],
                "project": row['Deal name masked'],
                "status": row['Execution Status'],
                "amount": f"INR {row['Amount']:,.2f}"
            })
            
        return results if results else "No specific records found for that search term."

    def answer_query(self, query):
        query = query.lower()
        
        # Keywords that trigger a specific search/lookup
        search_keywords = ["who is", "find", "search", "customer", "deal", "code", "summary", "about", "details"]
        if any(keyword in query for keyword in search_keywords):
            # Clean the query to extract the most likely ID
            clean_query = query
            fillers = ["give me", "find me", "who is", "about", "what is", "details of", "summary of", "deal name", "customer"]
            for f in fillers:
                clean_query = clean_query.replace(f, "")
            
            # Additional aggressive cleaning
            words = clean_query.split()
            significant_words = [w for w in words if w not in ["a", "the", "of", "summary", "find", "search", "give"]]
            
            if significant_words:
                search_term = significant_words[-1] # Usually the ID is at the end
            else:
                search_term = clean_query.strip()
            
            # Final check: if the query has a word with _ its likely the search term
            for w in query.split():
                if "_" in w:
                    search_term = w
                    break

            if len(search_term) >= 3:
                return {"search_results": self.lookup_record(search_term)}

        if "pipeline" in query:
            sector = None
            for s in ["energy", "mining", "powerline", "renewables", "railways", "dsp"]:
                if s in query:
                    sector = s
                    break
            return self.get_pipeline_summary(sector)
        elif "operational" in query or "work order" in query or "revenue" in query or "metrics" in query:
            return self.get_operational_metrics()
        else:
            return "I'm sorry, I couldn't find specific metrics. Try asking about 'pipeline', 'operational metrics', or search for a specific customer code like 'Customer_Code_16'."
