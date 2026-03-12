from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time,os
from dotenv import load_dotenv

load_dotenv()
obj = FastAPI()
max_retries = int(os.getenv("MAX_RETRIES", 5))
retry_count = 0
# app = FastAPI() # during running the server uvicorn <pyfile name(here it is main)>:<instance name(here it is obj or app)> --reload(for auto reloading) <port>
# if there is two same function with same HTTP method then first apply one who is write first,after that they don't search

class Post(BaseModel):
    title : str
    content : str
    # id : int
    publish : bool = True # optional one
    # rating: Optional[int] = None # using library 

while retry_count<max_retries:    
    try:
        # conn = psycopg2.connect("dbname=fastapi user=postgres password=sachi")
        conn = psycopg2.connect(host=os.getenv("DATABASE_HOST","localhost"),database=os.getenv("DATABASE_NAME","learning"),user=os.getenv("DATABASE_USER"),password=os.getenv("DATABASE_PASSWORD"),cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database succesfully connected")
        break
    except Exception as error:
        retry_count+=1
        print(f"Connection failed ({retry_count}/{max_retries}): {error}")
        if retry_count < max_retries:
            print("retrying in 2 seconds..")
            time.sleep(2)
        else:
            print("Max retries reached. Exiting...")
            exit(1)
        

my_post = [{
      "title": "title of post 1",
      "content": "content of post 1",
      "id": 1
    },{
      "title": "title of post 2",
      "content": "content of post 1",
      "id": 2
    }]
    
# @app.get("/")
@obj.get("/") # -> path
async def root():
    return {"message":"Hello world"}

# @obj.get("/") # double check but execute first get method here both have same path
# def get_posts():
#     return {"data":"just check"}
@obj.get("/posts")
def get_posts():
    # posts = cursor.execute("""select * from posts """)
    cursor.execute("""select * from posts """)
    posts = cursor.fetchall()
    # print(posts)
    # return {"data":"This is ur posts"}
    # return {"data":my_post}
    return {"data":posts}

# @obj.post("/createposts")
# # req : dict = Body(...) -> ye body ka saara content ko dict convert karke req me store karta hai ,dict ke jagah agar str likha toh input side se bhi stri aana chahiye tabhi koi error nhi aayega
# # async def create_posts(req : dict = Body(...)):
# async def create_posts(new_post: Post): # for input validation we inherit the base model
#     print(new_post.model_dump()) # instead of dict use model_dump()
#     return {"data":new_post}

def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p

def find_index_post(id):
    print(my_post)
    for i,p in enumerate(my_post):
        if p['id'] == id:
            return i
@obj.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_posts(post:Post):
    # cursor.execute(f"insert into posts (title,content,published) values({post.title},{post.content},{post.publish})") -> this way is not good because it is vulnerable to sql injection
    cursor.execute("""insert into posts (title,content,published) values (
        %s,%s,%s) returning *""",(post.title,post.content,post.publish))
    new_post = cursor.fetchone()
    conn.commit()
    # print(post)
    # print(post.model_dump())
    # post_dict = post.model_dump()
    # post_dict["id"] = randrange(1,10000000)
    # my_post.append(post_dict)
    
    return {"data":new_post}


@obj.get("/posts/{id}")
async def get_post(id:int,response:Response):
    # post = find_post((id)) # give {  "post_detail": null} beacuse id is str and in my function i compare int to string
    # post = find_post(int(id))
    cursor.execute("""select * from posts where id = %s""",str(id))
    post = cursor.fetchone()
    # post = find_post(id)
    
    # print(post)
    if not post:
        # response.status_code =  404
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id: {id} was not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} was not found")
        
    return {"post_detail": post}


@obj.get("/posts/latest")
async def get_latest_posts():
    post = my_post[len[my_post]-1]
    return {"post detail": post}


@obj.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int):
    # deleting post
    #  find the index in the array that has required ID
    # my_post.pop(index)
    # index = find_index_post(id)
    # print(index)
    cursor.execute("""delete from posts where id = %s returning *""",str(id))
    deleted_post = cursor.fetchone()
    conn.commit()
    
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"id {id} is not present")
    # my_post.pop(index)
    Response (status_code=status.HTTP_204_NO_CONTENT,content="success")
    
@obj.put("/posts/{id}")
async def update_post(id:int,post:Post):
    # index  = find_index_post(id)
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""",(post.title, post.content, post.publish, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"id {id} is not present")
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_post[index] = post_dict
    return {"message":updated_post}