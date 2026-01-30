from pydantic import BaseModel,EmailStr, Field
from typing import Literal

class faculty_loginData(BaseModel):
    email : EmailStr
    password : str
    
class faculty_data(BaseModel):
    name: str
    email: EmailStr
    password: str
    fac_number : str = Field(..., pattern=r"^[A-Z]{3}\d{3}$")
    dept : str

class PromotionData(BaseModel):
    studentId: str
    email: EmailStr
    name: str
    clubId: str
    clubName: str
    role: str = "admin"

class RemoveAdminData(BaseModel):
    studentId: str
    clubId: str






