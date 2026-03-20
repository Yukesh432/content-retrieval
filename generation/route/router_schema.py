from pydantic import BaseModel


class RoutingDecision(BaseModel):

    use_book_retrieval: bool
    use_web_search: bool
    needs_conversation_context: bool
    reason: str