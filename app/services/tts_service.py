import logging
import os
from pathlib import Path
from typing import Optional
import asyncio
import re

logger = logging.getLogger(__name__)

# TTS Provider imports
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False

class TTSService:
    """Text-to-Speech service supporting multiple languages and providers."""
    
    def __init__(self):
        self.preferred_providers = {
            'en': ['kokoro', 'pyttsx3', 'gtts'],
            'hi': ['gtts', 'kokoro'],
            'mr': ['gtts'], # gTTS has good Marathi support
        }
        self._kokoro_pipeline = None
        
    def _get_kokoro_pipeline(self):
        """Lazy initialization of Kokoro."""
        if KOKORO_AVAILABLE and self._kokoro_pipeline is None:
            try:
                # Kokoro supports Hindi with specific voice codes
                self._kokoro_pipeline = KPipeline(lang_code='h')
                logger.info("Kokoro TTS initialized for Hindi/English")
            except Exception as e:
                logger.error(f"Kokoro init failed: {e}")
        return self._kokoro_pipeline
    
    def generate_speech(self, text: str, language: str = 'en', output_path: str = None) -> Optional[str]:
        """Generate speech with language support."""
        if not text or not output_path:
            return None
    
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
        try:
            if language in ['hi', 'mr']:
                # Use gTTS for Hindi/Marathi (best quality)
                if GTTS_AVAILABLE:
                    # Clean text - remove markdown for TTS
                    clean_text = re.sub(r'[*#`_]', '', text)
                    # Devanagari range check also covers Marathi
                    clean_text = re.sub(r'[^\u0900-\u097F\s.,!?a-zA-Z0-9]', '', clean_text)[:5000]
                
                    tts = gTTS(text=clean_text, lang=language, slow=False)
                    tts.save(str(output_path))
                    logger.info(f"{language} TTS saved to {output_path}")
                    return str(output_path)

            elif language == 'en':  # English
                if GTTS_AVAILABLE:
                    clean_text = re.sub(r'[*#`_]', '', text)[:5000]
                    tts = gTTS(text=clean_text, lang='en', slow=False)
                    tts.save(str(output_path))
                    logger.info(f"English TTS saved to {output_path}")
                    return str(output_path)
            elif PYTTSX3_AVAILABLE:
                # Fallback to pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.save_to_file(text, str(output_path))
                engine.runAndWait()
                logger.info(f"pyttsx3 TTS saved to {output_path}")
                return str(output_path)
                
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
    
        return None
    
    def _generate_gtts(self, text: str, language: str, output_path: Path) -> str:
        """Generate using Google TTS (excellent for Hindi)."""
        # gTTS supports 'hi' for Hindi
        lang_code = 'hi' if language == 'hi' else 'en'
        
        # gTTS has a limit on text length, chunk if necessary
        max_chars = 5000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save(str(output_path))
        return str(output_path)
    
    def _generate_kokoro(self, text: str, language: str, output_path: Path) -> str:
        """Generate using Kokoro (high quality, local)."""
        pipeline = self._get_kokoro_pipeline()
        if not pipeline:
            raise RuntimeError("Kokoro not available")
        
        # Kokoro uses 'h' for Hindi, 'a' for American English
        # Voice mapping for Hindi
        voice = 'hf_alpha' if language == 'hi' else 'af_bella'
        
        generator = pipeline(
            text, 
            voice=voice,
            speed=1.0,
            split_pattern=r'\n+'
        )
        
        # Collect all audio segments
        import torch
        import soundfile as sf
        
        segments = []
        for _, _, audio in generator:
            segments.append(audio)
        
        if segments:
            full_audio = torch.cat(segments, dim=0)
            sf.write(str(output_path), full_audio.numpy(), 24000)
            return str(output_path)
        
        raise RuntimeError("No audio generated")
    
    def _generate_pyttsx3(self, text: str, output_path: Path) -> str:
        """Fallback using pyttsx3 (offline but limited voices)."""
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        
        # Try to find Hindi voice if available (rare on most systems)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'hindi' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # pyttsx3 saves as WAV
        temp_wav = output_path.with_suffix('.wav')
        engine.save_to_file(text, str(temp_wav))
        engine.runAndWait()
        
        # Convert to MP3 if needed
        if output_path.suffix == '.mp3':
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(str(temp_wav))
                audio.export(str(output_path), format='mp3')
                temp_wav.unlink()
                return str(output_path)
            except:
                return str(temp_wav)
        
        return str(temp_wav)

# Global instance
tts_service = TTSService()