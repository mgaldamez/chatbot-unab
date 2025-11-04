# U-TUTOR v5.0 - Audio Manager optimizado para Streamlit Cloud
# Solo Texto a Voz (TTS) con edge-tts y gTTS como respaldo
# Compatible con Streamlit Cloud (sin acceso a micrófono ni hardware local)

import os
import tempfile
import time
from typing import Optional
import asyncio
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


class AudioManager:
    """
    Gestor de audio para U-TUTOR v5.0 - Optimizado para Streamlit Cloud

    Características:
    - ✅ Solo Texto a Voz (TTS)
    - ✅ Edge-TTS como motor principal (mejor calidad y velocidad)
    - ✅ gTTS como respaldo
    - ✅ Caché de audio para evitar recálculos
    - ✅ Compatible con Streamlit Cloud
    - ❌ SIN micrófono
    - ❌ SIN voz a texto
    - ❌ SIN dependencias de hardware
    """

    def __init__(self):
        """Inicializa el gestor de audio"""
        self.temp_dir = tempfile.gettempdir()
        # Caché de audio: {cache_key} -> ruta_archivo
        self.audio_cache = {}

        # Verificar disponibilidad de motores TTS
        self.edge_tts_available = EDGE_TTS_AVAILABLE
        self.gtts_available = GTTS_AVAILABLE

    def text_to_speech(self, text: str, lang: str = "es") -> Optional[str]:
        """
        Convierte texto a voz y retorna la ruta del archivo MP3.

        Utiliza edge-tts como motor principal (mejor calidad y velocidad).
        Respaldo: gTTS si edge-tts falla.

        Args:
            text: Texto a convertir a voz
            lang: Código de idioma ('es' para español, 'en' para inglés)

        Returns:
            Ruta del archivo MP3 generado o None si hay error

        Ejemplo:
            audio_file = audio_manager.text_to_speech("Hola mundo")
            st.audio(audio_file)
        """
        try:
            # Limpiar y validar texto
            clean_text = text.strip()
            if not clean_text:
                st.warning("⚠️ No hay texto para convertir a audio")
                return None

            # Crear clave de caché
            cache_key = f"{clean_text}_{lang}"

            # Verificar caché primero
            if cache_key in self.audio_cache:
                cached_file = self.audio_cache[cache_key]
                if os.path.exists(cached_file):
                    return cached_file
                else:
                    # Archivo en caché fue eliminado
                    del self.audio_cache[cache_key]

            # Intentar edge-tts primero (mejor calidad y velocidad)
            if self.edge_tts_available:
                audio_file = self._generate_edge_tts(clean_text, lang)
                if audio_file:
                    self.audio_cache[cache_key] = audio_file
                    return audio_file

            # Respaldo: gTTS
            if self.gtts_available:
                audio_file = self._generate_gtts(clean_text, lang)
                if audio_file:
                    self.audio_cache[cache_key] = audio_file
                    return audio_file

            # Error: Ningún motor disponible
            st.error("❌ No hay motor TTS disponible. Instala: pip install edge-tts")
            return None

        except Exception as e:
            st.error(f"❌ Error al generar audio: {str(e)}")
            return None

    def _generate_edge_tts(self, text: str, lang: str = "es") -> Optional[str]:
        """
        Genera audio con edge-tts (motor principal).

        Edge-TTS ventajas:
        - Mejor calidad de voz neural
        - Más rápido que gTTS
        - Compatible con Streamlit Cloud

        Args:
            text: Texto a convertir
            lang: Código de idioma

        Returns:
            Ruta del archivo MP3 o None si falla
        """
        try:
            # Mapear código de idioma a voz edge-tts
            voice_map = {
                "es": "es-ES-AlvaroNeural",  # Voz masculina española
                # "es": "es-ES-ElviraNeural",  # Alternativa: voz femenina
                "en": "en-US-AriaNeural",  # Voz femenina inglés (US)
                # "en": "en-US-GuyNeural",  # Alternativa: voz masculina inglés (US)
            }

            voice = voice_map.get(lang, "es-ES-AlvaroNeural")

            # Generar audio de forma asíncrona
            audio_data = asyncio.run(self._generate_edge_tts_async(text, voice))

            if not audio_data:
                return None

            # Guardar archivo MP3 temporal
            timestamp = int(time.time() * 1000)
            audio_file = os.path.join(
                self.temp_dir, f"ututor_edge_{lang}_{timestamp}.mp3"
            )

            with open(audio_file, "wb") as f:
                f.write(audio_data)

            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                return audio_file
            else:
                return None

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
            Datos de audio en bytes o None si falla
        """
        try:
            communicate = edge_tts.Communicate(text, voice)

            # Acumular chunks de audio
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            return audio_data if audio_data else None

        except Exception as e:
            return None

    def _generate_gtts(self, text: str, lang: str = "es") -> Optional[str]:
        """
        Genera audio con gTTS (respaldo secundario).

        gTTS ventajas:
        - Muy confiable
        - No requiere configuración especial

        gTTS desventajas:
        - Más lento que edge-tts
        - Requiere conexión a internet

        Args:
            text: Texto a convertir
            lang: Código de idioma

        Returns:
            Ruta del archivo MP3 o None si falla
        """
        try:
            # Crear objeto gTTS
            tts = gTTS(text=text, lang=lang, slow=False, tld="com")

            # Guardar archivo MP3 temporal
            timestamp = int(time.time() * 1000)
            audio_file = os.path.join(
                self.temp_dir, f"ututor_gtts_{lang}_{timestamp}.mp3"
            )

            tts.save(audio_file)

            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                return audio_file
            else:
                return None

        except Exception as e:
            st.warning(f"⚠️ gTTS falló: {str(e)}")
            return None

    def clear_audio_cache(self):
        """
        Limpia el caché de audio para liberar memoria.

        Ejemplo:
            audio_manager.clear_audio_cache()
        """
        self.audio_cache.clear()
        st.info("🧹 Caché de audio limpiado")

    def get_cache_size(self) -> int:
        """
        Retorna el número de archivos en el caché.

        Returns:
            Cantidad de archivos cacheados
        """
        return len(self.audio_cache)

    def get_available_voices_info(self) -> dict:
        """
        Retorna información sobre los motores TTS disponibles.

        Returns:
            Diccionario con información de disponibilidad

        Ejemplo:
            info = audio_manager.get_available_voices_info()
            print(info)
            # {
            #     'edge_tts_available': True,
            #     'gtts_available': True,
            #     'available_languages': ['es', 'en'],
            #     'cache_size': 5
            # }
        """
        return {
            "edge_tts_available": self.edge_tts_available,
            "gtts_available": self.gtts_available,
            "available_languages": ["es", "en"],
            "cache_size": len(self.audio_cache),
            "motors": {
                "edge_tts": "✅ Disponible" if self.edge_tts_available else "❌ No instalado",
                "gtts": "✅ Disponible" if self.gtts_available else "❌ No instalado",
            },
        }

    def cleanup_old_files(self, max_age_seconds: int = 3600):
        """
        Limpia archivos de audio temporal que tienen más de max_age_seconds.

        Args:
            max_age_seconds: Edad máxima en segundos (default 1 hora)

        Ejemplo:
            audio_manager.cleanup_old_files(max_age_seconds=1800)  # 30 minutos
        """
        try:
            current_time = time.time()
            for filename in os.listdir(self.temp_dir):
                if filename.startswith("ututor_") and filename.endswith(".mp3"):
                    filepath = os.path.join(self.temp_dir, filename)
                    file_age = current_time - os.path.getmtime(filepath)

                    if file_age > max_age_seconds:
                        os.remove(filepath)
        except Exception:
            pass  # Silenciar errores de limpieza
