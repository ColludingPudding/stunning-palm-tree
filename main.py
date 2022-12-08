import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db

from auth import AuthHandler
from schema import AuthDetails

from models import Submission
from models import Submission as ModelSubmission
from schema import Submission as SchemaSubmission

load_dotenv(".env")

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])

auth_handler= AuthHandler()
users=[]

curl http://localhost:8000/register/ {"username":"potato", "password": "admin"}

@app.post("/register/", status_code = 201)
def register(auth_details: AuthDetails):
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code = 400, detail='Username is taken')
    hashed_password = auth_details.get_password_hash(auth_details.password)
    users.append({
        'username': auth_details.username,
        'password': hashed_password
    })
    return

@app.post('/login/')
def login(auth_details: AuthDetails):
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code= 401, detail= "Invalid username and/or password")
    token = auth_handler.encode_token(user["username"])
    return {'token':token}

@app.get("/")
async def root():
    return {"message": "Hello World"}

'''
@app.post("/add-submission/", response_model=SchemaSubmission)
def add_submission(Submission: SchemaSubmission):  
    submission_db = ModelSubmission(hash=Submission.hash, author = Submission.author,
    full_link = Submission.full_link,
    score = Submission.score,
    thumbnail = Submission.thumbnail,
    thumbnail_height = Submission.thumbnail_height,
    thumbnail_width = Submission.thumbnail_width,
    title = Submission.title,
    url = Submission.url)

    db.session.add(submission_db)
    db.session.commit()
    return submission_db
'''
'''
@app.Submission("/bulk-update/")
def bulk_update():
    values = [{'id': 0, 'test_value': 'a'}, {'id': 1, 'test_value': 'b'}]
    insert_stmt = Submissiongresql.insert(MyTable.__table__).values(values)

    update_stmt = insert_stmt.on_conflict_do_update(
    index_elements=[MyTable.id],
    set_=dict(data=values)
    )
'''
'''
@app.get("/Submissions/")
def get_Submissions(username=Depends(auth_handler.auth_wrapper)):
    Submissions = db.session.query(Submission).all()

    return Submissions

'''
# @app.Submission("/user/", response_model=SchemaUser)
# def create_user(user: SchemaUser):
#     db_user = ModelUser(
#         first_name=user.first_name, last_name=user.last_name, age=user.age
#     )
#     db.session.add(db_user)
#     db.session.commit()
#     return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
