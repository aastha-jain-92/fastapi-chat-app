from app.core.security import ALGORITHM
from app.db.database import engine, Base  
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, WebSocketDisconnect,HTTPException
from app.websockets.manager import manager
from app.db.database import SessionLocal
from app.db import models
from fastapi import FastAPI
from fastapi import WebSocket
from app.api import auth
from jose import jwt
import json
from app.api import messages
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.core.config import settings
from contextlib import asynccontextmanager
from app.routers.upload import router as upload_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(manager.subscribe())
    yield
    # Shutdown code

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(messages.router)
app.include_router(upload_router)

templates = Jinja2Templates(directory="app/templates")
app.include_router(auth.router, prefix="/auth")



@app.get("/")
def home(request: Request):
    token = request.cookies.get("token")
    if token:
        try:
            payload = jwt.decode(token,settings.secret_key, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                return RedirectResponse(url="/chat")
        except jwt.JWTError:
            pass
    return RedirectResponse(url="/login")

@app.get("/me")
def get_current_user(request: Request):
    print("Getting current user")
    token = request.cookies.get("token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "username": username
        }

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
        
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.cookies.get("token")
    if not token:
        print("No cookie token received")
        await websocket.close(code=1008)
        return
    try:
        payload = jwt.decode(token,settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.JWTError:
        await websocket.close()
        return

    await manager.connect(username, websocket)
    db = SessionLocal()
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data.get("type") == "typing":
                await manager.publish_message({
                "type": "typing",
                "sender": username,
                "receiver": data["to"]
                })
                continue
            receiver = data["to"]
            message = data["message"]

            # Check if receiver exists before saving
            receiver_exists = db.query(models.User).filter(models.User.username == receiver).first()

            if not receiver_exists:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"User '{receiver}' does not exist."
                }))
                continue

            # Save to DB only if receiver exists
            msg = models.Message(
                sender=username,
                receiver=receiver,
                content=message
            )
            db.add(msg)
            db.commit()
           
            await manager.publish_message({
            "type": "message",
            "sender": username,
            "receiver": receiver,
            "message": message
            })
            
    except WebSocketDisconnect:
        manager.disconnect(username,websocket)

@app.get("/chat", response_class=HTMLResponse)
def get_chat_page(request: Request):
    token = request.cookies.get("token")
    if not token:   
        return RedirectResponse("/login")
    return templates.TemplateResponse(
    name="chat.html",
    context={"request": request},
    request=request 
)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        context={"request": request},
        request=request
    )
    
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        name="register.html",
        context={"request": request},
        request=request
    )
    
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(manager.subscribe())

