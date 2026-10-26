import os
import hashlib
import asyncio
import edge_tts

VOICES = {
    "antonio": "pt-BR-AntonioNeural",
    "francisca": "pt-BR-FranciscaNeural",
    "thalita": "pt-BR-ThalitaMultilingualNeural",
    "ryan_en": "en-GB-RyanNeural",
    "brian_en": "en-US-BrianNeural"
}

DEFAULT_VOICE = "pt-BR-AntonioNeural"

class VoiceEngine:
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            self.cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "audio_cache"))
        else:
            self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.current_voice = DEFAULT_VOICE

    def set_voice(self, voice_key_or_name):
        if voice_key_or_name in VOICES:
            self.current_voice = VOICES[voice_key_or_name]
        elif "Neural" in voice_key_or_name:
            self.current_voice = voice_key_or_name
        return self.current_voice

    async def text_to_speech(self, text: str, voice: str = None) -> str:
        """Gera um arquivo de áudio MP3 a partir do texto usando edge-tts e retorna o caminho."""
        selected_voice = voice or self.current_voice
        clean_text = text.strip()
        if not clean_text:
            return None

        # Hash único para reutilizar cache de frases repetidas como 'Sim, senhor'
        text_hash = hashlib.md5(f"{selected_voice}_{clean_text}".encode("utf-8")).hexdigest()
        filename = f"tts_{text_hash}.mp3"
        filepath = os.path.join(self.cache_dir, filename)

        if os.path.exists(filepath):
            return filepath

        try:
            communicate = edge_tts.Communicate(clean_text, selected_voice)
            await communicate.save(filepath)
            return filepath
        except Exception as e:
            print(f"Erro na síntese de voz edge-tts: {e}")
            return None
