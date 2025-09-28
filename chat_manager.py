from typing import List, Dict, Any
from langchain_openai import ChatOpenAI


class ChatManager:
    def __init__(self, api_key: str, model: str , temperature: float = 0):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        self.system_message = """Eres Jake, un tutor universitario empático y profesional. 
        Ayuda al estudiante con sus dudas, habla como humano y nunca reveles que eres una IA."""
    
    def prepare_messages_for_api(self, messages: List[Dict[str, str]]) -> List[tuple]:
        """Prepara los mensajes para la API de OpenAI"""
        api_messages = [("system", self.system_message)]
        
        for msg in messages:
            role = "human" if msg["role"] == "user" else "assistant"
            api_messages.append((role, msg["content"]))
        
        return api_messages
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Obtiene una respuesta del modelo de IA"""
        try:
            api_messages = self.prepare_messages_for_api(messages)
            response = self.llm.invoke(api_messages)
            return response.content
        except Exception as e:
            raise Exception(f"Error al obtener respuesta del modelo: {str(e)}")
    
    def generate_conversation_title(self, first_message: str, max_length: int = 50) -> str:
        """Genera un título para la conversación basado en el primer mensaje"""
        if len(first_message) > max_length:
            return first_message[:max_length].strip() + "..."
        return first_message.strip()
    
    def validate_message(self, message: str) -> bool:
        """Valida que el mensaje no esté vacío"""
        return message and message.strip()