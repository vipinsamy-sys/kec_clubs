from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database.database import get_db
import json
from bson import ObjectId


router = APIRouter()
db = get_db()

class ObjectIdEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

@router.get("/all_clubs")
def get_all_clubs():
    clubs_collection = db["clubs"]
    
    clubs = list(clubs_collection.find({}, {"_id": 0}))  # exclude ObjectId
    
    return {
        "count": len(clubs),
        "clubs": clubs
    }





