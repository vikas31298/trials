import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Callable, Any, Dict
import utils.retrievers as r
import asyncio
import inspect 

class Tag(BaseModel):
    id: str
    title: str
    source: Optional[str] = ""
    variations: Optional[Union[List[dict], str]] = Field(default_factory=list)


class Page(BaseModel):
    page_number: int = Field(..., alias="pageNumber")
    tags: List[Tag]

    class Config:
        populate_by_name = True


class DocumentSchema(BaseModel):
    pages: List[Page]


class ProjectDataRetriever(BaseModel):
    project_id: str
    client: str
    pricing_model: str
    project_name: str
    project_description: str
    project_status: str
    project_start_date: str
    project_end_date: str
    project_manager: str
    project_team: str
    project_budget: float
    project_revenue: float
    project_change_mom_revenue: float
    
    # Fix: Properly type this with TypedDict or similar in a real application
    retrieval_functions: Dict[str, Dict[str, Any]]
    
    document_schema: DocumentSchema
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)

    class Config:
        arbitrary_types_allowed = True

    async def populate_tag(self, page: Page, tag: Tag):
        async with self.lock:
            if tag.id in self.retrieval_functions:
                func_or_lambda = self.retrieval_functions[tag.id]["retriever"]
                multiple_values = self.retrieval_functions[tag.id]["multiple_values"]

                print(f"Executing tag {tag.id} on page {page.page_number}")

                async def execute_once():
                    if callable(func_or_lambda):
                        result = func_or_lambda(self)
                        return await result if inspect.iscoroutine(result) else result
                    func, args = func_or_lambda
                    evaluated_args = [arg(self) if callable(arg) else arg for arg in args]
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*evaluated_args)
                    else:
                        result = func(*evaluated_args)
                    return str(result) if not isinstance(result, (list, dict)) else result

                try:
                    if multiple_values:
                        variations = await execute_once()
                    else:
                        variations = [await execute_once()]
                    tag.variations = [{"id": i, "text": variation} for i, variation in enumerate(variations)]
                except Exception as e:
                    tag.variations = [{"id": 0, "text": f"Error: {str(e)}"}]
            else:
                tag.variations = [{"id": 0, "text": "Tag executor not found"}]

    async def get_document_data(self):
        async with self.lock:
            return self.document_schema.model_dump(by_alias=True)

