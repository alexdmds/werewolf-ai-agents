from .system_templates import SYSTEM_PROMPTS

def build_prompt(agent_role, context):
    base = SYSTEM_PROMPTS.get(agent_role, "")
    return f"{base}\nContexte: {context}"
