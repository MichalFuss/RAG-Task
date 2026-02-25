from pydantic import BaseModel, Field
from typing import List, Optional
from llama_index.core.workflow import Event

# הגדרת האירועים שחסרו לך
class ExtractionEvent(Event):
    nodes: list
    query: str

class ChatEvent(Event):
    nodes: list
    query: str


# מקור הפריט (קובץ וסעיף)
class Source(BaseModel):
    file: str = Field(description="Path or name of the source file")
    anchor: Optional[str] = Field(default=None, description="Section anchor, e.g. #db or ## UI Rules")


# מבנה הנתונים לחילוץ (שלב ג') - תואם דרישות הפרויקט
class TechnicalPoint(BaseModel):
    id: str = Field(description="Unique ID e.g. dec-001, rule-001, warn-001")
    category: str = Field(
        description="Must be exactly one of: 'decisions', 'rules', or 'warnings'"
    )
    title: str = Field(description="Short title for the point")
    content: str = Field(description="Summary or description of the point")
    priority: str = Field(description="High, Medium, or Low")
    source: Source = Field(description="Source file and section (anchor) from the nodes")
    observed_at: str = Field(
        description="ISO format timestamp, e.g. 2026-02-18T00:00:00+02:00"
    )


class ProjectInsights(BaseModel):
    items: List[TechnicalPoint]
