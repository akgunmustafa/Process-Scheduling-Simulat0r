from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.logic import Process, run_fcfs, run_sjf, run_priority, run_rr
import copy


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/simulate")
async def simulate(
    request: Request,
    file: UploadFile = File(...),
    time_quantum: int = Form(...),
):
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()

    processes = []
    for line in decoded:
        parts = line.strip().split(",")
        if len(parts) == 4:
            processes.append(
                Process(
                    parts[0].strip(),
                    parts[1].strip(),
                    parts[2].strip(),
                    parts[3].strip(),
                )
            )

    results = {
        "FCFS": run_fcfs(copy.deepcopy(processes)),
        "SJF": run_sjf(copy.deepcopy(processes)),
        "Priority": run_priority(copy.deepcopy(processes)),
        "RR": run_rr(copy.deepcopy(processes), time_quantum),
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": results,
            "tq": time_quantum,
        },
    )


