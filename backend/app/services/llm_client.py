import json
import logging
import os
from typing import Any, Dict, Optional

from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, provider: str, api_key: str, model: str, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url

        # LiteLLM model format: provider/model (except openai which is just model)
        if self.provider == "openai":
            self.model = model
        elif self.provider == "gemini":
            self.model = f"gemini/{model}"
        elif self.provider == "anthropic":
            self.model = f"anthropic/{model}"
        elif self.provider == "deepseek":
            self.model = f"deepseek/{model}"
        elif self.provider == "ollama":
            self.model = f"ollama/{model}"
        else:
            self.model = f"{self.provider}/{model}"

        # Set provider-specific env vars that LiteLLM expects
        if self.provider == "gemini":
            os.environ["GEMINI_API_KEY"] = api_key
        elif self.provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif self.provider == "openai":
            os.environ["OPENAI_API_KEY"] = api_key
        elif self.provider == "deepseek":
            os.environ["DEEPSEEK_API_KEY"] = api_key

    @retry(
        stop=stop_after_attempt(1),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            # Don't pass base_url for gemini — LiteLLM handles it
            if self.base_url and self.provider not in ("gemini", "anthropic"):
                kwargs["base_url"] = self.base_url

            logger.info(f"Calling LLM: {self.model}")
            response = await acompletion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling LLM {self.model}: {str(e)}")
            raise

    async def complete_json(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        json_instruction = "\n\nIMPORTANT: You must respond ONLY with valid JSON. Do not include any other text, markdown formatting, or code fences."
        prompt_with_json = prompt + json_instruction

        raw_response = await self.complete(prompt_with_json, system_message, temperature, max_tokens)

        # Strip markdown code fences
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {raw_response[:500]}")
            raise ValueError(f"LLM did not return valid JSON: {str(e)}")


def get_llm_client(for_content: bool = False) -> LLMClient:
    """Factory function to get an LLM client from settings."""
    from app.config import settings

    if for_content:
        provider = settings.content_provider
        api_key = settings.content_api_key
        model = settings.content_model
        base_url = settings.content_base_url
    else:
        provider = settings.LLM_PROVIDER
        api_key = settings.LLM_API_KEY
        model = settings.LLM_MODEL
        base_url = settings.LLM_BASE_URL

    return LLMClient(provider=provider, api_key=api_key, model=model, base_url=base_url)
