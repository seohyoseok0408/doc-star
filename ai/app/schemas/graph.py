from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    type: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str | None = None


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
