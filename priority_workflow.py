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
    
    # Always run the base keyword checks
    # Category 1: Intended Use
    if has_any_match(combined_text, ["implant", "life-sustaining", "therapeutic", "critical care", "pacemaker", "ventilator"]):
        risks.append({
            "risk_area": "Intended Use & Classification",
            "specific_risk": "Description suggests life-sustaining or implantable system functions.",
            "severity": "High",
            "applicable_standard": "FDA Class III / ISO 14971"
        })
        max_severity = "High"
        
    # Category 2: Software & AI
    if has_any_match(combined_text, ["software", "ai", "ml", "algorithm", "cybersecurity", "cloud", "connectivity"]):
        risks.append({
            "risk_area": "Software & AI (SaMD/SiMD)",
            "specific_risk": "System involves cloud connectivity, software controls, or AI/ML algorithms.",
            "severity": "Medium",
            "applicable_standard": "IEC 62304 / FDA SaMD Guidance"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 3: Materials
    if has_any_match(combined_text, ["material", "biocompatib", "steril", "invasive", "tissue contact"]):
        risks.append({
            "risk_area": "Materials & Biocompatibility",
            "specific_risk": "Mentions sterilization, body contact, or novel biomaterials.",
            "severity": "Medium",
            "applicable_standard": "ISO 10993"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 4: Clinical
    if has_any_match(combined_text, ["clinical trial", "human factors", "usability", "human error"]):
        risks.append({
            "risk_area": "Clinical Data & Human Factors",
            "specific_risk": "Requires human factors usability verification or complex clinical trials.",
            "severity": "Medium",
            "applicable_standard": "IEC 62366"
        })
        if max_severity != "High":
            max_severity = "Medium"
            
    # Category 5: Manufacturing
    if has_any_match(combined_text, ["3d print", "additive manufacturing", "supply chain", "prone to failure", "failure"]):
        risks.append({
            "risk_area": "Design & Manufacturing Complexity",
            "specific_risk": "Involves complex assembly, novel fabrication methods, or failure-prone components.",
            "severity": "Medium",
            "applicable_standard": "ISO 13485"
            })
        if max_severity != "High":
            max_severity = "Medium"

    # Standard rule check for patient safety direct keywords
    safety_terms = ["patient safety", "patient harm", "harm to patient", "injury to patient", "patient injury", "adverse event", "patient risk", "clinical risk", "medical risk", "patient impact", "harming patients"]
    if has_any_match(combined_text, safety_terms):
        # Direct mention of safety harm promoted to High severity (Priority A)
        risks.append({
            "risk_area": "Product Compliance & Quality (Patient Safety)",
            "specific_risk": "Direct mention of patient safety risk or patient harm in intake fields.",
            "severity": "High",
            "applicable_standard": "ISO 14971 (Risk Management)"
        })
        max_severity = "High"

    risk_summary = f"Identified {len(risks)} compliance or quality risk areas in the form fields. The highest detected risk severity is {max_severity}."
    if not risks:
        risk_summary = "No high-risk compliance or quality issues were identified in the form fields."

    # Supplement/Refine using Gemini AI Semantic Analysis if API key is present
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

            Input Text:
            {combined_text}

            Evaluate the severity of risks identified in each category. Recommend a maximum severity of 'High', 'Medium', or 'Low'.
            For each risk identified, provide:
            - Risk Area (e.g. Intended Use & Classification, Software & AI (SaMD/SiMD), Materials & Biocompatibility, Clinical Data & Human Factors, Design & Manufacturing Complexity)
            - Specific Risk Identified (detailing what in the text suggests this risk)
            - Severity (Low, Medium, or High)
            - Applicable Standard/Regulation (e.g., ISO 14971, FDA SaMD Guidance, ISO 10993, IEC 62366, ISO 13485)

            Format your output strictly as a JSON object with:
            1. "max_severity": "High" | "Medium" | "Low"
            2. "risk_summary": A 2-3 sentence overview of the most critical compliance or quality gaps found.
            3. "risks": A list of objects containing: "risk_area", "specific_risk", "severity", "applicable_standard"
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
            
            # Combine AI results with keyword results
            severity_order = {"High": 3, "Medium": 2, "Low": 1}
            if severity_order[ai_max_severity] > severity_order[max_severity]:
                max_severity = ai_max_severity
                
            if ai_risk_summary:
                risk_summary = ai_risk_summary
                
            # Avoid duplicate risk areas from AI and keywords
            existing_areas = {r["risk_area"].lower() for r in risks}
            for ar in ai_risks:
                if ar.get("risk_area", "").lower() not in existing_areas:
                    risks.append(ar)
                    existing_areas.add(ar.get("risk_area", "").lower())
                    
        except Exception as e:
            print("Gemini semantic analysis failed, relying on keyword rules:", e)

    # Map Risk Severity to Priority
    # High -> Priority A, Medium -> Priority B, Low/None -> Priority C
    risk_priority = "C"
    if max_severity == "High":
        risk_priority = "A"
    elif max_severity == "Medium":
        risk_priority = "B"
        
    # Standard business impact rules
    rev = node_input.impact_revenue
    cost = node_input.impact_cost
    cust = node_input.impact_cust_service
    qual = node_input.impact_quality
    
    business_priority = "C"
    if rev == "Increase" and cost == "Saving":
        business_priority = "A"
    elif cust == "External" or qual == "Product":
        business_priority = "B"
        
    # Combine evaluations: take highest priority (A > B > C)
    priority_order = {"A": 3, "B": 2, "C": 1}
    final_calculated_priority = "C"
    if priority_order[risk_priority] >= priority_order[business_priority]:
        final_calculated_priority = risk_priority
    else:
        final_calculated_priority = business_priority
        
    # Compile markdown output format
    reason_markdown = f"### 1. Risk Summary\n{risk_summary}\n\n### 2. Risk Matrix\n"
    if risks:
        reason_markdown += "| Risk Area | Specific Risk Identified | Severity | Applicable Standard/Regulation |\n"
        reason_markdown += "| :--- | :--- | :--- | :--- |\n"
        for r in risks:
            reason_markdown += f"| {r.get('risk_area')} | {r.get('specific_risk')} | {r.get('severity')} | {r.get('applicable_standard')} |\n"
    else:
        reason_markdown += "*No risk categories identified.*"

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
