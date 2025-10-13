# 🎤 Luna Voice Recognition Setup Guide

## Quick Start

Luna now supports **push-to-talk voice recognition**! Just hold the **SPACEBAR** to speak to her.

---

## 🎯 Features

- ✅ **Push-to-Talk**: Hold SPACEBAR to record
- ✅ **Real-time Transcription**: Google Speech Recognition
- ✅ **DNA Memory Integration**: Voice conversations are remembered
- ✅ **Visual Feedback**: Recording status indicators
- ✅ **Microphone Testing**: Test your mic before chatting

---

## 📦 Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements_voice.txt
```

### 2. Install PyAudio (Windows)
If you get errors with PyAudio:
```bash
# Download the correct wheel for your Python version from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# Then install:
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

### 3. Alternative PyAudio Installation
```bash
# Try conda instead:
conda install pyaudio

# Or use pip with specific flags:
pip install --upgrade pip
pip install pyaudio --only-binary=all
```

---

## 🎮 How to Use

### Voice Chat Controls:
- **Hold SPACEBAR**: Start recording
- **Release SPACEBAR**: Stop recording and process
- **Test Mic Button**: Test your microphone

### Visual Indicators:
- 🎤 **Blue**: Ready to record
- 🔴 **Red**: Currently recording
- 🧠 **Orange**: Processing speech
- ✅ **Green**: Success

---

## 🔧 Troubleshooting

### "No module named 'speech_recognition'"
```bash
pip install SpeechRecognition
```

### "No module named 'pyaudio'"
```bash
# Windows:
pip install pipwin
pipwin install pyaudio

# Or download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

### "Microphone not found"
1. Check your microphone is connected
2. Test with other applications
3. Check Windows sound settings
4. Try running as administrator

### "Could not understand speech"
1. Speak clearly and slowly
2. Reduce background noise
3. Check microphone levels
4. Test with the "Test Mic" button

### "Speech recognition error"
- Check internet connection (uses Google Speech API)
- Try speaking louder
- Ensure microphone is working

---

## 🎤 Microphone Setup

### Windows:
1. Right-click speaker icon → "Open Sound settings"
2. Scroll down to "Input"
3. Select your microphone
4. Click "Device properties" to test

### Microphone Levels:
- **Too quiet**: Increase input volume
- **Too loud**: Decrease input volume or move away
- **Background noise**: Use noise cancellation if available

---

## 🔍 Testing Your Setup

### 1. Run Luna
```bash
python luna_clean.py
```

### 2. Test Microphone
- Click "Test Mic" button
- Say "Hello Luna"
- Check if it transcribes correctly

### 3. Voice Chat
- Hold SPACEBAR
- Say "Hello, how are you?"
- Release SPACEBAR
- Watch Luna respond!

---

## ⚙️ Advanced Configuration

### Speech Recognition Settings
Edit `luna_clean.py` to customize:

```python
# Adjust recognition sensitivity
self.recognizer.energy_threshold = 300
self.recognizer.dynamic_energy_threshold = True
self.recognizer.pause_threshold = 0.8
```

### Recording Settings
```python
# Adjust recording timeouts
audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
```

---

## 🌟 Tips for Best Results

### Speaking:
- ✅ Speak clearly and at normal pace
- ✅ Reduce background noise
- ✅ Hold SPACEBAR firmly while speaking
- ✅ Release SPACEBAR when finished

### Environment:
- ✅ Quiet room works best
- ✅ Close other applications using microphone
- ✅ Use a good quality microphone if possible

### Practice:
- ✅ Test with simple phrases first
- ✅ Use the "Test Mic" button to practice
- ✅ Luna learns from your voice patterns

---

## 🔄 Voice + DNA Memory

Every voice conversation is automatically saved to Luna's DNA memory system:

```
🎤 Voice: "I love anime"
🧬 DNA Memory: Encoded as nucleotide strand
💬 Luna: "Me too! What's your favorite?"
🔄 Future: Luna remembers your anime preferences!
```

---

## 🚀 What's Next?

### Planned Features:
- 🎵 **Text-to-Speech**: Luna speaks back to you
- 🌍 **Multiple Languages**: Support for different languages
- 🎛️ **Voice Commands**: Special commands for Luna
- 🔇 **Voice Activity Detection**: Auto-start/stop recording
- 📱 **Mobile Support**: Voice chat on mobile devices

---

## 📞 Support

If you're having issues:

1. **Check microphone**: Test in other apps
2. **Check internet**: Voice recognition needs internet
3. **Check permissions**: Allow microphone access
4. **Try test button**: Use "Test Mic" to debug
5. **Check console**: Look for error messages

---

**Ready to talk to Luna? Hold that SPACEBAR and start chatting!** 🎤🌸
