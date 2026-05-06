from pydantic import BaseModel, Field


class ParsedResult(BaseModel):
    representation_type: str
    parser_status: str = "completed"
    schema_snapshot: dict = Field(default_factory=dict)
    data: dict | list | None = None
    preview_data: dict | list | None = None
    extracted_text: str | None = None
    parser_notes: list[str] = Field(default_factory=list)


class CleaningResult(BaseModel):
    cleaning_status: str
    normalized_data: dict | list | None = None
    cleaning_actions: dict = Field(default_factory=dict)
    issues: dict = Field(default_factory=dict)
    skipped_steps: dict = Field(default_factory=dict)


class SummaryTagResult(BaseModel):
    public_summary: str
    processing_summary: str
    cleaning_summary: str
    risk_summary: str | None = None
    public_rag_text: str
    suggested_tags: dict = Field(default_factory=dict)
    llm_output_json: dict | None = None
