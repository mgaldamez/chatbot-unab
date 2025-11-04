# U-TUTOR v5.0 - TTS Manager para Streamlit Cloud
# Motor de síntesis de voz optimizado para edge-tts + gTTS
# Compatible 100% con Streamlit Cloud

import asyncio
import os
import tempfile
import time
from typing import Optional
import streamlit as st

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class TTSManager:
    """
    Gestor optimizado de Text-to-Speech para Streamlit Cloud.

    Motor principal: edge-tts (mejor calidad y velocidad)
    Respaldo: gTTS (muy confiable)

    Características:
    - ✅ Edge-TTS para voces neuronales de calidad
    - ✅ gTTS como respaldo
    - ✅ Caché en memoria para textos repetidos
    - ✅ Compatible con Streamlit Cloud
    - ✅ Sin dependencias de hardware
    - ❌ NO usa pyttsx3
    - ❌ NO usa pyaudio
    - ❌ NO tiene micrófono
    """

    def __init__(self, engine_type: str = "edge-tts"):
        """
        Inicializa el gestor TTS.

        Args:
            engine_type: Motor a usar ('edge-tts' o 'gtts')
        """
        self.engine_type = engine_type
        self.cache = {}  # Caché en memoria: {texto} -> bytes
        self.temp_dir = tempfile.gettempdir()

        # Voces disponibles en edge-tts
        self.voice_map = {
            "es": "es-ES-AlvaroNeural",  # Español masculino
            "en": "en-US-AriaNeural",  # Inglés femenino (US)
            "pt": "pt-BR-AntonioNeural",  # Portugués masculino (Brasil)
            "fr": "fr-FR-HenriNeural",  # Francés masculino
        }

        # Validar que el motor esté disponible
        if engine_type == "edge-tts" and not EDGE_TTS_AVAILABLE:
            st.warning("⚠️ edge-tts no está instalado. Usando gTTS como alternativa.")
            self.engine_type = "gtts"

        if self.engine_type == "gtts" and not GTTS_AVAILABLE:
            st.error("❌ Ni edge-tts ni gTTS están instalados.")
            self.engine_type = None

    def text_to_speech_fast(self, text: str, use_cache: bool = True) -> Optional[bytes]:
        """
        Convierte texto a voz de forma rápida y retorna bytes de audio.

        Utiliza caché en memoria para optimizar rendimiento.

        Args:
            text: Texto a convertir
            use_cache: Si usar caché para textos repetidos

        Returns:
            Bytes de audio MP3 o None si hay error

        Ejemplo:
            audio_bytes = tts_manager.text_to_speech_fast("Hola mundo")
            st.audio(audio_bytes, format="audio/mp3")
        """
        try:
            # Validar entrada
            clean_text = text.strip()
            if not clean_text:
                return None

            # Verificar caché
            if use_cache and clean_text in self.cache:
                return self.cache[clean_text]

            # Generar audio
            audio_data = None

            if self.engine_type == "edge-tts":
                audio_data = self._generate_edge_tts_bytes(clean_text)
            elif self.engine_type == "gtts":
                audio_data = self._generate_gtts_bytes(clean_text)

            # Guardar en caché
            if audio_data and use_cache:
                # Limitar tamaño del caché a 50 items
                if len(self.cache) > 50:
                    # Eliminar el primer item (más antiguo)
                    self.cache.pop(next(iter(self.cache)))

                self.cache[clean_text] = audio_data

            return audio_data

        except Exception as e:
            st.error(f"❌ Error en TTS: {str(e)}")
            return None

    def _generate_edge_tts_bytes(self, text: str, lang: str = "es") -> Optional[bytes]:
        """
        Genera audio con edge-tts (motor principal) y retorna bytes.

        Args:
            text: Texto a convertir
            lang: Código de idioma

        Returns:
            Bytes de audio MP3 o None si falla
        """
        try:
            voice = self.voice_map.get(lang, "es-ES-AlvaroNeural")

            # Ejecutar generación asíncrona
            audio_data = asyncio.run(self._generate_edge_tts_async(text, voice))

            return audio_data

        except Exception as e:
            st.warning(f"⚠️ Edge-TTS falló: {str(e)}")
            return None

    async def _generate_edge_tts_async(self, text: str, voice: str) -> Optional[bytes]:
        """
        Genera audio de forma asíncrona con edge-tts.

        Args:
            text: Texto a convertir
            voice: Identificador de voz (ej: "es-ES-AlvaroNeural")

        Returns:
            Bytes de audio MP3
        """
        try:
            communicate = edge_tts.Communicate(text, voice)

            # Acumular chunks
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data if audio_data else None

        except Exception:
            return None

    def _generate_gtts_bytes(self, text: str, lang: str = "es") -> Optional[bytes]:
        """
        Genera audio con gTTS (respaldo) y retorna bytes.

        Args:
            text: Texto a convertir
            lang: Código de idioma

        Returns:
            Bytes de audio MP3 o None si falla
        """
        try:
            import io

            # Crear objeto gTTS
            tts = gTTS(text=text, lang=lang, slow=False, tld="com")

            # Guardar a BytesIO en lugar de archivo
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            return fp.read()

        except Exception as e:
            st.warning(f"⚠️ gTTS falló: {str(e)}")
            return None

    def text_to_speech_file(self, text: str, lang: str = "es") -> Optional[str]:
        """
        Convierte texto a voz y guarda en un archivo temporal.

        Retorna la ruta del archivo MP3.

        Args:
            text: Texto a convertir
            lang: Código de idioma

        Returns:
            Ruta del archivo MP3 o None si falla

        Ejemplo:
            audio_file = tts_manager.text_to_speech_file("Hola mundo")
            st.audio(audio_file)
        """
        try:
            # Generar bytes
            audio_bytes = self.text_to_speech_fast(text, use_cache=True)

            if not audio_bytes:
                return None

            # Guardar a archivo temporal
            timestamp = int(time.time() * 1000)
            audio_file = os.path.join(self.temp_dir, f"ututor_{lang}_{timestamp}.mp3")

            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                return audio_file
            else:
                return None

        except Exception as e:
            st.error(f"❌ Error al guardar archivo: {str(e)}")
            return None

    def preprocess_text_for_tts(self, text: str) -> str:
        """
        Preprocesa el texto para optimizar TTS.

        - Elimina markdown
        - Acorta URLs
        - Simplifica caracteres especiales
        - Limita longitud a 2000 caracteres

        Args:
            text: Texto a procesar

        Returns:
            Texto procesado
        """
        import re

        # Eliminar markdown
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
        text = re.sub(r"```[^`]*```", "", text)  # Code blocks
        text = re.sub(r"`([^`]+)`", r"\1", text)  # Inline code

        # Acortar URLs
        text = re.sub(r"https?://\S+", "enlace web", text)

        # Simplificar listas
        text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)

        # Limitar longitud
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "... [audio truncado]"

        return text.strip()

    def get_optimal_engine(self) -> str:
        """
        Determina el mejor motor TTS disponible.

        Prioridad: edge-tts > gtts

        Returns:
            Nombre del motor disponible o None
        """
        if EDGE_TTS_AVAILABLE:
            return "edge-tts"
        elif GTTS_AVAILABLE:
            return "gtts"
        else:
            return None

    def clear_cache(self):
        """Limpia el caché en memoria."""
        self.cache.clear()

    def get_cache_info(self) -> dict:
        """Retorna información del caché."""
        return {
            "size": len(self.cache),
            "engine": self.engine_type,
            "edge_tts_available": EDGE_TTS_AVAILABLE,
            "gtts_available": GTTS_AVAILABLE,
        }
