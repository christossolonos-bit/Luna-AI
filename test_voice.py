"""
Simple voice recognition test for Luna
"""

import speech_recognition as sr
import time

def test_voice_recognition():
    print("🎤 Testing Luna's Voice Recognition System")
    print("=" * 50)
    
    # Initialize recognizer and microphone
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    try:
        # List available microphones
        print("\n📱 Available microphones:")
        for i, mic in enumerate(sr.Microphone.list_microphone_names()):
            print(f"   {i}: {mic}")
        
        # Test microphone
        print(f"\n🎤 Testing microphone...")
        with microphone as source:
            print("   Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("   Ready! Say something...")
            
            # Listen for audio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
        print("   Processing speech...")
        
        # Recognize speech
        text = recognizer.recognize_google(audio)
        print(f"✅ Successfully recognized: '{text}'")
        
        return True
        
    except sr.WaitTimeoutError:
        print("❌ No speech detected within 5 seconds")
        return False
    except sr.UnknownValueError:
        print("❌ Could not understand speech")
        return False
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_voice_recognition()
    
    if success:
        print("\n🎉 Voice recognition is working!")
        print("You can now use Luna with voice chat!")
    else:
        print("\n🔧 Voice recognition needs setup.")
        print("Check the VOICE_SETUP_GUIDE.md for troubleshooting.")
