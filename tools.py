# tools.py
import os
import asyncio
from pydantic import BaseModel, Field
from praisonai_tools import BaseTool

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMExtractionStrategy,
    LLMConfig,
    DefaultMarkdownGenerator,
)


# Define schema for model fees
class ModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the model.")
    input_fee: str = Field(..., description="Fee for input tokens.")
    output_fee: str = Field(..., description="Fee for output tokens.")


class ModelFeeTool(BaseTool):
    name: str = "ModelFeeTool"
    description: str = "Extracts model fees for input and output tokens from the given pricing page."

    async def _arun(self, url: str):
        # Define the LLM config (Groq or OpenAI etc.)
        llm_config = LLMConfig(
            provider="groq/meta-llama/llama-4-scout-17b-16e-instruct",
            api_token=os.environ["GROQ_API_KEY"],
        )

        extraction = LLMExtractionStrategy(
            llm_config=llm_config,
            schema=ModelFee.model_json_schema(),  # ensures correct structure
            instruction="""
                From the crawled content, extract all mentioned model names along with their fees for input and output tokens. 
                Do not miss any models in the entire content. One extracted model JSON format should look like this: 
                {"model_name": "GPT-4", "input_fee": "US$10.00 / 1M tokens", "output_fee": "US$30.00 / 1M tokens"}.
            """,
        )

        md_generator = DefaultMarkdownGenerator(
            options={"ignore_links": True}
        )

        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=1,
            extraction_strategy=extraction,
            markdown_generator=md_generator,
        )

        browser_conf = BrowserConfig(headless=True)

        async with AsyncWebCrawler(config=browser_conf) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_conf
            )
            return result.extracted_content

    def _run(self, url: str):
        return asyncio.run(self._arun(url))


if __name__ == "__main__":
    tool = ModelFeeTool()
    url = "https://openai.com/api/pricing/"
    result = tool.run(url)
    print(result)
