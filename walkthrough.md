# Walkthrough - Streamlit Business Form Application

We have successfully built a fully functional, premium-designed multi-tab Streamlit web form application. The implementation incorporates custom theme colors, advanced responsive light-theme CSS styling, dynamic KPI management, real-time input status calculations, Databricks SQL Warehouse integration, and multiple export formats.

---

## 📂 Project Structure

All files have been initialized under:
`my-first-project/streamlit-business-form/`

- [.streamlit/config.toml](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/.streamlit/config.toml): Defines custom light theme background (`#ffffff`), secondary background (`#f8fafc`), text color (`#0f172a`), and active indicators (`#4f46e5`).
- [requirements.txt](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/requirements.txt): Lists base dependencies including `google-adk>=2.3.0` and `google-genai>=2.10.0`.
- [priority_workflow.py](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/priority_workflow.py): Implements the ADK 2.0 Graph Workflow API with a `determine_and_confirm_priority` node and `RequestInput` for confirmation overrides.
- [app.py](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/app.py): The main Streamlit file handling layout, forms, session state, Priority Agent execution/resumption, database integration, AI chat, and document exports.
- [app.yaml](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/app.yaml): Configuration file for Databricks Apps deployments.
- [.gitignore](file:///Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI%20Agents-Intensive%20Vibe%20Coding%20Course%20with%20Google/my-first-project/streamlit-business-form/.gitignore): Standard git rules.

---

## ✨ Implemented Features

### 1. Tab 1: Problem Statement
- **PROJECT NAME**: Free text input.
- **WHAT SPECIFIC PROBLEM ARE WE SOLVING?**: Multi-line description field.
- **WHO IS IMPACTED?**: Stakeholders / affected parties.
- **WHAT IS THE CURRENT COST/IMPACT OF NOT SOLVING THE PROBLEM?**: Qualitative/quantitative loss estimation.
- **OTHER DETAILS**: Extra assumptions/context.

### 2. Tab 2: KPI & Value Realization
- **Value Linkage**: Detailed description of how value is created.
- **Dynamic KPIs**: Allows users to dynamically **Add** or **Remove** KPI objects in session state. Each KPI includes:
  - KPI Description
  - Alignment to Existing KPI
  - How is it Measured?
  - Easily Measurable?

### 3. Tab 3: Business Impact
Provides horizontal radio selector groups for strategic alignment classification:
- **Revenue**: *No Impact, Protection, Increase*
- **Cost**: *No Impact, Avoidance, Saving*
- **Customer Experience**: *No impact, External, Internal*
- **Process Efficiency**: *No impact, Improvement*
- **Process Duration**: *No impact, Reduction*
- **Quality**: *No impact, Data, Product*

### 4. Tab 4: 💬 AI Copilot Business Case Assistant
- **Application Context Lock**: Configured with a strict system instruction to only answer questions about the form fields, definitions, and review the user's current inputs. It declines general knowledge or out-of-scope prompts.
- **Dynamic Live Feed**: Automatically reads the current inputs in the form (Project Name, KPIs list, problem statements, impacts) and references them in chat.
- **Interactive UI**: Supports streaming message replies, clear chat history, and suggested prompt shortcuts (*Review draft*, *Brainstorm KPIs*, *Explain impact options*).
- **Gemini Config**: Configured in the sidebar. Users can enter a personal API Key or deploy in Databricks Apps to use OAuth automatically.

### 5. ⚡ Priority Agent (ADK 2.0 Graph Workflow API)
Integrates an intelligent graph-based Priority Agent workflow between form submission and database insertion:
- **High-Risk Categories & Severity-Based Priority**:
  Evaluates all form fields (project name, description, stakeholders, cost impact, dependencies, KPIs) against 5 regulatory and quality risk areas:
  1. *Intended Use & Classification* (e.g., life-sustaining, implantable, or automated therapeutic decision-making).
  2. *Software & AI (SaMD/SiMD)* (e.g., software code, AI/ML models, cloud connectivity, cybersecurity vulnerabilities).
  3. *Materials & Biocompatibility* (e.g., body contact, sterilization needs, novel biomaterials).
  4. *Clinical Data & Human Factors* (e.g., clinical trials, usability/human error risks).
  5. *Design & Manufacturing Complexity* (e.g., 3D printing, complex supply chains, critical single-point failure components).
  * **Priority A**: Assigned if any *High* severity risk is identified.
  * **Priority B**: Assigned if any *Medium* severity risk is identified.
  * **Priority C**: Assigned otherwise.
- **Standard Business Rules Integration**:
  The risk priority is combined with the standard business rules priority, taking the highest classification:
  * **Priority A**: Revenue = *Increase* AND Cost = *Saving*.
  * **Priority B**: Customer Experience = *External* OR Quality = *Product*.
  * **Priority C**: Default.
- **Structured Rationale Markdown**:
  Generates a formal, regulatory-aligned review report returned directly to the UI, consisting of:
  * `### 1. Risk Summary`: A 2-3 sentence overview of compliance or quality gaps.
  * `### 2. Risk Matrix`: A formatted Markdown table listing the risk areas, identified risks, severity (Low/Medium/High), and applicable standards (e.g., ISO 14971, IEC 62304, ISO 10993, IEC 62366, ISO 13485, and FDA 21 CFR Part 820 sections like 820.30 Design Controls or 820.100 CAPA).
- **Human-in-the-loop (HITL) Validation**:
  - Automatically runs the workflow upon submit.
  - Pauses execution and displays the structured Markdown review report natively in the UI.
  - Allows the user to confirm the assignment or override it to *A, B, or C*.
  - Upon user confirmation, resumes the workflow run with the override/selection and retrieves the final outcome.
- **Databricks Sync**: Saves the final approved priority under the column `priority` in the Databricks table `pm_test1.pm_test1_schema.business_case_intake`.

### 6. Interactive Console & Live Preview (Sidebar)
- **Demo Mode**: Allows you to click **"Load Demo"** to instantly inject a pre-written business case.
- **Form Reset**: Clear all fields at once with **"Clear Form"**.
- **Progress Tracker**: Displays a dynamic completion status bar.
- **Integration Settings**: Consolidated settings containing `🔐 Databricks Warehouse` configs and `✨ Gemini API Config`.
- **White Sidebar Styling**: Force styled to render a clean white background with black text for high readability and visual contrast.
- **Save Action**: Syncs form data to Databricks SQL Warehouse table (`pm_test1.pm_test1_schema.business_case_intake`).
- **Export Actions**: Export as **JSON**, **CSV** spreadsheets, or generate and download a professional Microsoft Word **Project Charter** (`.docx`) file.

---

## 🚀 How to Run the Application

To start the application, navigate to the directory and run:

```bash
cd "/Users/jariwm1/Library/CloudStorage/OneDrive-MedtronicPLC/Documents/AI Agents-Intensive Vibe Coding Course with Google/my-first-project/streamlit-business-form"
streamlit run app.py
```

Streamlit will automatically launch the web interface in your default browser at `http://localhost:8501`.
