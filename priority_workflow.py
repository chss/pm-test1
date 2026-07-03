from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from pydantic import BaseModel

class ProjectData(BaseModel):
    project_name: str
    problem_solving: str  # Project description
    impact_revenue: str
    impact_cost: str
    impact_cust_service: str
    impact_quality: str

@node(rerun_on_resume=True)
async def determine_and_confirm_priority(ctx: Context, node_input: ProjectData):
    print("--- NODE RUNNING ---")
    print("resume_inputs:", ctx.resume_inputs)
    
    # 1. Check for compliance, quality, or regulatory risk related to patient harm
    desc = node_input.problem_solving.lower()
    
    has_patient_safety_risk = False
    reason = "Standard business impact calculation."
    
    safety_terms = ["patient safety", "patient harm", "harm to patient", "injury to patient", "patient injury", "adverse event"]
    risk_terms = ["compliance", "regulatory", "quality", "risk"]
    
    # Automation logic for high-priority risk
    if any(t in desc for t in safety_terms):
        has_patient_safety_risk = True
        reason = "Automatically qualified as Priority A: Project description indicates direct patient harm or safety risk."
    elif any(r in desc for r in risk_terms[:3]) and any(s in desc for s in ["harm", "safety", "injury"]):
        has_patient_safety_risk = True
        reason = "Automatically qualified as Priority A: Project description indicates compliance, quality, or regulatory risk related to patient harm/safety."
        
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
        # fallback to get generic 'response' or first value if key doesn't match
        if not user_reply and len(reply_data) == 1:
            user_reply = list(reply_data.values())[0]
    else:
        user_reply = str(reply_data)
        
    user_reply = user_reply.strip()
    print("User replied:", user_reply)
    
    final_priority = priority
    # If the user enters a specific override (A, B, C), use it
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
