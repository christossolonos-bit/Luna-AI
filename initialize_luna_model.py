#!/usr/bin/env python3
"""
Initialize Luna's Custom Model
This script manually initializes Luna's custom transformer model with existing conversations
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main initialization function"""
    logger.info("🧠 Starting Luna's Custom Model Initialization...")
    
    try:
        # Import the daily trainer
        from luna_daily_trainer import initialize_daily_trainer, initialize_with_existing_knowledge, force_training
        
        # Initialize the daily trainer
        logger.info("📊 Initializing daily trainer...")
        trainer = initialize_daily_trainer()
        
        # Initialize with existing knowledge
        logger.info("🔄 Importing existing conversations...")
        success = initialize_with_existing_knowledge()
        
        if success:
            logger.info("✅ Successfully imported existing conversations!")
            
            # Force training
            logger.info("🔄 Starting forced training...")
            force_training()
            
            logger.info("✅ Luna's custom model initialization completed!")
            logger.info("🎉 Luna is now ready to use her custom transformer model!")
            
        else:
            logger.warning("⚠️ Limited existing conversations found")
            logger.info("🔄 Starting training with personality data only...")
            force_training()
            
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Luna's custom model is ready!")
        print("You can now chat with Luna and she'll use her custom transformer model.")
    else:
        print("\n❌ Initialization failed. Check the logs above for details.")
        sys.exit(1)
