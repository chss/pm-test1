from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import json
import re

class ProjectData(BaseModel):
    project_name: str
    problem_solving: str
    who_impacted: str
    cost_impact: str
    other_details: str
    value_creation: str
    kpis_json: str
    impact_revenue: str
    impact_cost: str
    impact_cust_service: str
    impact_quality: str

def has_any_match(text, term_list):
    for term in term_list:
        # Enforce word boundaries for short terms to prevent false substring matches (e.g. 'ai' in 'details')
        if len(term) <= 3:
            pattern = r'\b' + re.escape(term) + r'\b'
        else:
            pattern = re.escape(term)
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

@node(rerun_on_resume=True)
async def determine_and_confirm_priority(ctx: Context, node_input: ProjectData):
    print("--- NODE RUNNING ---")
    
    # 1. Combine all field information
    combined_text = "\n".join([
        f"Project Name: {node_input.project_name}",
        f"Description: {node_input.problem_solving}",
        f"Who is Impacted: {node_input.who_impacted}",
        f"Cost Impact: {node_input.cost_impact}",
        f"Other Details: {node_input.other_details}",
        f"Value Creation: {node_input.value_creation}",
        f"KPIs Table: {node_input.kpis_json}"
    ])
    
    max_severity = "Low"
    risks = []
    
    # Business impact detection states (from text analysis)
    detected_product_quality = False
    detected_revenue_increase = False
    detected_cost_saving = False
    detected_external_cx = False
    discrepancy_explanation = ""
    
    # Always run keyword checks for compliance and safety risks
    # Category 1: Intended Use
    if has_any_match(combined_text, ["implant", "life-sustaining", "therapeutic", "critical care", "pacemaker", "ventilator"]):
        risks.append({
            "risk_area": "Intended Use & Classification",
            "specific_risk": "Description suggests life-sustaining or implantable system functions.",
            "severity": "High",
            "applicable_standard": "FDA Class III / ISO 14971 / 21 CFR 820.30 (Design Controls - Risk Analysis)"
        })
        max_severity = "High"
        
    # Category 2: Software & AI
    if has_any_match(combined_text, ["software", "ai", "ml", "algorithm", "cybersecurity", "cloud", "connectivity"]):
        risks.append({
            "risk_area": "Software & AI (SaMD/SiMD)",
            "specific_risk": "System involves cloud connectivity, software controls, or AI/ML algorithms.",
            "severity": "Medium",
            "applicable_standard": "IEC 62304 / FDA SaMD Guidance / 21 CFR 820.30 (Design Controls - Software Validation)"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 3: Materials
    if has_any_match(combined_text, ["material", "biocompatib", "steril", "invasive", "tissue contact"]):
        risks.append({
            "risk_area": "Materials & Biocompatibility",
            "specific_risk": "Mentions sterilization, body contact, or novel biomaterials.",
            "severity": "Medium",
            "applicable_standard": "ISO 10993 / 21 CFR 820.30 (Design Verification) / 21 CFR 820.50 (Purchasing Controls)"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 4: Clinical
    if has_any_match(combined_text, ["clinical trial", "human factors", "usability", "human error"]):
        risks.append({
            "risk_area": "Clinical Data & Human Factors",
            "specific_risk": "Requires human factors usability verification or complex clinical trials.",
            "severity": "Medium",
            "applicable_standard": "IEC 62366 / 21 CFR 820.30 (Design Validation - Usability & Human Factors)"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 5: Manufacturing
    if has_any_match(combined_text, ["3d print", "additive manufacturing", "supply chain", "prone to failure", "failure"]):
        risks.append({
            "risk_area": "Design & Manufacturing Complexity",
            "specific_risk": "Involves complex assembly, novel fabrication methods, or failure-prone components.",
            "severity": "Medium",
            "applicable_standard": "ISO 13485 / 21 CFR 820.70 (Production and Process Controls) / 21 CFR 820.75 (Process Validation)"
        })
        if max_severity != "High":
            max_severity = "Medium"

    # Patient safety direct keywords check
    safety_terms = ["patient safety", "patient harm", "harm to patient", "injury to patient", "patient injury", "adverse event", "patient risk", "clinical risk", "medical risk", "patient impact", "harming patients"]
    if has_any_match(combined_text, safety_terms):
        risks.append({
            "risk_area": "Product Compliance & Quality (Patient Safety)",
            "specific_risk": "Direct mention of patient safety risk or patient harm in intake fields.",
            "severity": "High",
            "applicable_standard": "ISO 14971 / 21 CFR 820.100 (Corrective and Preventive Action - CAPA) / 21 CFR 820.30 (Design Controls - Risk Analysis)"
        })
        max_severity = "High"

    risk_summary = f"Identified {len(risks)} compliance or quality risk areas in the form fields. The highest detected risk severity is {max_severity}."
    if not risks:
        risk_summary = "No high-risk compliance or quality issues were identified in the form fields."

    # Gemini AI Semantic Analysis (incorporating business impact semantic checks and sanity tests)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Analyze the following medical product/project data from a business case intake form against these 5 High-Risk Categories:
            1. Intended Use & Classification: High-risk classification (e.g., life-sustaining, implantable, or automated therapeutic decision-making).
            2. Software & AI (SaMD/SiMD): Software, AI/ML algorithms, cloud connectivity, or cybersecurity vulnerabilities.
            3. Materials & Biocompatibility: Novel materials, invasive contact with the human body, or sterilization needs.
            4. Clinical Data & Human Factors: Clinical trials, high usability/human error risks.
            5. Design & Manufacturing Complexity: Complex supply chains, novel manufacturing (like 3D printing), critical components prone to failure.

            Also evaluate if the text suggests, even remotely, the following business impact categories:
            - Product Quality target (e.g. product revision, product quality QA, manufacturing quality, compliance)
            - Revenue Increase target (e.g. sales growth, market share protection, direct revenue generation)
            - Cost Saving target (e.g. cost reduction, waste reduction, operational efficiency savings)
            - External Customer Experience target (e.g. customer/patient satisfaction, NPS, customer support, external usability)

            Input Text:
            {combined_text}

            Evaluate the severity of risks identified in each category. Recommend a maximum severity of 'High', 'Medium', or 'Low'.
            For each risk identified, provide Risk Area, Specific Risk, Severity, and Applicable Standard.

            Format your output strictly as a JSON object with:
            1. "max_severity": "High" | "Medium" | "Low"
            2. "risk_summary": A 2-3 sentence overview of the most critical compliance or quality gaps found.
            3. "risks": A list of objects containing: "risk_area", "specific_risk", "severity", "applicable_standard"
            4. "detected_product_quality": boolean
            5. "detected_revenue_increase": boolean
            6. "detected_cost_saving": boolean
            7. "detected_external_cx": boolean
            8. "discrepancy_explanation": string (A detailed justification explaining any discrepancies between these detected targets and standard non-impact states).
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            res_data = json.loads(response.text)
            ai_max_severity = res_data.get("max_severity", "Low")
            ai_risk_summary = res_data.get("risk_summary", "")
            ai_risks = res_data.get("risks", [])
            
            detected_product_quality = res_data.get("detected_product_quality", False)
            detected_revenue_increase = res_data.get("detected_revenue_increase", False)
            detected_cost_saving = res_data.get("detected_cost_saving", False)
            detected_external_cx = res_data.get("detected_external_cx", False)
            discrepancy_explanation = res_data.get("discrepancy_explanation", "")
            
            severity_order = {"High": 3, "Medium": 2, "Low": 1}
            if severity_order[ai_max_severity] > severity_order[max_severity]:
                max_severity = ai_max_severity
                
            if ai_risk_summary:
                risk_summary = ai_risk_summary
                
            existing_areas = {r["risk_area"].lower() for r in risks}
            for ar in ai_risks:
                if ar.get("risk_area", "").lower() not in existing_areas:
                    risks.append(ar)
                    existing_areas.add(ar.get("risk_area", "").lower())
                    
        except Exception as e:
            print("Gemini semantic analysis failed, relying on keyword rules:", e)

    # Fallback keyword checks for business impact categories if Gemini was offline/absent
    if not api_key:
        detected_product_quality = has_any_match(combined_text, ["product revision", "product quality", "defect", "regulatory compliance", "qa", "quality assurance"])
        detected_revenue_increase = has_any_match(combined_text, ["revenue", "sales", "increase revenue", "market share"])
        detected_cost_saving = has_any_match(combined_text, ["saving", "cost reduction", "reduce cost", "lower cost"])
        detected_external_cx = has_any_match(combined_text, ["customer experience", "nps", "customer service", "user experience", "external customer"])

    # Determine risk-based priority
    risk_priority = "C"
    if max_severity == "High":
        risk_priority = "A"
    elif max_severity == "Medium":
        risk_priority = "B"
        
    # Read user's actual radio button inputs
    rev = node_input.impact_revenue
    cost = node_input.impact_cost
    cust = node_input.impact_cust_service
    qual = node_input.impact_quality
    
    # Calculate priority based on radio selections
    radio_priority = "C"
    if qual == "Product" or rev == "Increase" or cost == "Saving":
        radio_priority = "A"
    elif cust == "External":
        radio_priority = "B"
        
    # Sanity check: evaluate priority suggested by text fields
    text_priority = "C"
    discrepancy_reasons = []
    
    if detected_product_quality:
        text_priority = "A"
        if qual != "Product":
            discrepancy_reasons.append("Text mentions product QA/revision, but Quality Assurance radio button was set to 'No impact'.")
    elif detected_revenue_increase:
        text_priority = "A"
        if rev != "Increase":
            discrepancy_reasons.append("Text mentions revenue generation or sales, but Revenue Influence radio button was set to 'No impact'.")
    elif detected_cost_saving:
        text_priority = "A"
        if cost != "Saving":
            discrepancy_reasons.append("Text mentions cost reduction or savings, but Cost Reduction radio button was set to 'No impact'.")
            
    if detected_external_cx and text_priority != "A":
        text_priority = "B"
        if cust != "External":
            discrepancy_reasons.append("Text mentions customer experience or NPS, but Customer Experience radio button was set to 'No impact'.")

    # Combine evaluations: take highest priority (A > B > C)
    priority_order = {"A": 3, "B": 2, "C": 1}
    final_calculated_priority = "C"
    
    # Compare risk, radio, and text-based priorities
    for p in [risk_priority, radio_priority, text_priority]:
        if priority_order[p] > priority_order[final_calculated_priority]:
            final_calculated_priority = p
            
    # Compile markdown output format
    reason_markdown = f"### 1. Risk Summary\n{risk_summary}\n\n### 2. Risk Matrix\n"
    if risks:
        reason_markdown += "| Risk Area | Specific Risk Identified | Severity | Applicable Standard/Regulation |\n"
        reason_markdown += "| :--- | :--- | :--- | :--- |\n"
        for r in risks:
            reason_markdown += f"| {r.get('risk_area')} | {r.get('specific_risk')} | {r.get('severity')} | {r.get('applicable_standard')} |\n"
    else:
        reason_markdown += "*No risk categories identified.*\n"
        
    # Append Sanity Check Warning section if there's a discrepancy
    if discrepancy_reasons:
        reason_markdown += "\n### 3. Business Impact Discrepancy Check\n"
        reason_markdown += "⚠️ **Sanity Check Warning**: The Priority Agent detected a mismatch between your text details and radio selections:\n"
        for reason in discrepancy_reasons:
            reason_markdown += f"- {reason}\n"
        if discrepancy_explanation:
            reason_markdown += f"\n*AI Analysis*: {discrepancy_explanation}\n"
        reason_markdown += f"\nRecommended priority has been promoted to **Priority {final_calculated_priority}** to align with the text inputs.\n"

    # 2. Check if we have received a response to our RequestInput
    if not ctx.resume_inputs or "confirm_priority" not in ctx.resume_inputs:
        print("Yielding RequestInput with calculated priority and structured reason...")
        yield RequestInput(
            interrupt_id="confirm_priority",
            message=f"calculated_priority:{final_calculated_priority}:{reason_markdown}"
        )
        return
        
    # 3. Read reply & process override
    reply_data = ctx.resume_inputs["confirm_priority"]
    if isinstance(reply_data, dict):
        user_reply = reply_data.get("confirm_priority", "")
        if not user_reply and len(reply_data) == 1:
            user_reply = list(reply_data.values())[0]
    else:
        user_reply = str(reply_data)
        
    user_reply = user_reply.strip()
    print("User replied:", user_reply)
    
    final_priority = final_calculated_priority
    if user_reply.upper() in ["A", "B", "C"]:
        final_priority = user_reply.upper()
        
    print("Yielding final event with priority:", final_priority)
    yield Event(output={"priority": final_priority})

# Create priority workflow agent
priority_workflow = Workflow(
    name="priority_workflow",
    input_schema=ProjectData,
    edges=[
        ('START', determine_and_confirm_priority)
    ]
)
