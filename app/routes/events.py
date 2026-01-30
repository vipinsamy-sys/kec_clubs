from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.events import CreateEvent
from pymongo.errors import PyMongoError
from datetime import date, time


router = APIRouter()
db = get_db()

@router.post("/create-event")
def create_event(event: CreateEvent):
    events_collection = db["events"]

    event_data = event.dict()

    result = events_collection.insert_one(event_data)

    event_id = str(result.inserted_id)

    events_collection.update_one(
        {"_id": result.inserted_id},
        {"$set": {"event_id": event_id}}
    )
    return {
        "message": "Event created successfully",
        "event_id": event_id
    }



@router.get("/all_events")
def all_events():
    events = list(db["events"].find())
    for event in events:
        event["_id"] = str(event["_id"])
    return events
        

