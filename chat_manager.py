# U-TUTOR v3.0 - Mejoras en chat_manager.py: Streaming, validaciones mejoradas y personalidades
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage


class ChatManager:
    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        """Inicializa ChatManager con temperatura configurable - U-TUTOR v3.0"""
        self.llm = ChatOpenAI(
            api_key=api_key,  # type: ignore
            model_name=model,  # type: ignore
            temperature=temperature  # type: ignore
        )
        self.model = model  # Almacenar el nombre del modelo para referencia rápida
        self.system_message = """Eres Jake, un tutor universitario empático y profesional.
        Ayuda al estudiante con sus dudas, habla como humano y nunca reveles que eres una IA."""
        self.temperature = temperature
    
    def prepare_messages_for_api(self, messages: List[Dict[str, str]]) -> List[tuple]:
        """Prepara los mensajes para la API de OpenAI"""
        api_messages = [("system", self.system_message)]
        
        for msg in messages:
            role = "human" if msg["role"] == "user" else "assistant"
            api_messages.append((role, msg["content"]))
        
        return api_messages
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Obtiene una respuesta del modelo de IA - U-TUTOR v3.0"""
        try:
            api_messages = self.prepare_messages_for_api(messages)
            response = self.llm.invoke(api_messages)
            # Asegurar que retornamos string
            if isinstance(response.content, str):
                return response.content
            elif isinstance(response.content, list):
                # Si es lista, convertir a string
                return str(response.content)
            return str(response.content)
        except Exception as e:
            raise Exception(f"Error al obtener respuesta del modelo: {str(e)}")
    
    def get_response_stream(self, messages: List[Dict[str, str]]):
        """Obtiene respuesta en streaming para mejor UX - U-TUTOR v3.0"""
        try:
            api_messages = self.prepare_messages_for_api(messages)
            return self.llm.stream(api_messages)
        except Exception as e:
            raise Exception(f"Error al obtener respuesta en streaming: {str(e)}")
    
    def translate_text(self, text: str, target_language: str = 'en') -> str:
        """Traduce texto usando la API de OpenAI - U-TUTOR v3.0"""
        try:
            if target_language == 'es':
                return text  # No traducir si ya está en español

            # Crear prompt de traducción
            translation_prompt = [
                ("system", f"""Eres un traductor experto. Traduce el siguiente texto al {target_language.upper()}.

                Reglas:
                - Mantén el tono y estilo del texto original
                - Preserva el formato (markdown, listas, etc.)
                - Traduce solo el contenido, no agregues explicaciones
                - Si el texto ya está en {target_language.upper()}, devuélvelo tal como está

                Responde SOLO con la traducción, nada más."""),
                ("human", text)
            ]

            response = self.llm.invoke(translation_prompt)
            # Asegurar que obtenemos string
            content = response.content if isinstance(response.content, str) else str(response.content)
            return content.strip()

        except Exception as e:
            print(f"Error en traducción: {e}")
            return text  # Devolver texto original si falla la traducción
    
    def generate_conversation_title(self, first_message: str, max_length: int = 50) -> str:
        """Genera un título para la conversación basado en el primer mensaje"""
        if len(first_message) > max_length:
            return first_message[:max_length].strip() + "..."
        return first_message.strip()
    
    def generate_ai_title(self, messages: List[Dict[str, str]]) -> str:
        """Genera un título inteligente usando la API - U-TUTOR v3.0"""
        try:
            # Preparar mensajes para generar título
            title_prompt = [
                {"role": "system", "content": """Eres un asistente que genera títulos concisos y descriptivos para conversaciones educativas.

                Reglas:
                - Máximo 40 caracteres
                - Usa palabras clave del tema principal
                - Sé específico y claro
                - Usa español
                - NO incluyas emojis
                - Ejemplos: "Matemáticas: Ecuaciones", "Biología: Fotosíntesis", "Programación: POO"

                Responde SOLO con el título, nada más."""},
                {"role": "user", "content": f"Genera un título para esta conversación:\n\n{self._format_messages_for_title(messages)}"}
            ]

            response = self.llm.invoke(title_prompt)
            # Asegurar que obtenemos string
            content = response.content if isinstance(response.content, str) else str(response.content)
            title = content.strip()
            
            # Limpiar y validar el título
            title = title.replace('"', '').replace("'", '').strip()
            if len(title) > 40:
                title = title[:37] + "..."
            
            return title if title else "Nueva Conversación"
            
        except Exception as e:
            print(f"Error generando título con IA: {e}")
            # Fallback al método original
            if messages and len(messages) > 0:
                first_msg = messages[0].get("content", "")
                return self.generate_conversation_title(first_msg)
            return "Nueva Conversación"
    
    def _format_messages_for_title(self, messages: List[Dict[str, str]]) -> str:
        """Formatea los primeros mensajes para generar título - U-TUTOR v3.0"""
        formatted = ""
        max_messages = min(3, len(messages))  # Solo primeros 3 mensajes
        
        for i in range(max_messages):
            msg = messages[i]
            role = "Estudiante" if msg["role"] == "user" else "Tutor"
            content = msg["content"][:200]  # Limitar contenido
            formatted += f"{role}: {content}\n\n"
        
        return formatted.strip()
    
    def validate_message(self, message: str) -> tuple:
        """Validación mejorada con mensajes específicos - U-TUTOR v3.0"""
        if not message or not message.strip():
            return False, "El mensaje no puede estar vacío"
        
        if len(message) > 4000:
            return False, "El mensaje es demasiado largo (máx. 4000 caracteres)"
        
        # Detectar spam o mensajes repetitivos
        if len(message) > 10 and message == message[0] * len(message):
            return False, "Por favor, escribe un mensaje válido"
        
        return True, ""
    
    def update_personality(self, personality_type: str):
        """Actualiza la personalidad del asistente - U-TUTOR v3.0"""
        personalities = {
            "Profesional": """Eres Jake, un tutor universitario profesional y formal. 
            Proporciona explicaciones detalladas y académicas.""",
            
            "Amigable": """Eres Jake, un tutor universitario cercano y amigable. 
            Explicas de manera casual pero efectiva, usando ejemplos cotidianos.""",
            
            "Conciso": """Eres Jake, un tutor universitario directo y conciso. 
            Vas al grano y das respuestas precisas sin rodeos.""",
            
            "Detallado": """Eres Jake, un tutor universitario exhaustivo. 
            Proporcionas explicaciones profundas con múltiples ejemplos y contexto."""
        }
        
        self.system_message = personalities.get(personality_type, self.system_message)

    def update_temperature(self, new_temperature: float):
        """Actualiza la temperatura del modelo - U-TUTOR v5.0"""
        self.temperature = new_temperature
        self.llm.temperature = new_temperature
        
    