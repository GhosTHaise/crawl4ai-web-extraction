import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMExtractionStrategy , LLMConfig, DefaultMarkdownGenerator,LLMContentFilter
from pydantic import BaseModel, Field
from crawl4ai import JsonCssExtractionStrategy
import os
class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(..., description="Fee for output token ßfor the OpenAI model.")

ollama_config = LLMConfig(provider="ollama/llama3:latest")
groq_config = LLMConfig(provider="groq/meta-llama/llama-4-scout-17b-16e-instruct",api_token=os.environ["GROQ_API_KEY"])

# if you switch to LLMExtractionStrategy, you don’t need LLMContentFilter anymore.
#filter = LLMContentFilter(
#    llm_config=groq_config,
#    instruction="""
#        From the crawled content, extract all mentioned model names along with their fees for input and output tokens. 
#        Do not miss any models in the entire content. One extracted model JSON format should look like this: 
#        {"model_name": "GPT-4", "input_fee": "US$10.00 / 1M tokens", "output_fee": "US$30.00 / 1M tokens"}.
#    """,
#    chunk_token_threshold=500,
#    verbose=True
#)

extraction = LLMExtractionStrategy(
    llm_config=groq_config,
    schema=OpenAIModelFee.model_json_schema(),  # optional: enforces structure
    instruction="""
        From the crawled content, extract all mentioned model names along with their fees for input and output tokens. 
        Do not miss any models in the entire content. One extracted model JSON format should look like this: 
        {"model_name": "GPT-4", "input_fee": "US$10.00 / 1M tokens", "output_fee": "US$30.00 / 1M tokens"}.
    """,
)

md_generator = DefaultMarkdownGenerator(
    #content_filter=filter,
    options={"ignore_links": True}
)

run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        extraction_strategy=extraction,
        markdown_generator=md_generator
    )

async def main():
    url = "https://openai.com/api/pricing/"
    browser_conf = BrowserConfig(headless=True)  # or False to see the browser

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_conf
        )
        print(result.extracted_content)

if __name__ == "__main__":
    asyncio.run(main())