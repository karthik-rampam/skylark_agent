# Decision Log: Monday.com Business Intelligence Agent

**Author:** Skylark BI Agent Team  
**Date:** March 10, 2026  
**Subject:** Architectural Decisions, Trade-offs, and Leadership Update Interpretation

---

## 1. Executive Summary
The Skylark BI Agent was developed to bridge the gap between messy, multi-source operational data on Monday.com and high-level executive decision-making. The solution focuses on real-time data ingestion, robust cleaning of "real-world messy data," and a premium conversational interface that provides both summarized metrics and granular record lookups.

---

## 2. Key Assumptions
During the development of this prototype, the following assumptions were made:

1.  **Founder-Level Priority**: We assumed that founders prioritize **speed and accuracy** over complex multi-step reasoning. Therefore, the engine was built to provide direct, verifiable numbers rather than speculative AI interpretations.
2.  **Data Inconsistency**: We assumed the Monday.com boards would contain historical inconsistencies (e.g., misspelled sectors, empty amount fields). The `BIEngine` was designed with a "permissive processing" layer to normalize these on-the-fly.
3.  **Real-Time Requirement**: We assumed that business decisions cannot be made on stale data. Consequently, we opted for a **Dynamic Fetching Strategy** where every user query triggers a fresh GraphQL call to Monday.com, rather than relying on a cached database.
4.  **Privacy by Design**: We assumed that while Founders need high-level views, they also occasionally need to "verify" the source. We implemented **Masked Search** capabilities to allow secure lookup of individual Customer IDs without exposing unnecessary metadata.

---

## 3. Technical Trade-offs

### A. Rule-Based Aggregation vs. Pure LLM Analysis
*   **Decision**: Implemented a robust, rule-based `BIEngine` for data processing.
*   **Reasoning**: LLMs are prone to "hallucinations" when performing complex arithmetic on large datasets. To ensure the Founder receives **accurate** financial revenue and pipeline values, we used Pandas for the heavy lifting. The "AI" aspect is focused on query understanding and mapping (e.g., mapping "energy" to "Renewables + Powerline").
*   **Trade-off**: Slightly less flexibility in "natural language" compared to a pure Agentic LLM, but 100% mathematical accuracy.

### B. Dynamic Fetching vs. Webhooks
*   **Decision**: Used live GraphQL API requests per query.
*   **Reasoning**: Implementing a full webhook architecture requires a 24/7 hosted listener and a database to store states. For a prototype, dynamic fetching ensures the data is always fresh without the overhead of database synchronization.
*   **Trade-off**: Higher latency (approx 1-2 seconds) per request compared to local DB lookups.

### C. Technology Stack (Flask + Vanilla JS)
*   **Decision**: Avoided heavy frameworks like React or Next.js.
*   **Reasoning**: A BI agent needs to be lightweight and fast. Vanilla JavaScript allowed for precise control over animations (like the triple-dot typing indicator) and visual chart rendering (Chart.js) without the "boilerplate" of a modern SPA framework.
*   **Trade-off**: Management of UI state is manual rather than reactive.

---

## 4. Interpretation of "Leadership Updates"
The assignment requested an implementation that helps prepare data for leadership updates. I interpreted this through three distinct pillars:

1.  **Report-Ready Summaries**: 
    The agent does not return raw data objects. Instead, it formats results into **Executive Bullet Points** (using `•` and custom headers) that can be directly copy-pasted into a weekly email or a Slide Deck.
    
2.  **Visual Storytelling (The Dashboard)**: 
    Leadership updates are rarely just text. The implementation includes an **Executive Dashboard** view that visualizes "Pipeline Value by Sector" and "Operational Status." This allows a leader to take a quick screenshot of the charts for their presentation.

3.  **Granular Evidence (Drill-Down)**: 
    A key part of leadership is being able to defend the numbers. By adding **Record Lookups** (e.g., *"Find Customer_Code_16"*), the agent allows the leader to quickly verify the "raw data" behind an aggregated total if questioned by other executives.

---

## 5. Future Roadmap (If more time were available)

1.  **Multi-Board Correlation**: Currently, the agent queries Deals and Work Orders. Future versions would implement a "Join" logic to track a project's lifecycle from the initial Sales Deal to the final Work Order completion automatically.
2.  **Predictive Forecasting**: Using historical "Close Dates" and project "Execution Status" to predict revenue slippage or pipeline bottlenecks before they happen.
3.  **Automated Slide Generation**: An export feature that generates a PDF or PowerPoint slide containing the current dashboard charts and a text summary based on the latest query.
4.  **Advanced SLM (Small Language Models)**: Fine-tuning a local model specifically on the company's business terminology to handle even more complex, multi-variable queries without external API costs.

---

## 6. Closing Note
The Skylark BI Agent strikes a balance between a premium technical implementation and a practical business tool. It prioritizes data resilience and accuracy, ensuring that Founders have a "single source of truth" they can trust.
