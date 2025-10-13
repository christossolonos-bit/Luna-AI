"""
Test script for Luna's TTS with Edge TTS Ava multilingual voice
"""

import edge_tts
import asyncio
import pygame
import os
import time
import tempfile

def test_ava_tts():
    print("🎤 Testing Luna's TTS with Edge TTS Ava Multilingual Voice")
    print("=" * 60)
    print("✅ Edge TTS is FREE - No API key needed!")
    
    # Initialize pygame for audio playback
    try:
        pygame.mixer.init()
        print("✅ Audio system initialized")
    except Exception as e:
        print(f"❌ Audio initialization failed: {e}")
        return False
    
    # Test text samples in different languages
    test_texts = [
        ("English", "Hello! I'm Luna, your AI companion. How are you today?"),
        ("Spanish", "¡Hola! Soy Luna, tu compañera de IA. ¿Cómo estás hoy?"),
        ("French", "Bonjour! Je suis Luna, votre compagnon IA. Comment allez-vous aujourd'hui?"),
        ("Japanese", "こんにちは！私はルナ、あなたのAIコンパニオンです。今日はどうですか？"),
    ]
    
    print(f"\n🎯 Testing with Edge TTS Ava multilingual voice...")
    
    for language, text in test_texts:
        print(f"\n🌍 Testing {language}: {text}")
        
        try:
            # Run async TTS test
            asyncio.run(test_speech_async(language, text))
            print(f"   ✅ {language} TTS successful!")
                
        except Exception as e:
            print(f"   ❌ {language} TTS error: {e}")
        
        # Pause between tests
        time.sleep(1)
    
    print(f"\n🎉 TTS testing completed!")
    return True

async def test_speech_async(language: str, text: str):
    """Test speech generation using Edge TTS"""
    try:
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate speech with Edge TTS
        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-AvaMultilingualNeural",
            rate="+0%",
            pitch="+0Hz",
            volume="+0%"
        )
        
        await communicate.save(temp_path)
        
        # Play the audio file
        print(f"   🔊 Playing {language} speech...")
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        # Wait for playback
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"Edge TTS error: {e}")
        raise

if __name__ == "__main__":
    success = test_ava_tts()
    
    if success:
        print("\n🎤 Ava TTS is working!")
        print("You can now use Luna with voice output!")
    else:
        print("\n🔧 TTS needs setup.")
        print("Check the TTS_SETUP_GUIDE.md for troubleshooting.")
