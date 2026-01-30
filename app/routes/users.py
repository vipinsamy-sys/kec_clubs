from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.users import UserRegister , User_loginData, EventRegistration
from bson.objectid import ObjectId

router = APIRouter()
db = get_db()



@router.post("/register")
def register_user(user: UserRegister):
    users_collection = db["users"]
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    users_collection.insert_one(user.dict())
    return {
        "message": "User registered successfully"
            }

@router.post("/student-login")
def login_user(user: User_loginData):
    users_collection = db['users']
    print("LOGIN ATTEMPT:", user.email)

    db_user = users_collection.find_one({"email": user.email})
    print("DB USER:", db_user)

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    print("DB PASSWORD:", db_user["password"])
    print("INPUT PASSWORD:", user.password)


    # Compare password
    if db_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Get is_admin field (default to False if not present)
    is_admin = bool(db_user.get("is_admin", False))

    
    return {
        "message": "User logged in successfully",
        "user": {
            "user_id": str(db_user["_id"]),
            "name": db_user["name"],
            "email": db_user["email"],
            
            "is_admin": is_admin
        }
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


from fastapi import HTTPException

@router.post("/register-event")
def register_event(registration: EventRegistration):
    users_collection = db["users"]
    events_collection = db["events"]

    user_id = registration.user_id
    event_id = registration.event_id

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if user_id in event.get("registered_users", []):
        raise HTTPException(status_code=400, detail="Already registered")

    events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$push": {"registered_users": user_id},
            "$inc": {"current_participants": 1}
        }
    )

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"events_participated": event_id}}
    )

    return {"message": "User registered successfully"}

