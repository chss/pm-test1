# Enterprise Business Case Intake Portal 💼

A premium, interactive multi-tab Streamlit web application designed to help teams structure, evaluate, and classify new business cases, KPIs, and corporate impact vectors. 

The application is tailored for **Medical Device Manufacturers** and integrates agentic compliance/safety checks aligned with **FDA 21 CFR Part 820** and **ISO 14971**.

---

## ✨ Features

- **📝 Tab 1: Problem Statement**
  - Project name identification.
  - Core problem framing and root-cause analysis.
  - Stakeholder impact evaluation.
  - Financial/qualitative cost assessment of not solving the issue.

- **🎯 Tab 2: KPI & Value Realization**
  - Narrative link between the initiative and value creation.
  - **Dynamic KPI Manager**: Add or remove multiple KPIs dynamically. Capture alignment, measurement protocols, and feasibility checks.

- **📊 Tab 3: Business Impact**
  - Standardized radio selectors to classify outcomes against key corporate dimensions:
    - **Revenue Influence** (*No Impact, Protection, Increase*)
    - **Cost Reduction** (*No Impact, Avoidance, Saving*)
    - **Customer Experience** (*No impact, External, Internal*)
    - **Quality Assurance** (*No impact, Data, Product*)

- **🤖 Tab 4: AI Copilot Assistant**
  - Live chat assistant that acts as a form completion coach.
  - Directly reads the live state of your input fields to suggest edits, draft KPIs, or clarify regulatory requirements.

- **🛡️ Tab 5: Priority Agent (ADK 2.0 Graph Workflow)**
  - Runs a structured **Gemini LLM Semantic Analysis** on every submission.
  - **Regulatory Safety Check**: Automatically reviews all fields for compliance, quality, or patient harm safety risks, mapping findings to **FDA 21 CFR Part 820** sections (e.g. Design Controls, Production Controls, CAPA) and international standards (e.g., ISO 14971, IEC 62304, ISO 10993).
  - **Discrepancy Sanity Check**: Compares your text inputs with Tab 3 radio selections. If you describe a high-impact initiative (like product QA or external customer service) but select "No impact" on the radios, the agent flags the discrepancy, issues a warning, and promotes the project to the higher recommended priority level.

---

## 🚦 Priority Logic Mapping

The final recommended priority is determined as the maximum of:
1. **Risk Severity**: High Risk/Safety -> **Priority A**; Medium Risk -> **Priority B**; Low/None -> **Priority C**.
2. **Business Impact Selection**:
   * **Priority A**: Quality Assurance = *Product*, Revenue = *Increase*, **OR** Cost = *Saving*.
   * **Priority B**: Customer Experience = *External*.
   * **Priority C**: Everything else.
3. **Text-Detected Business Targets (Sanity Promotion)**: If text descriptions mention product quality, revenue gains, cost savings, or customer service, they are mapped to their respective higher priorities (A or B) and warning notices are generated.

---

## 🚀 Getting Started

### 📋 Prerequisites
Make sure you have Python 3.11+ installed.

### ⚙️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/chss/pm-test1.git
   cd pm-test1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### ⚡ Running the App
Launch the Streamlit web application:
```bash
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`. Configure your **Gemini API Key** in the sidebar's integration settings to enable the Copilot and Priority Agent.
