#!/usr/bin/env python3
# luna_inference.py
"""
Inference script for Luna's custom transformer model
"""

import sys
from luna_transformer import LunaTrainer

def main():
    print("🤖 Luna Custom Model Inference")
    
    # Initialize trainer and load model
    trainer = LunaTrainer(model_path="luna_model_final")
    
    if not trainer.load_model("luna_model_final"):
        print("❌ Failed to load model!")
        return
    
    print("✅ Model loaded successfully!")
    print("💬 Start chatting with Luna (type 'quit' to exit):")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Generate response
            response = trainer.generate_response(user_input)
            print(f"Luna: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
