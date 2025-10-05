from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
from database import get_db_connection, close_db_connection
import psycopg2

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    code: Optional[str] = None

class ToolCreate(Tool):
    user_id: int

class ToolResponse(Tool):
    user_ids: List[int] = []

class Chat(BaseModel):
    role: str
    message: str

# User routes
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO USERS (name, hashed_password) VALUES (%s, %s) RETURNING id, name",
            (user.name, hashed_password)
        )
        new_user = cur.fetchone()
        conn.commit()
        return {"id": new_user["id"], "name": new_user["name"]}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)

# Tool routes
@app.post("/tools/", response_model=ToolResponse)
async def create_tool(tool: ToolCreate):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # First, verify the user exists
        cur.execute("SELECT id FROM USERS WHERE id = %s", (tool.user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Begin transaction
        cur.execute(
            "INSERT INTO TOOLS (name, description, code) VALUES (%s, %s, %s) RETURNING *",
            (tool.name, tool.description, tool.code)
        )
        new_tool = cur.fetchone()

        # Create the user-tool association
        cur.execute(
            "INSERT INTO USERS_TOOLS (user_id, tool_name) VALUES (%s, %s)",
            (tool.user_id, tool.name)
        )
        
        # Get all users associated with this tool
        cur.execute(
            "SELECT user_id FROM USERS_TOOLS WHERE tool_name = %s",
            (tool.name,)
        )
        user_ids = [row["user_id"] for row in cur.fetchall()]
        
        conn.commit()
        return {**new_tool, "user_ids": user_ids}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)

@app.get("/tools/", response_model=List[ToolResponse])
async def get_tools():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.*, array_agg(ut.user_id) as user_ids
            FROM TOOLS t
            LEFT JOIN USERS_TOOLS ut ON t.name = ut.tool_name
            GROUP BY t.name, t.description, t.code, t."createdAt"
        """)
        tools = cur.fetchall()
        return tools
    finally:
        close_db_connection(conn)

@app.get("/users/{user_id}/tools/", response_model=List[ToolResponse])
async def get_user_tools(user_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # First verify the user exists
        cur.execute("SELECT id FROM USERS WHERE id = %s", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Get all tools associated with the user
        cur.execute("""
            SELECT t.*, array_agg(ut2.user_id) as user_ids
            FROM TOOLS t
            INNER JOIN USERS_TOOLS ut ON t.name = ut.tool_name
            LEFT JOIN USERS_TOOLS ut2 ON t.name = ut2.tool_name
            WHERE ut.user_id = %s
            GROUP BY t.name, t.description, t.code, t."createdAt"
        """, (user_id,))
        tools = cur.fetchall()
        return tools
    finally:
        close_db_connection(conn)

@app.post("/tools/{tool_name}/users/{user_id}")
async def associate_tool_with_user(tool_name: str, user_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Verify both tool and user exist
        cur.execute("SELECT name FROM TOOLS WHERE name = %s", (tool_name,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Tool not found")
            
        cur.execute("SELECT id FROM USERS WHERE id = %s", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Create the association
        cur.execute(
            "INSERT INTO USERS_TOOLS (user_id, tool_name) VALUES (%s, %s)",
            (user_id, tool_name)
        )
        conn.commit()
        return {"message": "Tool associated with user successfully"}
    except psycopg2.Error as e:
        conn.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(status_code=400, detail="Tool is already associated with this user")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)

# Session routes
@app.post("/sessions/")
async def create_session():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO SESSIONS DEFAULT VALUES RETURNING id")
        session = cur.fetchone()
        conn.commit()
        return {"session_id": session["id"]}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)

# Chat routes
@app.post("/sessions/{session_id}/chats/")
async def create_chat(session_id: int, chat: Chat):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # First create the chat message
        cur.execute(
            "INSERT INTO CHATS (role, message) VALUES (%s, %s) RETURNING id",
            (chat.role, chat.message)
        )
        chat_id = cur.fetchone()["id"]
        
        # Then link it to the session
        cur.execute(
            "INSERT INTO SESSIONS_CHAT (session_id, chat_id) VALUES (%s, %s)",
            (session_id, chat_id)
        )
        conn.commit()
        return {"chat_id": chat_id, "session_id": session_id}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        close_db_connection(conn)

@app.get("/sessions/{session_id}/chats/")
async def get_session_chats(session_id: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.* FROM CHATS c
            JOIN SESSIONS_CHAT sc ON c.id = sc.chat_id
            WHERE sc.session_id = %s
            ORDER BY c.time
        """, (session_id,))
        chats = cur.fetchall()
        return chats
    finally:
        close_db_connection(conn)