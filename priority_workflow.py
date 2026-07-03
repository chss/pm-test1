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
    print("resume_inputs:", ctx.resume_inputs)
    
    # 1. Combine all field information to check "any field information"
    combined_text = " ".join([
        node_input.project_name,
        node_input.problem_solving,
        node_input.who_impacted,
        node_input.cost_impact,
        node_input.other_details,
        node_input.value_creation,
        node_input.kpis_json
    ]).lower()
    
    has_patient_safety_risk = False
    reason = "Standard business impact calculation."
    
    # Keyword Rule Check
    safety_terms = ["patient safety", "patient harm", "harm to patient", "injury to patient", "patient injury", "adverse event", "patient risk", "clinical risk", "medical risk", "patient impact", "harming patients"]
    quality_compliance_terms = ["compliance", "regulatory", "quality issue", "defect", "recall", "deviation", "audit finding", "non-conformance", "fda", "capa", "regulatory risk", "compliance issue", "quality risk"]
    
    keyword_match = False
    matched_safety = [t for t in safety_terms if t in combined_text]
    matched_risk = [t for t in quality_compliance_terms if t in combined_text]
    
    if matched_safety:
        keyword_match = True
        matched_str = ", ".join(matched_safety)
        reason = f"Automatically qualified as Priority A (Keyword Match): Found direct patient safety/harm risk keywords: '{matched_str}'."
    elif matched_risk and any(s in combined_text for s in ["harm", "safety", "injury", "risk", "hazard"]):
        keyword_match = True
        matched_str = ", ".join(matched_risk)
        reason = f"Automatically qualified as Priority A (Keyword Match): Found quality/compliance risk keywords related to patient harm: '{matched_str}'."
        
    # Semantic AI Analysis Check
    api_key = os.getenv("GEMINI_API_KEY")
    if not keyword_match and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Analyze the following text from a business case intake form. Determine if the text suggests, even remotely, any product compliance, quality issues, defects, deviations, or regulatory risks that could lead to patient harm, patient safety issues, or adverse patient events.
            
            Text:
            {combined_text}
            
            Respond in JSON format with two fields:
            1. "is_risk": boolean (true if it suggests a product compliance/quality issue leading to patient harm, false otherwise).
            2. "explanation": string (a clear, detailed explanation of why you classified it this way, mentioning specific phrases from the text that indicate the risk, or explaining why it does not pose a risk).
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            res_data = json.loads(response.text)
            if res_data.get("is_risk"):
                has_patient_safety_risk = True
                reason = f"Automatically qualified as Priority A (AI Semantic Analysis): {res_data.get('explanation')}"
        except Exception as e:
            print("Gemini semantic analysis failed, relying on keyword rules:", e)
            
    if keyword_match:
        has_patient_safety_risk = True
        
    if has_patient_safety_risk:
        priority = "A"
    else:
        # Standard rules
        rev = node_input.impact_revenue
        cost = node_input.impact_cost
        cust = node_input.impact_cust_service
        qual = node_input.impact_quality
        
        priority = "C"
        if rev == "Increase" and cost == "Saving":
            priority = "A"
        elif cust == "External" or qual == "Product":
            priority = "B"
            
    # 2. Check if we have received a response to our RequestInput
    if not ctx.resume_inputs or "confirm_priority" not in ctx.resume_inputs:
        print("Yielding RequestInput with calculated priority and reason...")
        yield RequestInput(
            interrupt_id="confirm_priority",
            message=f"calculated_priority:{priority}:{reason}"
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
    
    final_priority = priority
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
