from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .router_schema import RoutingDecision
from ..prompts import load_prompts
from bookchunker.logging_utils import get_logger

import json


class RouterAgent:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        self.prompts = load_prompts()

        self.logger = get_logger("router.agent")

    def route(self, query, history=None):

        history_text = ""

        if history:

            lines = []

            for msg in history[-6:]:

                role = msg.get("role", "user")
                content = msg.get("content", "")

                lines.append(f"{role}: {content}")

            history_text = "\n".join(lines)

        system_prompt = self.prompts["router"]["system"]

        user_prompt = self.prompts["router"]["user_template"].format(
            history=history_text,
            query=query
        )

        self.logger.info("Router invoked")
        self.logger.info(f"Query: {query}")

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        try:

            decision_json = json.loads(response.content)

        except Exception:

            self.logger.warning("Router JSON parse failed")

            decision_json = {
                "use_book_retrieval": True,
                "use_web_search": False,
                "needs_conversation_context": False,
                "reason": "fallback"
            }

        decision = RoutingDecision(**decision_json)

        self.logger.info(f"Router decision: {decision}")

        return decision