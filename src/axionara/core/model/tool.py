from pydantic import BaseModel


class AgentToolInfo(BaseModel):
    name: str = ""
    invocation_message: str = ""
