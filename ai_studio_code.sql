-- 1. USERS Table
-- Represents individual users of the system.
CREATE TABLE USERS (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL, -- Added UNIQUE constraint for name
    hashed_password VARCHAR(255) NOT NULL,
);

-- 2. TOOLS Table
-- Represents available tools in the system.
CREATE TABLE TOOLS (
    name VARCHAR(255) PRIMARY KEY, -- Used 'name' as PK as it's the FK in USERS_TOOLS
    description TEXT,
    code TEXT,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. SESSIONS Table
-- Represents ongoing or historical sessions (e.g., chat sessions, work sessions).
CREATE TABLE SESSIONS (
    id BIGSERIAL PRIMARY KEY,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "lastUpdated" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. CHATS Table
-- Represents individual chat messages. An 'id' is added as a primary key for relational integrity.
CREATE TABLE CHATS (
    id BIGSERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,    -- e.g., 'user', 'assistant', 'system'
    message TEXT NOT NULL,
    time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Junction Table: USERS_TOOLS (Many-to-Many: USERS <-> TOOLS)
-- Links users to the tools they are specific to or have access to.
CREATE TABLE USERS_TOOLS (
    user_id BIGINT NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    
    PRIMARY KEY (user_id, tool_name),
    
    FOREIGN KEY (user_id) 
        REFERENCES USERS(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (tool_name) 
        REFERENCES TOOLS(name) 
        ON DELETE CASCADE
);

-- 6. Junction Table: USERS_SESSIONS (Many-to-Many: USERS <-> SESSIONS)
-- Links users to their specific sessions.
CREATE TABLE USERS_SESSIONS (
    user_id BIGINT NOT NULL,
    session_id BIGINT NOT NULL,
    
    PRIMARY KEY (user_id, session_id),
    
    FOREIGN KEY (user_id) 
        REFERENCES USERS(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (session_id) 
        REFERENCES SESSIONS(id) 
        ON DELETE CASCADE
);

-- 7. Junction Table: SESSIONS_CHAT (Many-to-Many: SESSIONS <-> CHATS)
-- Links chat messages to the sessions they belong to.
CREATE TABLE SESSIONS_CHAT (
    session_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    
    PRIMARY KEY (session_id, chat_id),
    
    FOREIGN KEY (session_id) 
        REFERENCES SESSIONS(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (chat_id) 
        REFERENCES CHATS(id) 
        ON DELETE CASCADE
);