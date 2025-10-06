# U-TUTOR v3.0 - Mejoras en database_manager.py: Context managers, optimizaciones y nuevos métodos
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones eficientes - U-TUTOR v3.0"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
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
        """Crea una nueva conversación usando context manager - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
            conversation_id = cursor.lastrowid
            conn.commit()
            return conversation_id
    
    def get_conversations(self) -> List[Tuple]:
        """Obtiene todas las conversaciones - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at 
                FROM conversations 
                ORDER BY updated_at DESC
            ''')
            return cursor.fetchall()
    
    def get_conversation_by_id(self, conversation_id: int) -> Optional[Tuple]:
        """Obtiene una conversación específica por ID - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            return cursor.fetchone()
    
    def update_conversation_title(self, conversation_id: int, new_title: str) -> bool:
        """Actualiza el título de una conversación - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_title, conversation_id)
            )
            success = cursor.rowcount > 0
            conn.commit()
            return success
    
    def save_message(self, conversation_id: int, role: str, content: str):
        """Guarda un mensaje en la base de datos - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content)
            )
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            conn.commit()
    
    def load_conversation_messages(self, conversation_id: int) -> List[Tuple]:
        """Carga el historial de mensajes de una conversación - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content, timestamp 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC
            ''', (conversation_id,))
            return cursor.fetchall()
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Elimina una conversación y todos sus mensajes - U-TUTOR v3.0"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Primero eliminar todos los mensajes de la conversación
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                messages_deleted = cursor.rowcount
                print(f"🗑️ Mensajes eliminados: {messages_deleted}")
                
                # Luego eliminar la conversación
                cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                conversations_deleted = cursor.rowcount
                print(f"🗑️ Conversaciones eliminadas: {conversations_deleted}")
                
                # Confirmar los cambios
                conn.commit()
                
                # Verificar que se eliminó al menos la conversación
                success = conversations_deleted > 0
                print(f"✅ Eliminación exitosa: {success}")
                
                return success
        except Exception as e:
            print(f"❌ Error al eliminar conversación {conversation_id}: {e}")
            return False
    
    def get_conversation_stats(self) -> dict:
        """Obtiene estadísticas de las conversaciones - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT title, updated_at 
                FROM conversations 
                ORDER BY updated_at DESC 
                LIMIT 1
            """)
            latest_conversation = cursor.fetchone()
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'latest_conversation': latest_conversation
            }
    
    def export_conversation_to_markdown(self, conversation_id: int) -> str:
        """Exporta conversación a formato Markdown - U-TUTOR v3.0"""
        conversation = self.get_conversation_by_id(conversation_id)
        messages = self.load_conversation_messages(conversation_id)
        
        md_content = f"# {conversation[1]}\n\n"
        md_content += f"*Creado: {conversation[2]}*\n\n---\n\n"
        
        for role, content, timestamp in messages:
            emoji = "👤" if role == "user" else "🤖"
            md_content += f"### {emoji} {role.title()}\n{content}\n\n"
        
        return md_content

    def get_detailed_stats(self) -> dict:
        """Estadísticas avanzadas - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(msg_count) FROM (
                    SELECT COUNT(*) as msg_count 
                    FROM messages 
                    GROUP BY conversation_id
                )
            """)
            avg_messages = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT c.title, COUNT(m.id) as msg_count
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
                ORDER BY msg_count DESC
                LIMIT 1
            """)
            longest_conv = cursor.fetchone()
            
            # Obtener conversación más antigua
            cursor.execute("""
                SELECT created_at FROM conversations 
                ORDER BY created_at ASC 
                LIMIT 1
            """)
            oldest_result = cursor.fetchone()
            oldest_conversation = oldest_result[0] if oldest_result else None
            
            # Obtener conversación más reciente
            cursor.execute("""
                SELECT created_at FROM conversations 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            newest_result = cursor.fetchone()
            newest_conversation = newest_result[0] if newest_result else None
            
            return {
                'avg_messages_per_conv': round(avg_messages, 1),
                'longest_conversation': longest_conv,
                'oldest_conversation': oldest_conversation,
                'newest_conversation': newest_conversation
            }

    def search_conversations(self, query: str) -> List[Tuple]:
        """Busca conversaciones por título - U-TUTOR v3.0"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, created_at, updated_at 
                FROM conversations 
                WHERE LOWER(title) LIKE LOWER(?)
                ORDER BY updated_at DESC
            ''', (f'%{query}%',))
            return cursor.fetchall()
    
    def generate_auto_title(self, conversation_id: int, chat_manager) -> str:
        """Genera un título automático para una conversación usando IA - U-TUTOR v3.0"""
        try:
            messages_data = self.load_conversation_messages(conversation_id)
            messages = []
            
            for role, content, _ in messages_data:
                messages.append({"role": role, "content": content})
            
            if messages:
                ai_title = chat_manager.generate_ai_title(messages)
                # Actualizar el título en la base de datos
                self.update_conversation_title(conversation_id, ai_title)
                return ai_title
            else:
                return "Nueva Conversación"
                
        except Exception as e:
            print(f"Error generando título automático: {e}")
            return "Nueva Conversación"