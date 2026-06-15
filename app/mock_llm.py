from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .tracing import langfuse_context, observe


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(name="llm_generation", as_type="generation", capture_input=False, capture_output=False)
    def generate(self, prompt: str) -> FakeResponse:
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 5
        docs = prompt.partition("Docs=")[2].partition("\nQuestion=")[0]
        answer = f"Based on the retrieved context: {docs}"
        if "PII" in docs or "logging" in prompt.lower():
            answer += " Sensitive PII must be redacted before logs or traces are stored."
        langfuse_context.update_current_generation(
            model=self.model,
            usage_details={"input": input_tokens, "output": output_tokens},
            metadata={"prompt_chars": len(prompt)},
        )
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)