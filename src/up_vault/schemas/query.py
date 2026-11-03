from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=100)


class QuerySource(BaseModel):
    document_id: int
    filename: str
    chunk_index: int


class QueryResponse(BaseModel):
    sources: list[QuerySource]
