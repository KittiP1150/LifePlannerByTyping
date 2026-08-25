import os

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.db.database import engine, Base, get_db
from app.db.models import TaskDB, LocationDB
from app.task_schema import ChatRequest, PlannerResponse, DailyTask, DailyLocation
from app.llm_service import generate_plan_from_text

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Plan API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/plan", response_model=PlannerResponse)
def get_plan_by_date(target_date: str, db: Session = Depends(get_db)):
    year_month = target_date[:7]
    db_tasks = db.query(TaskDB).filter(TaskDB.date == target_date).all() 
    db_locations = db.query(LocationDB).filter(LocationDB.date.like(f"{year_month}%")).all()
    
    tasks_list = [
        DailyTask(
            date=t.date,
            title=t.title,
            start_time=t.start_time,
            end_time=t.end_time,
            category=t.category,
            priority=t.priority
        ) for t in db_tasks
    ]
    
    locations_list = [
        DailyLocation(date=loc.date, city=loc.city) for loc in db_locations
    ]
    
    return PlannerResponse(
        reply_message="", 
        tasks=tasks_list, 
        locations=locations_list
    )

@app.post("/api/v1/plan", response_model=PlannerResponse)
async def create_plan(request: ChatRequest, db: Session = Depends(get_db), x_api_key: str = Header(None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API Key. Please provide a valid GROQ API Key.")
    
    try:
        db_tasks = db.query(TaskDB).all()
        db_locations = db.query(LocationDB).all()
        
        current_tasks = [
            {
                "title": t.title,
                "date": t.date,
                "start_time": t.start_time,
                "end_time": t.end_time,
                "category": t.category,
                "priority": t.priority
            }
            for t in db_tasks
        ]
        current_locations = [{"date": l.date, "city": l.city} for l in db_locations]
        
        ai_response = generate_plan_from_text(request.user_message, x_api_key, current_tasks, current_locations, request.target_date)
    
        new_tasks = ai_response.get("tasks", [])
        new_locations = ai_response.get("locations", [])
        deleted_tasks = ai_response.get("deleted_tasks", [])
        deleted_locations = ai_response.get("deleted_locations") or []
        reply_msg = ai_response.get("reply_message", "already done!!")
        
        for dt in deleted_tasks:
            del_title = dt.get("title")
            del_date = dt.get("date") or request.target_date
            if del_title:
                db.query(TaskDB).filter(
                    TaskDB.title == del_title, 
                    TaskDB.date == del_date
                ).delete()
        
        for dl in deleted_locations:
            del_city = dl.get("city")
            del_loc_date = dl.get("date") or request.target_date
            if del_city:
                db.query(LocationDB).filter(
                    LocationDB.city == del_city, 
                    LocationDB.date == del_loc_date
                ).delete()
        
        for t in new_tasks:
            task_date = t.get("date") or request.target_date 
            new_row = TaskDB(
                title=t.get("title", "Untitled"),
                date=task_date,
                start_time=t.get("start_time"),
                end_time=t.get("end_time"),
                category=t.get("category", "Work"),
                priority=t.get("priority", "Medium")
            )
            db.add(new_row)

        for l in new_locations:
            loc_date = l.get("date") or request.target_date
            new_loc = LocationDB(date=loc_date, city=l.get("city", "Bangkok"))
            db.add(new_loc)
            
        db.commit()
        
        year_month = request.target_date[:7]
        updated_tasks = db.query(TaskDB).filter(TaskDB.date == request.target_date).all()
        updated_locations = db.query(LocationDB).filter(LocationDB.date.like(f"{year_month}%")).all()
        tasks_list = [
            DailyTask(
                date=t.date, title=t.title, start_time=t.start_time, 
                end_time=t.end_time, category=t.category, priority=t.priority
            ) for t in updated_tasks
        ]
        
        locations_list = [
            DailyLocation(date=loc.date, city=loc.city) 
            for loc in updated_locations
        ]
        
        return PlannerResponse(reply_message=reply_msg, tasks=tasks_list, locations=locations_list)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Processing Error: {str(e)}")
    
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

    @app.get("/{catchall:path}")
    def serve_react_app(catchall: str):
        file_path = os.path.join("dist", catchall)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("dist/index.html")