from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import json

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
    
    # Enforce Gemini API Key requirement for mandatory semantic evaluation
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required for Priority Agent semantic analysis. Please configure your Gemini API Key in the sidebar settings.")
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are a regulatory affairs and quality assurance agent representing a medical device manufacturer subject to FDA 21 CFR Part 820 Quality System Regulations.
        Your task is to analyze the following business case inputs to determine the recommended priority of the project (Priority A, B, or C) and conduct a compliance risk assessment.

        PROJECT DATA INPUTS:
        {combined_text}

        USER'S SELECTED BUSINESS IMPACTS (RADIO BUTTONS):
        - Revenue Influence: "{node_input.impact_revenue}"
        - Cost Reduction: "{node_input.impact_cost}"
        - Customer Experience: "{node_input.impact_cust_service}"
        - Quality: "{node_input.impact_quality}"

        EVALUATION INSTRUCTIONS:
        1. Evaluate the project text details against these 5 High-Risk Categories:
           - Intended Use & Classification: Life-sustaining, implantable, or automated therapeutic decision-making (High risk).
           - Software & AI (SaMD/SiMD): Software code, AI/ML models, cloud connectivity, cybersecurity vulnerabilities (Medium risk).
           - Materials & Biocompatibility: Body contact, sterilization needs, novel materials (Medium risk).
           - Clinical Data & Human Factors: Complex clinical trials, usability/human error risks (Medium risk).
           - Design & Manufacturing Complexity: 3D printing, complex supply chains, critical single-point failure components (Medium risk).
           - Also flag any direct patient safety risk or patient harm indications (High risk).
           Recommend a risk priority level (High risk -> Priority A, Medium risk -> Priority B, Low/No risk -> Priority C).

        2. Perform a semantic sanity check of the text details against the user's radio button selections:
           - Does the text suggest the project targets Product Quality (product revisions, quality QA, compliance)? If yes and Quality radio is NOT 'Product', flag this discrepancy.
           - Does the text suggest the project targets Revenue Increase (sales, revenue generation, market share)? If yes and Revenue radio is NOT 'Increase', flag this discrepancy.
           - Does the text suggest the project targets Cost Saving (cost reduction, efficiency savings)? If yes and Cost radio is NOT 'Saving', flag this discrepancy.
           - Does the text suggest the project targets External Customer Experience (customer/patient satisfaction, NPS, customer support)? If yes and Customer Experience radio is NOT 'External', flag this discrepancy.
           If any text target is detected, recommend its corresponding priority:
           - Product Quality, Revenue Increase, or Cost Saving -> Priority A
           - External Customer Experience -> Priority B

        3. Calculate the final recommended priority (A > B > C) taking the highest of:
           - The risk-based priority (High -> A, Medium -> B, Low -> C)
           - The user's actual radio buttons priority (Quality=Product/Revenue=Increase/Cost=Saving -> A; Customer Experience=External -> B; else C)
           - The text-detected priority (Quality/Revenue/Cost detected -> A; External Customer Experience detected -> B; else C)

        Format your output strictly as a JSON object with:
        1. "calculated_priority": "A" | "B" | "C"
        2. "max_severity": "High" | "Medium" | "Low"
        3. "risk_summary": A 2-3 sentence overview of compliance or quality gaps found in the text.
        4. "risks": A list of objects containing:
           - "risk_area": The category name (e.g. Intended Use & Classification, Software & AI (SaMD/SiMD), Materials & Biocompatibility, Clinical Data & Human Factors, Design & Manufacturing Complexity, Product Compliance & Quality (Patient Safety))
           - "specific_risk": Specific risk description referencing details from the text.
           - "severity": "High" | "Medium" | "Low"
           - "applicable_standard": Relevant standards and FDA regulations (e.g. ISO 14971, IEC 62304 / 21 CFR 820.30, ISO 10993, IEC 62366, ISO 13485 / 21 CFR 820.70 / 21 CFR 820.75, 21 CFR 820.100)
        5. "discrepancies": A list of strings listing any mismatch warnings found (e.g. "Text mentions product validation, but Quality Assurance radio button was set to 'No impact'.").
        6. "discrepancy_explanation": A 1-2 sentence semantic justification of the discrepancy.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        res_data = json.loads(response.text)
        final_calculated_priority = res_data.get("calculated_priority", "C")
        max_severity = res_data.get("max_severity", "Low")
        risk_summary = res_data.get("risk_summary", "No high-risk compliance or quality issues were identified.")
        risks = res_data.get("risks", [])
        discrepancies = res_data.get("discrepancies", [])
        discrepancy_explanation = res_data.get("discrepancy_explanation", "")
    except Exception as e:
        # Fall back to throwing error to frontend so user knows LLM call failed
        raise RuntimeError(f"Gemini semantic analysis call failed: {str(e)}")

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
    if discrepancies:
        reason_markdown += "\n### 3. Business Impact Discrepancy Check\n"
        reason_markdown += "⚠️ **Sanity Check Warning**: The Priority Agent detected a mismatch between your text details and radio selections:\n"
        for d in discrepancies:
            reason_markdown += f"- {d}\n"
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
