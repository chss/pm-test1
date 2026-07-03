# Capstone White Paper: Business Case Priority Intake Form

**Project Name:** Business Case Priority Intake Form  
**Course:** Capstone Project Submission  
**Date:** July 1, 2026  

---

## 1. Executive Summary and Problem Statement

Organizations struggle with project intake, management, and resource allocation. Subjective evaluation methods, unstructured input fields, and manual tracking lead to delayed approvals, misaligned investments, and fragmented data repositories. 

The **Business Case Priority Intake Form** resolves these issues by delivering a structured, secure, and intelligent web intake portal. It combines modern web-based form elements (Streamlit), serverless relational databases (Databricks SQL Warehouse), and agentic coordination (Google ADK 2.0) to standardize the collection and categorization of corporate initiatives.

### Core Problems Addressed
* **Data Incompleteness**: Traditional intake forms suffer from empty text fields, complicating analysis. By enforcing strict constraints on core fields (Project Name and Description) and auto-generating standard fallbacks (`"Not Applicable"`) for optional fields, we ensure data integrity.
* **Subjective Prioritization**: Initiatives are often prioritized based on influence rather than quantifiable business value. Our solution establishes a structured, rule-based prioritization mechanism.
* **Lack of Review Control**: Fully automated systems risk false positives, while fully manual systems create operational bottlenecks. Introducing a Human-in-the-Loop (HITL) step allows humans to review and override automated decisions.
* **Disconnected Data Warehouses**: Project documentation and databases are frequently disconnected. Direct Delta Lake integration ensures immediate, structured storage.

---

## 2. System Architecture

The application is built on a 3-tier decoupled architecture combining a responsive frontend portal, an agentic graph runtime, and an enterprise data warehouse.

```mermaid
graph TD
    User([User]) -->|1. Enters Form Data| UI[Streamlit Frontend]
    UI -->|2. Clicks Save / Submit| PA[Priority Agent Graph - ADK 2.0]
    PA -->|3. Invoke Gemini Semantic Engine| Gemini[Gemini 2.5 Flash API]
    Gemini -->|Calculated Priority & Discrepancies| PA
    PA -->|Priority A/B/C + Risk Matrix| HITL[RequestInput Interrupt]
    HITL -->|4. Yields Interrupt to UI| UI
    User -->|5. Confirms / Overrides Priority| UI
    UI -->|6. Resumes Workflow with Input| PA
    PA -->|7. Returns Final Priority Output| UI
    UI -->|8. Executes Param SQL Insert| DB[(Databricks SQL Warehouse)]
    DB -->|Delta Table| business_case_intake
```

### Architectural Components
1. **Frontend Portal (Streamlit)**: Serves as the user interface, styling the workspace with a clean light theme (`#ffffff` background and indigo `#4f46e5` accents). It calculates form completion progress dynamically and displays the Priority Agent's review card when interrupted.
2. **Orchestration Agent (Google ADK 2.0 Graph Workflow)**: Manages state, handles data schemas, executes business logic, and schedules human verification requests.
3. **Data Warehouse (Databricks Delta Lake)**: Serves as the repository, capturing the project name, description, dynamic KPIs (stored as JSON arrays), business impacts, and final priority assignments.

---

## 3. Solution Details and Agent Intelligence

### Intelligent Intake Form
The user enters qualitative details across three structured tabs:
* **Problem Statement**: Standardizes project definition, stakeholder analysis, and status-quo cost calculations.
* **Value and KPIs**: Focuses on value creation linkage and allows the user to dynamically add, remove, and track metrics.
* **Business Impact**: Collects strategic alignment vectors (Revenue, Cost, Customer Experience, Process Efficiency, Process Duration, and Quality).

### The Priority Agent Graph (ADK 2.0 Workflow)
The Priority Agent runs as an ADK 2.0 Graph Workflow consisting of a custom function node wired to the `START` entry point. It runs a **Gemini LLM Semantic Analyzer** on every submission to perform a deep compliance risk assessment and sanity check.

#### 1. Regulatory Risk & Quality Assessment
The agent evaluates the combined text fields against **5 High-Risk Categories** (aligned with ISO 14971 and FDA 21 CFR Part 820 QSR):
* **Intended Use & Classification**: Detects life-sustaining, implantable, or automated therapeutic decision-making functions (High severity -> Priority A).
* **Software & AI (SaMD/SiMD)**: Detects software code, AI/ML models, cloud connectivity, or cybersecurity vulnerabilities (Medium severity -> Priority B).
* **Materials & Biocompatibility**: Detects body contact, sterilization needs, or novel materials (Medium severity -> Priority B).
* **Clinical Data & Human Factors**: Detects complex clinical trials or human-error usability risks (Medium severity -> Priority B).
* **Design & Manufacturing Complexity**: Detects 3D printing, complex supply chains, or failure-prone components (Medium severity -> Priority B).
* **Direct Patient Safety**: Detects safety hazards, patient harm, or clinical risks (High severity -> Priority A).

Findings are rendered in a structured Markdown **Risk Matrix** mapping risks to standards (e.g. 21 CFR 820.30 Design Controls, 21 CFR 820.100 CAPA, 21 CFR 820.70 Production Controls, ISO 14971, IEC 62304).

#### 2. Business Impact Rules & Discrepancy Checks
The agent checks the business alignment radio selections:
* **Priority A**: Quality Assurance = `Product` OR Revenue = `Increase` OR Cost = `Saving`.
* **Priority B**: Customer Experience = `External`.
* **Priority C**: Everything else.

**Sanity Check Mismatch**: The LLM compares the text descriptions against your radio selections. If the description mentions a product quality revision or cost savings, but you selected "No impact" on the radios, the agent flags this discrepancy, warns the user, and auto-promotes the recommendation to the higher priority.

---

## 4. Database Schema

All submissions are stored in the catalog `pm_test1`, schema `pm_test1_schema`, and table `business_case_intake` with the following schema:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `project_name` | `STRING` | Unique identifying title of the project (Required) |
| `problem_solving` | `STRING` | Project description and core problem statement (Required) |
| `who_impacted` | `STRING` | Stakeholders and units impacted by the problem |
| `cost_impact` | `STRING` | Current operational/financial cost of the problem |
| `other_details` | `STRING` | Assumptions, constraints, or background information |
| `value_creation` | `STRING` | Direct linkage to value creation driver models |
| `kpis` | `STRING` | Serialized JSON array containing dynamic KPI metrics |
| `impact_revenue` | `STRING` | Revenue impact rating (Increase, Protection, No Impact) |
| `impact_cost` | `STRING` | Cost impact rating (Saving, Avoidance, No Impact) |
| `impact_cust_service` | `STRING` | Customer service audience (External, Internal, No impact) |
| `impact_efficiency` | `STRING` | Process efficiency impact (Improvement, No impact) |
| `impact_duration` | `STRING` | Process duration impact (Reduction, No impact) |
| `impact_quality` | `STRING` | Quality focus area (Product, Data, No impact) |
| `priority` | `STRING` | Final approved priority (A, B, or C) |
| `submitted_at` | `TIMESTAMP` | Server timestamp of database commit |

---

## 5. Further Enhancement Opportunities

The current implementation provides a foundation that can be expanded with the following enhancements:

* **Auto-Generated Financial Estimates**: Use LLMs to parse text inputs and estimate financial metrics, such as Return on Investment (ROI) or Net Present Value (NPV).
* **Multi-Stage Workflow Approvals**: Extend the graph with multiple `RequestInput` nodes to route priority reviews to managers and finance directors based on estimated budget thresholds.
* **System Integrations**: Set up webhooks or event loops to automatically sync approved entries to task management tools like Jira or ServiceNow.
* **Analytics Dashboards**: Build a Databricks SQL dashboard to visualize intake pipelines, KPI trends, and strategic resource allocation.

---

## 6. Conclusion

The **Business Case Priority Intake Form** demonstrates how agentic orchestration can improve business operations. Combining a user-friendly frontend, structured logic, and database integration reduces manual processing times, improves data quality, and establishes transparent governance. Leveraging the ADK 2.0 Graph Workflow API allows the application to balance automation with human oversight.
