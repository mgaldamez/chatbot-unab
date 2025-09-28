import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla para conversaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla para mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, title: str) -> int:
        """Crea una nueva conversación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def get_conversations(self) -> List[Tuple]:
        """Obtiene todas las conversaciones ordenadas por fecha de actualización"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at 
            FROM conversations 
            ORDER BY updated_at DESC
        ''')
        
        conversations = cursor.fetchall()
        conn.close()
        
        return conversations
    
    def get_conversation_by_id(self, conversation_id: int) -> Optional[Tuple]:
        """Obtiene una conversación específica por ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        
        conversation = cursor.fetchone()
        conn.close()
        
        return conversation
    
    def update_conversation_title(self, conversation_id: int, new_title: str) -> bool:
        """Actualiza el título de una conversación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_title, conversation_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def save_message(self, conversation_id: int, role: str, content: str):
        """Guarda un mensaje en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insertar mensaje
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        
        # Actualizar timestamp de la conversación
        cursor.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
    
    def load_conversation_messages(self, conversation_id: int) -> List[Tuple]:
        """Carga el historial de mensajes de una conversación"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        return messages
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Elimina una conversación y todos sus mensajes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Eliminar mensajes primero (por la foreign key)
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        
        # Luego eliminar la conversación
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_conversation_stats(self) -> dict:
        """Obtiene estadísticas de las conversaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de conversaciones
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        # Total de mensajes
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # Conversación más reciente
        cursor.execute("""
            SELECT title, updated_at 
            FROM conversations 
            ORDER BY updated_at DESC 
            LIMIT 1
        """)
        latest_conversation = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'latest_conversation': latest_conversation
        }