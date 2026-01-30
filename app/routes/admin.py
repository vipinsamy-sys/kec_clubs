from fastapi import APIRouter, HTTPException
from app.database.database import get_db
from app.models.admin import admin_loginData

router = APIRouter()
db = get_db()


@router.post("/admin-login")
def login_admin(admin: admin_loginData):
    admins_collection = db['admins']
    db_admin = admins_collection.find_one({"email": admin.email})

    if not db_admin:
        raise HTTPException(status_code=400, detail="User not found")

    # Compare password
    if db_admin["password"] != admin.password:
        raise HTTPException(status_code=400, detail="Invalid password")
    
    return {
        "message": "logged in successfully",
        "admin": {
            "name": db_admin["name"],
            "email": db_admin["email"],
            "role": "admin"
        }
    }

