from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional,List
import sqlite3
import hashlib
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
import os

# create api
app=FastAPI()

# 定義可訪問的來源(CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    # 线上环境：你的Railway域名
    "https://endearing-alignment.up.railway.app",
    # 本地开发：常见的前端开发服务器端口
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500", # 一些Live Server的默认端口
    "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 靜態文件服務
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
app.mount("/", StaticFiles(directory="./frontend", html=True), name="frontend")

# initialize "borrow.db"
@app.on_event("startup")
def init_database():
    # 只在數據庫不存在時初始化
    if not os.path.exists("borrow.db"):
        open("borrow.db","w").close()
        with DatabaseConnectCursor("borrow.db") as cur:
            cur.execute("""
                create table types(
                    id integer primary key autoincrement,
                    name text unique,
                    describe text default '',
                    count integer default 0
                );
            """)
            cur.execute("""
                create table items(
                    id integer primary key autoincrement,
                    typeid integer,
                    foreign key(typeid) references types(id)
                );
            """)
        print("數據庫初始化完成")

# 可選：測試用的重置端點
@app.post("/api/reset_db")
def reset_db():
    if os.path.exists("borrow.db"):
        os.remove("borrow.db")
    init_database()
    return {"message":"數據庫已重置為初始狀態"}

# database manager
class DatabaseConnectCursor:
    def __init__(self,name:str):
        self.name=name
        self.conn=None
        self.cur=None
    
    def __enter__(self):
        try:
            self.conn=sqlite3.connect(self.name)
            self.cur=self.conn.cursor()
            return self.cur
        except sqlite3.Error as e:
            print(f"sql error:{e}")
            raise 
    
    def __exit__(self,t,v,tb):
        if self.conn:
            try:
                if t is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except sqlite3.Error as e:
                print(f"commit or rollback error:{e}")
                raise 
            finally:
                if self.cur:
                    self.cur.close()
                self.conn.close()
        return False

# password hashing
def new_hash(s:str)->str:
    return hashlib.sha256(s.encode()).hexdigest()
pw=new_hash("123456")

@app.get("/")
def home():
    return {"message":"the home"}

@app.get("/get_types/")
def get_types():
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select * from types")
        data = cur.fetchall()
        columns_names=["id","name","describe","count"]
        return {
            "message":"get_types successful!",
            "data":[dict(zip(columns_names,l)) for l in data]
        }

@app.get("/get_items/")
def get_items():
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select * from items")
        data = cur.fetchall()
        columns_names=["id","typeid"]
        return {
            "message":"get_items successful!",
            "data":[dict(zip(columns_names,l)) for l in data]
        }

class add_type_input(BaseModel):
    pw:str
    name:str
    describe:Optional[str]
@app.post("/add_type/")
def add_type(t:add_type_input):
    if new_hash(t.pw)!=pw:
        raise HTTPException(status_code=401,detail="wrong password!")
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select id from types where name=?",(t.name,))
        data=cur.fetchall()
        if len(data)==1:
            raise HTTPException(status_code=409,detail=f"type {repr(t.name)} is already exists!")
        cur.execute("insert into types(name,describe) values(?,?)",(t.name,t.describe))
    return {"message": "add_type successful!"}

class add_item_input(BaseModel):
    pw:str
    typename:str
    count:int
@app.post("/add_item/")
def add_item(items:add_item_input):
    if new_hash(items.pw)!=pw:
        raise HTTPException(status_code=401,detail="wrong password!")
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select id from types where name=?",(items.typename,))
        data=cur.fetchall()
        if len(data)!=1:
            raise HTTPException(status_code=404,detail=f"type {repr(items.typename)} is not exists!")
        if items.count<=0:
            raise HTTPException(status_code=400,detail="count must be a positive integer!")
        typeid=data[0][0]
        cur.execute("update types set count=count+? where id=?",(items.count, typeid))
        for i in range(items.count):
            cur.execute("insert into items(typeid) values(?)",(typeid,))
    return {"message":"add_item successful!"}

class delete_type_input(BaseModel):
    pw:str
    name:str
@app.delete("/delete_type/")
def delete_type(t:delete_type_input):
    if new_hash(t.pw)!=pw:
        raise HTTPException(status_code=401,detail="wrong password!")
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select id from types where name=?",(t.name,))
        data=cur.fetchall()
        if len(data)!=1:
            raise HTTPException(status_code=404,detail=f"type {repr(t.name)} is not exists!")
        typeid=data[0][0]
        cur.execute("delete from items where id in(select id from items where typeid=?)",(typeid,))
        cur.execute("delete from types where id =?",(typeid,))
    return {"message":"delete_type successful!"}

class delete_item_input(BaseModel):
    pw:str
    typename:str
    count:int
@app.delete("/delete_item/")
def delete_item(items:delete_item_input):
    if new_hash(items.pw)!=pw:
        raise HTTPException(status_code=401,detail="wrong password!")
    with DatabaseConnectCursor("borrow.db") as cur:
        cur.execute("select id,count from types where name=?",(items.typename,))
        data=cur.fetchall()
        if len(data)!=1:
            raise HTTPException(status_code=404,detail=f"type {repr(items.typename)} is not exists!")
        if items.count<=0:
            raise HTTPException(status_code=400,detail="count must be a positive integer!")
        typeid,typecount=data[0]
        if typecount<items.count:
            raise HTTPException(status_code=400,detail="delete count is bigger than count!")
        cur.execute("update types set count=count-? where id=?",(items.count,typeid))
        cur.execute("delete from items where id in(select id from items where typeid=? limit ?)",(typeid,items.count))
    return {"message":"delete_item successful!"}


