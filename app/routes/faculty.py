from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.faculty import faculty_loginData, PromotionData, RemoveAdminData


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
    
@router.get("/filter-participants")
def filter_participants(
    club: str = None,
    department: str = None,
    year: str = None,
    month: int = None,
    week: int = None
):
    """Filter participants by club, department, year, month, and week"""
    users_collection = db["users"]
    query = {}

    if club:
        query["club"] = club
    if department:
        query["department"] = department
    if year:
        try:
            query["year"] = int(year)
        except:
            pass
    
    users = list(users_collection.find(query, {"_id": 0, "password": 0}))
    return {
        "count": len(users),
        "students": users
    }

@router.get("/departments")
def get_departments():
    """Get all unique departments from users collection"""
    users_collection = db["users"]
    departments = users_collection.distinct("department")
    return {
        "departments": sorted([d for d in departments if d])
    }

@router.get("/get-students")
def get_all_students():
    """Get all students with their participation details"""
    users_collection = db["users"]
    students = list(users_collection.find({}, {"_id": 1, "name": 1, "email": 1, "studentId": 1, "department": 1, "year": 1, "club": 1}))
    
    # Convert ObjectId to string
    for student in students:
        student["_id"] = str(student["_id"])
    
    return students

@router.get("/event-participants")
def get_event_participants_list(event_id: str):
    """Get all participants for a specific event"""
    from bson.objectid import ObjectId
    events_collection = db["events"]
    users_collection = db["users"]

    # Try finding by _id first, then by event_id
    try:
        event = events_collection.find_one({"_id": ObjectId(event_id)}) or \
                events_collection.find_one({"event_id": event_id})
    except:
        event = events_collection.find_one({"event_id": event_id})

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registered_users = event.get("registered_users", [])
    
    # Get user details for registered users
    participants = list(users_collection.find(
        {"email": {"$in": registered_users}},
        {"_id": 0, "password": 0}
    ))

    return {
        "event_id": event_id,
        "event_title": event.get("title", "Unknown"),
        "count": len(participants),
        "participants": participants
    }

@router.post("/promote-admin")
def promote_student_to_admin(promotion_data: PromotionData):
    """Promote a student to admin for a specific club"""
    from bson.objectid import ObjectId
    
    admin_collection = db["admin"]
    users_collection = db["users"]
    
    student_id = promotion_data.studentId
    student_email = promotion_data.email
    student_name = promotion_data.name
    club_id = promotion_data.clubId
    club_name = promotion_data.clubName
    
    if not all([student_id, student_email, club_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Check if student exists
    try:
        student = users_collection.find_one({"_id": ObjectId(student_id)})
    except:
        student = users_collection.find_one({"email": student_email})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already admin for this club
    existing_admin = admin_collection.find_one({
        "studentId": student_id,
        "clubId": club_id
    })
    
    if existing_admin:
        raise HTTPException(status_code=400, detail="Student is already admin for this club")
    
    # Create admin record
    admin_record = {
        "studentId": student_id,
        "email": student_email,
        "name": student_name,
        "clubId": club_id,
        "clubName": club_name,
        "role": "admin",
        "status": "active"
    }
    
    result = admin_collection.insert_one(admin_record)
    
    return {
        "message": f"{student_name} has been promoted to admin for {club_name}",
        "admin_id": str(result.inserted_id)
    }

@router.get("/get-admins")
def get_all_admins():
    """Get all current admins"""
    admin_collection = db["admin"]
    admins = list(admin_collection.find({}, {"_id": 1, "studentId": 1, "name": 1, "email": 1, "clubId": 1, "clubName": 1, "role": 1, "status": 1}))
    
    # Convert ObjectId to string
    for admin in admins:
        admin["_id"] = str(admin["_id"])
    
    return admins

@router.post("/remove-admin")
def remove_admin(admin_data: RemoveAdminData):
    """Remove admin privileges from a student"""
    from bson.objectid import ObjectId
    
    admin_collection = db["admin"]
    
    student_id = admin_data.studentId
    club_id = admin_data.clubId
    
    if not all([student_id, club_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    result = admin_collection.delete_one({
        "studentId": student_id,
        "clubId": club_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Admin record not found")
    
    return {
        "message": "Admin privileges removed successfully"
    }
