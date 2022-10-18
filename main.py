from pydantic import BaseModel
from fastapi import FastAPI, Request,Form
from fastapi.responses import HTMLResponse
from re import template
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from mongoengine import Document, StringField
import pymongo
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

base_dir = Path(__file__).resolve().parent
#mongo db connection
# client = pymongo.MongoClient("mongodb://localhost:27017")
# mongo atlas connection
client = pymongo.MongoClient(os.getenv("mongouri"))
# Database
user = client['data']
#Fast api Initialize
app = FastAPI()

#Static file serv
app.mount("/static", StaticFiles(directory=str(Path(base_dir,"static"))), name="static")

#Jinja2 Template directory
templates = Jinja2Templates(directory=str(Path(base_dir,"templates")))

# Collection
user_collection = user['user_login']
#  base Model for login
class User(BaseModel):
    user_name: str
    user_email : str
    user_password : str

# login page rendering
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html" ,{"request": request})
#login POST
@app.post('/', response_class=HTMLResponse)
async def login(request: Request, User_Email:str=Form(...),User_Password:str=Form(...)):#, cpatchaTextBox:str=Form(...)):
    email = User_Email
    password = User_Password
    user_collection = user['user_login']
    data = user_collection.find_one({"user_email": email })
    print(email)
    print(password)
    if not data:            
        print("no records")
        return templates.TemplateResponse('mail.html', {'message':"invalid email",'request':request})        
    else:
        print(data['user_password'])
        if data['user_password']==password: 
            return templates.TemplateResponse('dashboard.html', {'request':request,'user':user})
        else:
            return templates.TemplateResponse('invalid.html',{'message':'invalid password','request':request})

# Dash baord page rendering
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


#signup page rendering
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

#signup post method
@app.post('/signup',response_class=HTMLResponse)
async def create_user(request: Request,User_Name:str=Form(...), User_Email:str=Form(...),User_Password:str=Form(...)):
    user_u=User(user_name=User_Name,user_email=User_Email,user_password=User_Password)
    user_collection.insert_one(user_u.dict())
    result=user_collection.find({})
    return templates.TemplateResponse("login.html",{"request":request,"user_login":result})

#collection for shipment
shipment_collection=user['shipment']
#basemodel for shipment
class shipment(BaseModel):
    InvoiceNumber:str
    ContainerNumber:int
    ShipmentDescription:str
    RouteDetails:str
    GoodsType:str
    Devices:int
    ExpectedDeliveryDate:str
    PONumber:int
    DeliveryNumber:int
    NDCNummber:int
    BatchID:int
    SerialNumberofGoods:int

# shipment page rendering
@app.get("/shipment", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("shipment.html", {"request": request})    

#shipment post method
@app.post('/shipment',response_class=HTMLResponse)
async def shipment_page(request: Request,invoicenumber:str=Form(...), containernumber:int=Form(...),shipmentdescription:str=Form(...),routedetails:str=Form(...),goodstype:str=Form(...),devices:int=Form(...),date:str=Form(...),ponumber:int=Form(...),deliverynumber:int=Form(...),ndcnumber:int=Form(...),batchid:int=Form(...),goods:int=Form(...)):
    shipment_s=shipment(InvoiceNumber=invoicenumber,ContainerNumber=containernumber,ShipmentDescription=shipmentdescription,RouteDetails=routedetails,GoodsType=goodstype,Devices=devices,ExpectedDeliveryDate=date,PONumber=ponumber,DeliveryNumber=deliverynumber,NDCNummber=ndcnumber,BatchID=batchid,SerialNumberofGoods=goods)
    shipment_collection.insert_one(shipment_s.dict())
    result=shipment_collection.find({})
    return templates.TemplateResponse("shipmentsuccess.html",{"request":request,"user_login":result})

#devicedata collection
mycoll=user['collection'] 
#basemodel for device data stream
class devicedata(BaseModel):
    Battery_Level: int
    Device_Id:int
    First_Sensor_temperature:int
    Route_From:str
    Route_To:str 
          
# device data 
@app.get("/devicedata", response_class=HTMLResponse)
async def stream_page(request: Request):
    shipments = []
    all_shipments = mycoll.find({},{"_id":0})
    for i in all_shipments:
        shipments.append(i)
    return templates.TemplateResponse("devicedata.html", {"request": request,"shipments":shipments})



