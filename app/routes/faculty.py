from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.faculty import  faculty_loginData
from bson.objectid import ObjectId

router = APIRouter()
db = get_db()

@router.post("/faculty-login")
def login_faculty(faculty:  faculty_loginData):
    fac_collection = db['faculty']
    db_faculty = fac_collection.find_one({"email": faculty.email})

    if not db_faculty:
        raise HTTPException(status_code=400, detail="User not found")

    # Compare password
    if db_faculty["password"] != faculty.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    
    return {
        "message": "logged in successfully",
        "faculty": {
            "name": db_faculty["name"],
            "email": db_faculty["email"],
            "role": "faculty"
        }
    }
    
@router.get("/all_events")
def get_all_events():
    
    events_collection = db["events"]
    all_events = list(events_collection.find({}))
    # Convert ObjectId to string for JSON serialization
    for event in all_events:
        event["_id"] = str(event["_id"])

    return {
        "count": len(all_events),
        "events": all_events
    }

@router.get("/events-dashboard")
def get_upcoming_events():
    events_collection = db["events"]
    upcoming_events = list(events_collection.find({"status": "upcoming"}))
    # Convert ObjectId to string for JSON serialization
    for event in upcoming_events:
        event["_id"] = str(event["_id"])

    return {
        "count": len(upcoming_events),
        "events": upcoming_events
    }
@router.get("/events-past")
def get_past_events():
    events_collection = db["events"]
    past_events = list(events_collection.find({"status": "past"}))
    # Convert ObjectId to string for JSON serialization
    for event in past_events:
        event["_id"] = str(event["_id"])

    return {
        "count": len(past_events),
        "events": past_events
    }

@router.get("/event_participants")
def get_event_participants(event_id: str):
    """
    Get all participants for a specific event using event ObjectId
    """
    events_collection = db["events"]
    users_collection = db["users"]

    # Convert event_id to ObjectId and fetch event
    try:
        event_obj_id = ObjectId(event_id)
        event = events_collection.find_one({"_id": event_obj_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid event ID format")

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get registered user IDs from the event
    registered_user_ids = event.get("registered_users", [])

    if not registered_user_ids:
        return {
            "event_id": event_id,
            "event_title": event.get("title", "Unknown Event"),
            "count": 0,
            "participants": []
        }

    # Convert user IDs to ObjectIds and fetch user details
    try:
        user_obj_ids = [ObjectId(uid) if isinstance(uid, str) else uid for uid in registered_user_ids]
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid user ID in registered_users")

    # Fetch user details
    participants = list(users_collection.find(
        {"_id": {"$in": user_obj_ids}},
        {"_id": 1, "name": 1, "email": 1, "user_roll": 1, "dept": 1, "year": 1}
    ))

    # Convert ObjectId to string
    for participant in participants:
        participant["_id"] = str(participant["_id"])

    return {
        "event_id": event_id,
        "event_title": event.get("title", "Unknown Event"),
        "count": len(participants),
        "participants": participants
    }
    
    