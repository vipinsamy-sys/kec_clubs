from pydantic import BaseModel,EmailStr, Field
from typing import Literal


class admin_loginData(BaseModel):
    email : EmailStr
    password : str

class admin_data(BaseModel):
    name: str
    email: EmailStr
    password: str
    admin_number : int
    admin_roll: str = Field(..., pattern=r"^\d{2}[A-Z]{3}\d{3}$")    #^:strart , \d:int , {2} : limit , [A-Z]: caps limit in {3} , $:end          
    dept : str
    #year: str = Field(..., pattern=r"^(1st|2nd|3rd|4th) year$")
    year: Literal["1st year", "2nd year", "3rd year", "4th year"]



