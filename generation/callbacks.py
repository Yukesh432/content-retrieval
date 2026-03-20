from langchain_core.callbacks import BaseCallbackHandler
import time

class AgentTelemetryCallback(BaseCallbackHandler):

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        print("LLM START")

    def on_llm_end(self, response, **kwargs):
        latency = time.time() - self.start_time
        print(f"LLM END | latency={latency:.2f}s")

    def on_llm_error(self, error, **kwargs):
        print("LLM ERROR:", error)


class TokenCounterCallback(BaseCallbackHandler):

    def on_llm_end(self, response, **kwargs):
        usage = response.llm_output.get("token_usage")
        print("Token usage:", usage)