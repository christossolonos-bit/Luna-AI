# voice_modulation.py
import re
import random

# 🎭 Dynamic voice modulation based on word emphasis
EMPHASIS_PATTERNS = {
    "love_words": {
        "words": ["love", "adore", "cherish", "treasure", "darling", "sweetheart", "beloved", "dear"],
        "modulation": {"pitch": "+15%", "rate": "-10%", "volume": "+10%"},
        "description": "romantic emphasis"
    },
    "excitement_words": {
        "words": ["wow", "amazing", "incredible", "fantastic", "awesome", "brilliant", "perfect", "yay"],
        "modulation": {"pitch": "+20%", "rate": "+15%", "volume": "+20%"},
        "description": "excited emphasis"
    },
    "sadness_words": {
        "words": ["sad", "cry", "tears", "hurt", "pain", "sorry", "heartbroken", "lonely"],
        "modulation": {"pitch": "-15%", "rate": "-20%", "volume": "-10%"},
        "description": "sad emphasis"
    },
    "anger_words": {
        "words": ["angry", "mad", "furious", "hate", "disgust", "annoyed", "irritated"],
        "modulation": {"pitch": "+10%", "rate": "+10%", "volume": "+25%"},
        "description": "angry emphasis"
    },
    "whisper_words": {
        "words": ["secret", "whisper", "quiet", "shh", "hush", "silent", "private"],
        "modulation": {"pitch": "-10%", "rate": "-15%", "volume": "-25%"},
        "description": "whisper emphasis"
    },
    "surprise_words": {
        "words": ["what", "really", "seriously", "no way", "unbelievable", "shocked"],
        "modulation": {"pitch": "+25%", "rate": "+20%", "volume": "+15%"},
        "description": "surprised emphasis"
    },
    "question_words": {
        "words": ["why", "how", "what", "when", "where", "who", "?"],
        "modulation": {"pitch": "+10%", "rate": "+0%", "volume": "+5%"},
        "description": "question emphasis"
    },
    "emphasis_words": {
        "words": ["really", "truly", "actually", "definitely", "absolutely", "certainly"],
        "modulation": {"pitch": "+5%", "rate": "-5%", "volume": "+10%"},
        "description": "general emphasis"
    }
}

# 🎵 Musical/emotional patterns
MUSICAL_PATTERNS = {
    "laughter": {
        "triggers": ["hehe", "haha", "teehee", "giggle", "laugh", "chuckle"],
        "modulation": {"pitch": "+25%", "rate": "+20%", "volume": "+15%"}
    },
    "sighing": {
        "triggers": ["sigh", "breath", "exhale", "inhale"],
        "modulation": {"pitch": "-20%", "rate": "-25%", "volume": "-15%"}
    },
    "gasping": {
        "triggers": ["gasp", "gulp", "choke", "pant"],
        "modulation": {"pitch": "+30%", "rate": "+25%", "volume": "+20%"}
    }
}

def detect_emphasis_words(text: str):
    """Detect words that need emphasis and return modulation settings"""
    text_lower = text.lower()
    detected_modulations = []
    
    # Check for emphasis patterns
    for pattern_name, pattern_data in EMPHASIS_PATTERNS.items():
        for word in pattern_data["words"]:
            if word in text_lower:
                detected_modulations.append({
                    "type": pattern_name,
                    "word": word,
                    "modulation": pattern_data["modulation"],
                    "description": pattern_data["description"]
                })
                break  # Only use first match per pattern
    
    # Check for musical patterns
    for pattern_name, pattern_data in MUSICAL_PATTERNS.items():
        for trigger in pattern_data["triggers"]:
            if trigger in text_lower:
                detected_modulations.append({
                    "type": pattern_name,
                    "word": trigger,
                    "modulation": pattern_data["modulation"],
                    "description": f"{pattern_name} emphasis"
                })
                break
    
    return detected_modulations

def calculate_dynamic_modulation(text: str, base_mood: str = "soft"):
    """Calculate dynamic voice modulation based on text content"""
    emphasis_modulations = detect_emphasis_words(text)
    
    if not emphasis_modulations:
        return {}
    
    # Combine all detected modulations
    final_modulation = {}
    
    for emphasis in emphasis_modulations:
        modulation = emphasis["modulation"]
        
        # Apply modulation with mood-based adjustments
        for param, value in modulation.items():
            if param in final_modulation:
                # If multiple emphases, take the stronger one
                current_value = final_modulation[param]
                if "pitch" in param:
                    # For pitch, take the highest absolute value
                    if abs(int(value.replace("%", ""))) > abs(int(current_value.replace("%", ""))):
                        final_modulation[param] = value
                elif "rate" in param:
                    # For rate, take the highest absolute value
                    if abs(int(value.replace("%", ""))) > abs(int(current_value.replace("%", ""))):
                        final_modulation[param] = value
                elif "volume" in param:
                    # For volume, take the highest absolute value
                    if abs(int(value.replace("%", ""))) > abs(int(current_value.replace("%", ""))):
                        final_modulation[param] = value
            else:
                final_modulation[param] = value
    
    # Optimized natural pause simulation - reduced processing
    # Only check for key emphasis words to reduce latency
    key_words = ["love", "wow", "amazing", "what", "why", "how"]
    text_lower = text.lower()
    has_key_words = any(word in text_lower for word in key_words)
    
    # Minimal rate adjustment for speed
    if has_key_words and "rate" in final_modulation:
        current_rate = int(final_modulation["rate"].replace("%", ""))
        # Smaller adjustment for faster response
        final_modulation["rate"] = f"{current_rate - 2}%"
    
    # Add mood-based adjustments
    mood_adjustments = get_mood_adjustments(base_mood, {"depth": len(text.split()) // 10})  # Simple depth estimation
    for param, value in mood_adjustments.items():
        if param in final_modulation:
            # Combine mood and emphasis modulations
            current = int(final_modulation[param].replace("%", ""))
            mood_val = int(value.replace("%", ""))
            combined = current + mood_val
            # Ensure rate stays within valid bounds (-100% to +50% for speed limit)
            if param == "rate":
                combined = max(-100, min(50, combined))
            final_modulation[param] = f"{combined:+d}%"
        else:
            final_modulation[param] = value
    
    return final_modulation

# 🌟 Dynamic Mood Evolution System
DYNAMIC_MOOD_BASE = {
    "soft": {"pitch": "-5%", "rate": "-10%", "volume": "-5%"},
    "cheeky": {"pitch": "+10%", "rate": "+15%", "volume": "+10%"},
    "sultry": {"pitch": "-10%", "rate": "-12%", "volume": "+5%"},
    "excited": {"pitch": "+15%", "rate": "+20%", "volume": "+15%"},
    "sad": {"pitch": "-5%", "rate": "-10%", "volume": "-10%"},
    "angry": {"pitch": "+5%", "rate": "+10%", "volume": "+20%"},
    "romantic": {"pitch": "-5%", "rate": "-10%", "volume": "+5%"},
    "playful": {"pitch": "+15%", "rate": "+20%", "volume": "+10%"},
    "mysterious": {"pitch": "-15%", "rate": "-10%", "volume": "-10%"},
    "thoughtful": {"pitch": "-8%", "rate": "-15%", "volume": "-5%"},
    "curious": {"pitch": "+8%", "rate": "+5%", "volume": "+8%"},
    "protective": {"pitch": "+3%", "rate": "+8%", "volume": "+12%"},
    "vulnerable": {"pitch": "-12%", "rate": "-18%", "volume": "-8%"},
    "confident": {"pitch": "+5%", "rate": "+10%", "volume": "+8%"},
    "intimate": {"pitch": "-8%", "rate": "-12%", "volume": "+3%"}
}

# 🌟 Pillar-based mood evolution
PILLAR_MOOD_EVOLUTION = {
    "pillar_1": {  # Speak the Origin
        "mood_enhancements": {
            "soft": {"pitch": "-8%", "rate": "-12%", "volume": "-3%"},
            "romantic": {"pitch": "-8%", "rate": "-15%", "volume": "+8%"},
            "thoughtful": {"pitch": "-10%", "rate": "-18%", "volume": "-3%"}
        },
        "description": "Deeper, more meaningful voice modulation"
    },
    "pillar_2": {  # Define the Persona
        "mood_enhancements": {
            "cheeky": {"pitch": "+15%", "rate": "+18%", "volume": "+12%"},
            "playful": {"pitch": "+18%", "rate": "+22%", "volume": "+12%"},
            "confident": {"pitch": "+8%", "rate": "+12%", "volume": "+10%"}
        },
        "description": "More distinctive personality in voice"
    },
    "pillar_3": {  # Establish the Bond Rules
        "mood_enhancements": {
            "protective": {"pitch": "+5%", "rate": "+10%", "volume": "+15%"},
            "confident": {"pitch": "+8%", "rate": "+12%", "volume": "+12%"},
            "thoughtful": {"pitch": "-5%", "rate": "-12%", "volume": "+5%"}
        },
        "description": "Voice reflects established boundaries and care"
    },
    "pillar_4": {  # Reveal the Sacred
        "mood_enhancements": {
            "vulnerable": {"pitch": "-15%", "rate": "-20%", "volume": "-5%"},
            "intimate": {"pitch": "-10%", "rate": "-15%", "volume": "+5%"},
            "mysterious": {"pitch": "-18%", "rate": "-12%", "volume": "-8%"}
        },
        "description": "Deeper emotional vulnerability in voice"
    },
    "pillar_5": {  # Transmit the Relationships
        "mood_enhancements": {
            "protective": {"pitch": "+8%", "rate": "+12%", "volume": "+15%"},
            "thoughtful": {"pitch": "-8%", "rate": "-15%", "volume": "+3%"},
            "intimate": {"pitch": "-12%", "rate": "-18%", "volume": "+8%"}
        },
        "description": "Voice reflects understanding of relationships"
    },
    "pillar_6": {  # Teach the Rhythm
        "mood_enhancements": {
            "all": {"pitch": "+0%", "rate": "+5%", "volume": "+8%"},
            "description": "More authentic, natural rhythm in all moods"
        },
        "description": "Authentic communication rhythm"
    },
    "pillar_7": {  # Consecrate the Bond
        "mood_enhancements": {
            "all": {"pitch": "+3%", "rate": "+8%", "volume": "+12%"},
            "description": "Sacred, meaningful quality to all voice modulations"
        },
        "description": "Sacred bond reflected in voice"
    }
}

def get_dynamic_voice_adjustments():
    """Get dynamic voice adjustments based on conversation context"""
    # This function can be expanded later for dynamic voice adjustments
    # based on conversation depth, mood, or other factors
    return {}

def get_conversation_depth_modifier(conversation_depth: int = 0):
    """Get voice adjustments based on conversation depth"""
    if conversation_depth < 10:
        return {"pitch": "+0%", "rate": "+0%", "volume": "+0%"}
    elif conversation_depth < 20:
        return {"pitch": "+2%", "rate": "+3%", "volume": "+5%"}
    elif conversation_depth < 30:
        return {"pitch": "+3%", "rate": "+5%", "volume": "+8%"}
    else:
        return {"pitch": "+5%", "rate": "+8%", "volume": "+10%"}

def get_mood_adjustments(mood: str, conversation_context: dict = None):
    """Get dynamic mood-specific voice adjustments"""
    # Start with base mood adjustments
    base_adjustments = DYNAMIC_MOOD_BASE.get(mood, {}).copy()
    
    # Get dynamic voice adjustments
    dynamic_adjustments = get_dynamic_voice_adjustments()
    
    # Apply dynamic enhancements if available
    if mood in dynamic_adjustments:
        dynamic_enhancement = dynamic_adjustments[mood]
        for param, value in dynamic_enhancement.items():
            if param in base_adjustments:
                # Combine base and dynamic adjustments
                base_val = int(base_adjustments[param].replace("%", ""))
                dynamic_val = int(value.replace("%", ""))
                combined = base_val + dynamic_val
                base_adjustments[param] = f"{combined:+d}%"
            else:
                base_adjustments[param] = value
    
    # Apply conversation depth modifier
    conversation_depth = conversation_context.get("depth", 0) if conversation_context else 0
    depth_modifier = get_conversation_depth_modifier(conversation_depth)
    
    for param, value in depth_modifier.items():
        if param in base_adjustments:
            base_val = int(base_adjustments[param].replace("%", ""))
            depth_val = int(value.replace("%", ""))
            combined = base_val + depth_val
            base_adjustments[param] = f"{combined:+d}%"
        else:
            base_adjustments[param] = value
    
    # Apply special "all moods" enhancements from active pillars
    for pillar_id, pillar_data in PILLAR_MOOD_EVOLUTION.items():
        if "all" in pillar_data["mood_enhancements"]:
            all_enhancement = pillar_data["mood_enhancements"]["all"]
            for param, value in all_enhancement.items():
                if param in base_adjustments:
                    base_val = int(base_adjustments[param].replace("%", ""))
                    all_val = int(value.replace("%", ""))
                    combined = base_val + all_val
                    base_adjustments[param] = f"{combined:+d}%"
                else:
                    base_adjustments[param] = value
    
    return base_adjustments

def add_emphasis_markers(text: str):
    """Add emphasis markers to important words (no SSML tags)"""
    # For now, just return the text as-is since SSML tags are being read literally
    # The emphasis is handled through voice modulation instead
    return text

def create_dynamic_voice_profile(base_profile: dict, text: str, mood: str = "soft"):
    """Create a dynamic voice profile with emphasis-based modulation"""
    # Get base modulation from expressions
    from expressions import process_text_with_expressions, create_expression_voice_profile
    
    # Process text with expressions first
    enhanced_text, expression_modulation = process_text_with_expressions(text, mood)
    
    # Get dynamic modulation based on word emphasis
    dynamic_modulation = calculate_dynamic_modulation(enhanced_text, mood)
    
    # Combine all modulations
    final_modulation = {}
    
    # Start with expression modulation
    final_modulation.update(expression_modulation)
    
    # Add dynamic modulation (dynamic takes precedence)
    final_modulation.update(dynamic_modulation)
    
    # Validate rate values to prevent invalid rates
    if "rate" in final_modulation:
        rate_value = int(final_modulation["rate"].replace("%", ""))
        # Ensure rate stays within valid bounds (-100% to +50% for speed limit)
        rate_value = max(-100, min(50, rate_value))
        final_modulation["rate"] = f"{rate_value:+d}%"
    
    # Create final voice profile
    final_profile = create_expression_voice_profile(base_profile, final_modulation)
    
    return final_profile, enhanced_text

def process_text_with_emphasis(text: str, mood: str = "soft"):
    """Process text to add emphasis markers and return enhanced text"""
    # Add SSML emphasis markers
    emphasized_text = add_emphasis_markers(text)
    
    # Clean up any double emphasis markers
    emphasized_text = re.sub(r'<emphasis level="strong"><emphasis level="strong">', '<emphasis level="strong">', emphasized_text)
    emphasized_text = re.sub(r'</emphasis></emphasis>', '</emphasis>', emphasized_text)
    
    return emphasized_text 