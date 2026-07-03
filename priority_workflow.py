from google.adk.workflow import Workflow, node
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from pydantic import BaseModel

class ProjectData(BaseModel):
    project_name: str
    impact_revenue: str
    impact_cost: str
    impact_cust_service: str
    impact_quality: str

@node(rerun_on_resume=True)
async def determine_and_confirm_priority(ctx: Context, node_input: ProjectData):
    print("--- NODE RUNNING ---")
    print("resume_inputs:", ctx.resume_inputs)
    
    # 1. Determine base priority based on conditions
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
        print("Yielding RequestInput...")
        yield RequestInput(
            interrupt_id="confirm_priority",
            message=f"calculated_priority:{priority}"
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
