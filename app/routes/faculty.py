from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.faculty import  faculty_loginData

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
    events_collection = db["events"]
    users_collection = db["users"]

    event = events_collection.find_one({"event_id": event_id}, {"_id": 0})

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registered_users = event.get("registered_users", [])

    participants = list(events_collection.find(
        {"email": {"$in": registered_users}},
        {"_id": 0, "password": 0} 
    ))

    return {
        "event_id": event_id,
        "count": len(participants),
        "participants": participants
    }
    

@router.post("/manage_admins")
def manage_admins(action: str, email: str):
    fac_collection = db['faculty']
    user = fac_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    if action == "promote":
        fac_collection.update_one({"email": email}, {"$set": {"role": "admin"}})
        return {"message": f"{email} has been promoted to admin."}
    elif action == "demote":
        fac_collection.update_one({"email": email}, {"$set": {"role": "faculty"}})
        return {"message": f"{email} has been demoted to faculty."}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'promote' or 'demote'.")