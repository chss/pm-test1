# Enterprise Business Case Intake Portal 💼

A premium, interactive multi-tab Streamlit web application designed to help teams structure, evaluate, and classify new business cases, KPIs, and corporate impact vectors.

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
    - **Revenue** (*No Impact, Protection, Increase*)
    - **Cost** (*No Impact, Avoidance, Saving*)
    - **Customer Experience** (*No impact, External, Internal*)
    - **Process Efficiency** (*No impact, Improvement*)
    - **Process Duration** (*No impact, Reduction*)
    - **Quality** (*No impact, Data, Product*)

- **🎛️ Console Panel (Sidebar)**
  - **Dynamic Progress Bar**: Live completion tracking for required fields.
  - **Executive Preview**: Real-time summary showing current business impacts and total KPIs defined.
  - **Demo Data Injector**: Click "Load Demo" to immediately fill the form with a mock business case (*Smart Inventory Optimization Engine*) for quick testing.
  - **Export Formats**: One-click downloads for compiled data as a structured **JSON** file or flat **CSV** spreadsheet.

- **🎨 Premium Visuals & Styling**
  - Out-of-the-box custom slate & indigo glassmorphism theme styling.
  - Beautiful typographic hierarchy powered by Google's *Outfit* font.
  - Micro-animations and responsive layouts.

---

## 🚀 Getting Started

### 📋 Prerequisites
Make sure you have Python 3.8+ installed.

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
The application will open in your default browser at `http://localhost:8501`.
