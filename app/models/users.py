from pydantic import BaseModel,EmailStr, Field
from typing import Literal

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_number : int
    user_roll: str = Field(..., pattern=r"^\d{2}[A-Z]{3}\d{3}$")    #^:strart , \d:int , {2} : limit , [A-Z]: caps limit in {3} , $:end          
    dept : str
    #year: str = Field(..., pattern=r"^(1st|2nd|3rd|4th) year$")
    year: Literal["1st year", "2nd year", "3rd year", "4th year"]


class User_loginData(BaseModel):
    email : EmailStr
    password : str


class EventRegistration(BaseModel):
    user_id: str
    event_id: str



