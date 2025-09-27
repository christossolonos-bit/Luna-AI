# 🖥️ Luna Custom Model - Hardware Optimization Guide

## 📊 **Current Optimizations Applied**

### **Model Size Reduction:**
- **Vocab Size**: 50K → 8K (84% reduction)
- **Hidden Size**: 1024 → 256 (75% reduction)
- **Layers**: 24 → 6 (75% reduction)
- **Sequence Length**: 2048 → 256 (87% reduction)
- **Training Config**: 8 layers → 4 layers (50% reduction)

### **Memory Usage:**
- **Before**: ~50-100M parameters (4-8GB+ memory)
- **After**: ~1-2M parameters (500MB-1GB memory)
- **Reduction**: 95%+ memory savings

## ⚙️ **Training Optimizations**

### **Batch Processing:**
- **Batch Size**: 2 (very small for memory efficiency)
- **Gradient Accumulation**: 8 steps (simulates batch size of 16)
- **Memory Management**: Automatic cleanup after each batch

### **Sequence Truncation:**
- **Max Length**: 128 tokens (prevents memory overflow)
- **Automatic Truncation**: Long sequences are cut to fit

## 🚀 **Recommended Training Process**

### **Step 1: Initialize with Existing Knowledge**
```bash
# Click "🧠 Init Knowledge" button in GUI
# OR run:
python initialize_luna_model.py
```

### **Step 2: Monitor Training**
- **Training Time**: 5-15 minutes (vs 1-2 hours before)
- **Memory Usage**: ~500MB-1GB (vs 4-8GB before)
- **Progress**: Check "🧠 Training Status" button

### **Step 3: Force Training**
```bash
# Click "🔄 Force Train" button in GUI
# OR run:
python -c "from luna_daily_trainer import force_training; force_training()"
```

## 🔧 **Hardware Requirements**

### **Minimum Requirements:**
- **RAM**: 4GB (2GB free)
- **Storage**: 1GB free space
- **CPU**: Any modern CPU (2+ cores)
- **GPU**: Optional (will use CPU if no GPU)

### **Recommended:**
- **RAM**: 8GB (4GB free)
- **Storage**: 2GB free space
- **CPU**: 4+ cores
- **GPU**: Any CUDA-capable GPU (2GB+ VRAM)

## 📈 **Performance Expectations**

### **Training Speed:**
- **CPU Only**: 10-20 minutes for 100 epochs
- **With GPU**: 5-10 minutes for 100 epochs
- **Memory Usage**: 500MB-1GB peak

### **Model Quality:**
- **Smaller but focused**: Trained specifically on your conversations
- **Fast inference**: Quick response generation
- **Personality preservation**: Maintains Luna's unique voice

## 🛠️ **Troubleshooting**

### **If Training is Still Slow:**
1. **Reduce epochs**: Change `epochs_per_day = 50` in `luna_daily_trainer.py`
2. **Smaller batches**: Change `batch_size=1` in training calls
3. **Close other apps**: Free up RAM

### **If Out of Memory:**
1. **Restart Luna**: Close and reopen the application
2. **Clear cache**: Delete `luna_model.pt` and retrain
3. **Reduce vocab**: Change `vocab_size=4000` in `ModelConfig`

### **If Training Fails:**
1. **Check logs**: Look for error messages in terminal
2. **Verify data**: Ensure `luna_memories.db` exists
3. **Reinstall PyTorch**: `pip install torch --upgrade`

## 🎯 **Best Practices**

### **For Optimal Performance:**
1. **Train during off-hours**: Use the 5 AM Cyprus time schedule
2. **Monitor resources**: Keep Task Manager open during training
3. **Regular backups**: Save `luna_model.pt` before major updates
4. **Incremental training**: Let daily training build up gradually

### **For Quality Results:**
1. **Quality conversations**: Focus on meaningful interactions
2. **Consistent personality**: Luna learns from your chat style
3. **Patience**: Let the model train over several days
4. **Feedback**: Adjust based on Luna's responses

## 🔄 **Daily Training Schedule**

### **Automatic Training:**
- **Time**: 5:00 AM Cyprus time (UTC+3)
- **Frequency**: Once per day
- **Duration**: 5-15 minutes
- **Background**: Runs while you sleep

### **Manual Training:**
- **Trigger**: "🔄 Force Train" button
- **Use case**: Testing or immediate updates
- **Frequency**: As needed

## 📊 **Monitoring Tools**

### **GUI Buttons:**
- **🧠 Training Status**: Shows current training data and progress
- **🧠 Init Knowledge**: Imports existing conversations
- **🔄 Force Train**: Triggers immediate training

### **Log Files:**
- **Training Log**: `training_log.json`
- **Training Data**: `luna_training_data.json`
- **Model File**: `luna_model.pt`

## 🎉 **Success Indicators**

### **When Training Works:**
- ✅ Model file created (`luna_model.pt`)
- ✅ Training logs show completion
- ✅ Luna responds with custom model
- ✅ Memory usage stays under 1GB
- ✅ Training completes in <15 minutes

### **Quality Metrics:**
- **Response Speed**: <2 seconds
- **Personality**: Maintains Luna's voice
- **Relevance**: Contextually appropriate responses
- **Creativity**: Original and engaging content

---

**💡 Tip**: The optimized model is designed to be lightweight but effective. It focuses on learning your specific conversation patterns and Luna's personality rather than general knowledge, making it both fast and personalized.
