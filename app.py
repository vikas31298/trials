from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
import inspect
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Callable, Any, Dict

from utils.project_report import project_report_schema, project_report_retrievers
from utils.sales_report import sales_report_schema, sales_report_retrievers
from utils.projectmodels import ProjectDataRetriever, DocumentSchema, Page, Tag

app = FastAPI()


async def project_report_generator(id: str):
    print("Generating project report for id:", id)

    data_retriever = ProjectDataRetriever(
        project_id=id,
        year=2025,
        project_name="Project Alpha",
        client="Client Meta",
        pricing_model="Fixed Price",
        project_description="This is a project description",
        project_status="In Progress",
        project_start_date="2024-01-01",
        project_end_date="2024-12-31",
        project_manager="John Doe",
        project_team="Team A",
        project_budget=100000,
        project_revenue=100000,
        project_change_mom_revenue=0.1,
        retrieval_functions=project_report_retrievers,
        document_schema=project_report_schema.model_dump(),
    )

    total_pages = len(data_retriever.document_schema.pages)
    total_tags = sum(len(page.tags) for page in data_retriever.document_schema.pages)
    tags_processed = 0

    yield f"event: init\ndata: {json.dumps({'total_pages': total_pages})}\n\n"

    progress_queue = asyncio.Queue()

    async def process_page(page_index, page: Page):
        nonlocal tags_processed
        for tag_index, tag in enumerate(page.tags):
            try:
                await data_retriever.populate_tag(page, tag)
                tags_processed += 1
                progress = {
                    "page": page_index + 1,
                    "total_pages": total_pages,
                    "tag": tag_index + 1,
                    "total_tags": len(page.tags),
                    "tagId": tag.id,
                    "overall_progress": tags_processed / total_tags
                }
                await progress_queue.put(progress)
            except Exception as e:
                await progress_queue.put({
                    "page": page_index + 1,
                    "tagId": tag.id,
                    "error": str(e),
                    "type": "error"
                })

    tasks = [asyncio.create_task(process_page(i, page)) for i, page in enumerate(data_retriever.document_schema.pages)]

    async def progress_reporter():
        while any(not task.done() for task in tasks) or not progress_queue.empty():
            try:
                progress_event = await asyncio.wait_for(progress_queue.get(), timeout=1.0)
                yield f"event: progress\ndata: {json.dumps(progress_event)}\n\n"
            except asyncio.TimeoutError:
                continue

    async for progress_event in progress_reporter():
        yield progress_event

    await asyncio.gather(*tasks)

    done_data = await data_retriever.get_document_data()
    yield f"event: done\ndata: {json.dumps(done_data)}\n\n"


@app.get("/retrieval")
async def project_report_extraction():
    id = "7"
    return StreamingResponse(project_report_generator(id), media_type="text/event-stream")