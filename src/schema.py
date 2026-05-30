import uuid
from typing import Optional
from pydantic import BaseModel, Field

class ChunkMetadata(BaseModel):
    source_file: str
    chunk_index: int
    header_context: Optional[str] = None
    strategy_used: str
    related_image_path: Optional[str] = None
    has_table: bool = False

class SemanticChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    token_count: int
    metadata: ChunkMetadata
