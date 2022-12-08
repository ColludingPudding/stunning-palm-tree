from pydantic import BaseModel

class AuthDetails(BaseModel):
    username: str
    password: str
    
class Submission(BaseModel):
    hash: str
    author: str
    full_link: str
    score: int
    thumbnail: str
    thumbnail_height: int
    thumbnail_width: int
    title: str	
    url: str

    class Config:
        orm_mode = True
