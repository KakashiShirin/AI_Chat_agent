import uuid
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChatSession:
    """Represents a single chat session with its own context"""
    session_id: str
    chat_id: str
    database_session_id: str
    created_at: float
    last_activity: float
    message_count: int
    context: Dict[str, Any]
    
    def __post_init__(self):
        if not self.context:
            self.context = {
                "schema_info": None,
                "last_query": None,
                "last_result": None,
                "conversation_history": [],
                "data_summary": None
            }

class ChatSessionManager:
    """Manages multiple chat sessions with isolated contexts"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = 3600  # 1 hour timeout
    
    def create_chat_session(self, database_session_id: str) -> str:
        """Create a new chat session for a specific database session"""
        chat_id = str(uuid.uuid4())
        current_time = time.time()
        
        session = ChatSession(
            session_id=database_session_id,
            chat_id=chat_id,
            database_session_id=database_session_id,
            created_at=current_time,
            last_activity=current_time,
            message_count=0,
            context={}
        )
        
        self.sessions[chat_id] = session
        logger.info(f"📱 Created new chat session: {chat_id} for database: {database_session_id}")
        return chat_id
    
    def get_chat_session(self, chat_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        session = self.sessions.get(chat_id)
        if session:
            # Update last activity
            session.last_activity = time.time()
            return session
        return None
    
    def update_chat_context(self, chat_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update the context of a specific chat session"""
        session = self.get_chat_session(chat_id)
        if session:
            session.context.update(context_updates)
            session.message_count += 1
            logger.info(f"📝 Updated context for chat {chat_id}")
            return True
        return False
    
    def add_message_to_history(self, chat_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to the chat history"""
        session = self.get_chat_session(chat_id)
        if session:
            if "conversation_history" not in session.context:
                session.context["conversation_history"] = []
            
            session.context["conversation_history"].append({
                "timestamp": time.time(),
                "message": message
            })
            
            # Keep only last 20 messages to prevent memory bloat
            if len(session.context["conversation_history"]) > 20:
                session.context["conversation_history"] = session.context["conversation_history"][-20:]
            
            logger.info(f"💬 Added message to chat {chat_id} history")
            return True
        return False
    
    def get_chat_context(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get the context of a specific chat session"""
        session = self.get_chat_session(chat_id)
        if session:
            return session.context
        return None
    
    def get_database_session_id(self, chat_id: str) -> Optional[str]:
        """Get the database session ID for a chat session"""
        session = self.get_chat_session(chat_id)
        if session:
            return session.database_session_id
        return None
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired chat sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for chat_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(chat_id)
        
        for chat_id in expired_sessions:
            del self.sessions[chat_id]
            logger.info(f"🗑️ Cleaned up expired chat session: {chat_id}")
        
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active chat sessions"""
        current_time = time.time()
        active_sessions = len(self.sessions)
        total_messages = sum(session.message_count for session in self.sessions.values())
        
        return {
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "session_timeout": self.session_timeout,
            "sessions": [
                {
                    "chat_id": chat_id,
                    "database_session_id": session.database_session_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "message_count": session.message_count,
                    "age_minutes": (current_time - session.created_at) / 60
                }
                for chat_id, session in self.sessions.items()
            ]
        }
    
    def delete_chat_session(self, chat_id: str) -> bool:
        """Delete a specific chat session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            logger.info(f"🗑️ Deleted chat session: {chat_id}")
            return True
        return False

# Global instance
chat_session_manager = ChatSessionManager()
