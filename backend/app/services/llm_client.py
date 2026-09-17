import json
import logging
import re
from typing import Any, Dict, Optional

from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, provider: str, api_key: str, model: str, base_url: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        
        if provider.lower() == "openai":
            self.model = model
        else:
            self.model = f"{provider.lower()}/{model}"

    @retry(
        stop=stop_after_attempt(3),
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
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "api_key": self.api_key,
            }
            if self.base_url:
                kwargs["base_url"] = self.base_url

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
        json_instruction = "\n\nIMPORTANT: You must respond ONLY with valid JSON. Do not include any other text."
        prompt_with_json = prompt + json_instruction
        
        raw_response = await self.complete(prompt_with_json, system_message, temperature, max_tokens)
        
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
            
        try:
            return json.loads(cleaned_response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {raw_response}")
            raise ValueError(f"LLM did not return valid JSON: {str(e)}")


def get_llm_client(for_content: bool = False) -> LLMClient:
    """Factory function to get an LLM client from settings."""
    import os
    if for_content:
        provider = os.getenv("CONTENT_LLM_PROVIDER", "openai")
        api_key = os.getenv("CONTENT_LLM_API_KEY", "dummy")
        model = os.getenv("CONTENT_LLM_MODEL", "gpt-4o")
        base_url = os.getenv("CONTENT_LLM_BASE_URL")
    else:
        provider = os.getenv("LLM_PROVIDER", "openai")
        api_key = os.getenv("LLM_API_KEY", "dummy")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        base_url = os.getenv("LLM_BASE_URL")
        
    return LLMClient(provider=provider, api_key=api_key, model=model, base_url=base_url)
