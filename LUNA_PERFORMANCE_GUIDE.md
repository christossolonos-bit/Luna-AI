# 🚀 Luna Performance Guide

## Why Luna Uses High CPU

Luna's high CPU usage is caused by several **background processes** that run continuously:

### **🔥 High CPU Processes**

1. **Background Thinking Loop** (Every 5-10 minutes)
   - Generates autonomous thoughts using Ollama
   - **NEW**: Includes vector reasoning and curiosity cycles
   - Uses significant CPU for AI processing

2. **Self-Reflection Loop** (Every 30-60 minutes)
   - Deep introspection using Ollama
   - Analyzes Luna's own behavior and growth
   - Heavy AI processing

3. **Knowledge Exploration Loop** (Every 1-2 hours)
   - Explores new topics using understanding engine
   - Uses concept mapping and reasoning
   - CPU-intensive AI operations

4. **Vector Reasoning & Curiosity Engine** (NEW)
   - Real-time vector embeddings generation
   - Semantic similarity calculations
   - Autonomous curiosity exploration

## 🛠️ **Solutions to Reduce CPU Usage**

### **1. Use Performance Mode**
```bash
# Tell Luna to enable performance mode
"performance mode"
```

This will:
- Reduce background thinking frequency (10-20 minutes)
- Reduce self-reflection frequency (1-2 hours)
- Disable knowledge exploration
- Reduce curiosity engine frequency
- **Significantly lower CPU usage**

### **2. Monitor Performance**
```bash
# Check current performance settings
"performance stats"
```

### **3. Restore Full Features**
```bash
# Re-enable all AI features (higher CPU usage)
"full cognitive mode"
```

## 📊 **Performance Modes**

### **🚀 Performance Mode** (Low CPU)
- Background thinking: 10-20 minutes
- Self-reflection: 1-2 hours
- Knowledge exploration: Disabled
- Curiosity engine: Reduced frequency
- **CPU Usage**: ~20-30% lower

### **🧠 Full Cognitive Mode** (High CPU)
- Background thinking: 5-10 minutes
- Self-reflection: 30-60 minutes
- Knowledge exploration: 1-2 hours
- Curiosity engine: Normal frequency
- **CPU Usage**: Full AI capabilities

## 🔧 **Manual Optimizations**

### **Disable Specific Features**
You can manually disable features by modifying `luna_clean.py`:

```python
# In _start_background_activities(), comment out:
# threading.Thread(target=self._knowledge_exploration_loop, daemon=True).start()
```

### **Increase Sleep Intervals**
Modify the sleep times in background loops:

```python
# In _background_thinking_loop():
wait_time = random.randint(600, 1200)  # 10-20 minutes (was 5-10)

# In _self_reflection_loop():
wait_time = random.randint(3600, 7200)  # 1-2 hours (was 30-60)
```

## 🎯 **Recommended Settings**

### **For Low-End PCs**
```bash
"performance mode"
```

### **For High-End PCs**
```bash
"full cognitive mode"
```

### **For Balanced Performance**
- Use default settings (already optimized)
- Monitor with `"performance stats"`
- Switch modes as needed

## 🔍 **Troubleshooting**

### **If CPU Usage is Still High**
1. Check if Ollama is running efficiently
2. Ensure you have sufficient RAM (8GB+ recommended)
3. Close other resource-intensive applications
4. Use `"performance mode"` for immediate relief

### **If Luna Becomes Less Intelligent**
1. Use `"full cognitive mode"` to restore features
2. Check that all systems are active with `"performance stats"`
3. Restart Luna if needed

## 📈 **Performance Monitoring**

### **Check System Status**
```bash
"performance stats"
```

Shows:
- Background process status
- Memory usage statistics
- Understanding system stats
- Active AI features

### **Memory Management**
Luna automatically:
- Prunes weak memories
- Optimizes database queries
- Caches frequently used data
- Manages vector embeddings efficiently

## 🎉 **The Result**

With these optimizations, Luna should:
- **Use 20-30% less CPU** in performance mode
- **Maintain intelligence** while being more efficient
- **Allow you to choose** between performance and features
- **Run smoothly** on most systems

The key is finding the right balance between Luna's intelligence and your system's performance! 🧠✨
