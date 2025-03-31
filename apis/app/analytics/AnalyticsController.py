from fastapi import FastAPI

app = FastAPI()

@app.post("/assign_resource/{task_id}")
def assign_resource(task_id: int):
    return assign_resource_agent(task_id)

@app.get("/detect_bottlenecks/")
def detect_bottlenecks():
    return detect_bottleneck_agent()

@app.post("/reassign_tasks/{resource_id}")
def reassign_tasks(resource_id: int):
    return reassign_tasks_agent(resource_id)
