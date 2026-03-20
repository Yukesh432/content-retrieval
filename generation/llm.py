from __future__ import annotations

import base64
from typing import Optional, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import AIMessage
from langchain_core.callbacks import CallbackManager
from bookchunker.generation.callbacks import AgentTelemetryCallback
from bookchunker.logging_utils import get_logger, log_event

from .prompts import load_prompts
from .route.routing import (
    needs_context,
    should_web_search,
    classify_style_chat,
    classify_style_notes,
)
from .tools.web_search import WebSearchClient

load_dotenv()


class VisualizationAgent:
    def __init__(self, model: str = "gpt-5.1", temperature: float = 0.3, enable_web_search: bool = False):
        # self.llm = ChatOpenAI(model=model, temperature=temperature)
        callback_manager = CallbackManager([AgentTelemetryCallback()])

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            callbacks=callback_manager
        )
        self.prompts = load_prompts()

        self.enable_web_search = enable_web_search
        self.web = WebSearchClient(max_results=5) if enable_web_search else None

        self.logger = get_logger("bookchunker.agent")

    # -----------------------------
    # Chat
    # -----------------------------
    def run(
        self,
        user_query: str,
        # retrieved_content: Optional[str] = None,
        retrieved_chunks: Optional[List[dict]] = None,
        selected_notes: Optional[List[str]] = None,
        conversation_history: Optional[List[str]] = None,
        book_id: Optional[str] = None,
        force_context: bool = False,
        force_web_search: bool = False,
    ) -> str:
        system_prompt = self.prompts["chat"]["system"]

        # used_book = bool(retrieved_content and retrieved_content.strip())
        used_book = bool(retrieved_chunks)
        used_notes = bool(selected_notes)
        used_web = False

        context_parts: List[str] = []

        if selected_notes:
            context_parts.append("Selected Study Notes:\n" + "\n\n".join(selected_notes))

        if retrieved_chunks:
            used_book = True

            formatted_chunks = []

            for chunk in retrieved_chunks:
                formatted_chunks.append(
                    f"[Book: {chunk.get('book_id')} | Score: {chunk.get('score'):.4f}]\n"
                    f"{chunk.get('text')}"
                )

            joined = "\n\n---\n\n".join(formatted_chunks)

            context_parts.append(
                "Retrieved Textbook Chunks:\n" + joined[:6000]
            )

        if should_web_search(
            enable_web_search=self.enable_web_search,
            user_query=user_query,
            retrieved_chunks=retrieved_chunks,
            force_web_search=force_web_search,
        ):
            web_ctx = self.web.search_compact(user_query, max_chars=6000) if self.web else ""
            if web_ctx:
                context_parts.append(web_ctx)

        if conversation_history:

            history_text = []

            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                history_text.append(f"{role.capitalize()}: {content}")

            context_parts.append("Conversation History:\n" + "\n".join(history_text))
        if context_parts and (force_context or needs_context(user_query)):
            context_block = "\n\n".join(context_parts)
            user_prompt = self.prompts["chat"]["contextual_user"].format(
                context_block=context_block,
                user_query=user_query,
            )
        else:
            user_prompt = self.prompts["chat"]["general_user"].format(user_query=user_query)

        style = classify_style_chat(used_book=used_book, used_notes=used_notes, used_web=used_web)

        log_event(self.logger, "generation.route", {
            "mode": "chat",
            "style": style,
            "used_book": used_book,
            "used_notes": used_notes,
            "used_web": used_web,
            "book_id": book_id,
        })

        # messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        messages = [SystemMessage(content=system_prompt)]

        # inject conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # last 3 exchanges
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # current user query
        messages.append(HumanMessage(content=user_prompt))
        response = self.llm.invoke(messages)
        return response.content

    # -----------------------------
    # Notes (multimodal)
    # -----------------------------
    def generate_notes(
        self,
        topic: str,
        unit: str,
        text_context: str,
        image_paths: Optional[List[str]] = None,
        book_id: Optional[str] = None,
        force_web_search: bool = True,
    ) -> str:
        system_prompt = self.prompts["notes"]["system"]

        used_book = bool(text_context and text_context.strip())
        used_web = True

        web_ctx = ""
        if self.enable_web_search and force_web_search and self.web:
            used_web = True
            web_ctx = self.web.search_compact(f"{topic} ({unit})", max_chars=5000)

        # Important: append web_ctx to context so prompt can compile
        combined_context = (text_context[:6000] + ("\n\n" + web_ctx if web_ctx else "")).strip()

        style = classify_style_notes(used_book=used_book, used_web=used_web)

        log_event(self.logger, "generation.route", {
            "mode": "notes",
            "style": style,
            "topic": topic,
            "unit": unit,
            "book_id": book_id,
            "used_book": used_book,
            "used_web": used_web,
            "image_count": len(image_paths or []),
        })

        user_text = self.prompts["notes"]["user_template"].format(
            book_id=book_id or "Unknown",
            unit=unit,
            topic=topic,
            text_context=combined_context,
        )

        content_parts = [{"type": "text", "text": user_text}]

        if image_paths:
            for path in image_paths[:3]:
                try:
                    with open(path, "rb") as f:
                        encoded = base64.b64encode(f.read()).decode("utf-8")
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded}"}
                    })
                except Exception:
                    continue

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=content_parts)]
        response = self.llm.invoke(messages)
        return response.content