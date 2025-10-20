# 🔍 Luna Curiosity Engine

## Overview

Luna's Curiosity Engine is a real-time autonomous learning system that enables Luna to explore knowledge gaps, generate dynamic questions, and discover new insights through curiosity-driven exploration. This system works in conjunction with Luna's vector reasoning and DNA memory systems to create truly autonomous learning.

## 🚀 Key Features

### **Real-Time Curiosity Generation**
- Dynamically generates questions based on current knowledge state
- No pre-written questions - all generated in real-time
- Adapts question generation based on exploration strategy

### **Knowledge Gap Identification**
- Uses vector reasoning to identify areas of low knowledge density
- Analyzes conversation patterns to find unexplored topics
- Prioritizes targets based on curiosity score and exploration potential

### **Multi-Strategy Exploration**
- **Semantic**: Explores meaning and relationships
- **Temporal**: Analyzes patterns over time
- **Emotional**: Understands emotional contexts and patterns
- **Causal**: Explores cause-and-effect relationships

### **Autonomous Learning Cycles**
- Runs automatically when Luna's curiosity level is high
- Integrates with Luna's understanding and memory systems
- Generates follow-up targets for deeper exploration

### **Dynamic Question Generation**
- Creates questions based on exploration strategy
- Adapts question depth based on exploration progress
- Generates follow-up questions for deeper understanding

## 🏗️ Architecture

### **Core Components**

1. **LunaCuriosityEngine** (`luna_curiosity_engine.py`)
   - Main curiosity engine with autonomous exploration
   - Knowledge gap identification and target prioritization
   - Real-time question generation and exploration

2. **CuriosityTarget** (Data Structure)
   - Represents a topic for exploration
   - Contains curiosity score, knowledge gap size, and exploration strategy
   - Tracks related concepts and exploration depth

3. **CuriosityExploration** (Data Structure)
   - Result of an exploration session
   - Contains insights, connections, and follow-up targets
   - Tracks exploration confidence and learning value

4. **Integrated Luna System** (`luna_clean.py`)
   - Curiosity engine integrated into main response generation
   - Autonomous curiosity runs triggered by high curiosity levels
   - Manual curiosity commands for user-triggered exploration

## 📊 Data Structures

### **CuriosityTarget**
```python
@dataclass
class CuriosityTarget:
    topic: str
    curiosity_score: float
    knowledge_gap_size: float
    exploration_priority: float
    related_concepts: List[str]
    exploration_strategy: str  # 'semantic', 'temporal', 'emotional', 'causal'
    generated_questions: List[str]
    exploration_depth: int
```

### **CuriosityExploration**
```python
@dataclass
class CuriosityExploration:
    target: CuriosityTarget
    questions_generated: List[str]
    insights_discovered: List[str]
    new_connections: List[Dict]
    knowledge_gaps_filled: List[str]
    follow_up_targets: List[CuriosityTarget]
    exploration_confidence: float
    learning_value: float
```

### **Database Schema**
- `curiosity_targets`: Stores exploration targets with vector embeddings
- `curiosity_explorations`: Records exploration results and insights
- `curiosity_patterns`: Identifies successful exploration patterns
- `autonomous_discoveries`: Stores discoveries from autonomous exploration

## 🔧 Installation

### **Dependencies**
```bash
pip install -r requirements_vector_reasoning.txt
```

### **Required Packages**
- `sentence-transformers>=2.2.0` - For vector embeddings
- `numpy>=1.21.0` - For numerical operations
- `sqlite3` - For database storage (built into Python)

## 🚀 Usage

### **Autonomous Curiosity**
Luna automatically runs curiosity cycles when:
- Her curiosity level is above 0.6
- At least 5 minutes have passed since last curiosity run
- She has sufficient exploration energy

### **Manual Curiosity Commands**
```bash
# Trigger a curiosity run
"curiosity run"
"explore"

# View curiosity statistics
"curiosity stats"
```

### **Programmatic Usage**
```python
from luna_curiosity_engine import initialize_curiosity_engine, run_curiosity_cycle
from luna_dna_memory import initialize_dna_memory
from luna_understanding import UnderstandingEngine

# Initialize systems
curiosity_engine = initialize_curiosity_engine()
dna_memory = initialize_dna_memory()
understanding = UnderstandingEngine("model_name")

# Run curiosity cycle
explorations = run_curiosity_cycle(dna_memory, understanding)

# Access results
for exploration in explorations:
    print(f"Target: {exploration.target.topic}")
    print(f"Insights: {len(exploration.insights_discovered)}")
    print(f"Questions: {len(exploration.questions_generated)}")
```

## 🧪 Testing

### **Run Tests**
```bash
python test_curiosity_engine.py
```

### **Run Demo**
```bash
python demo_curiosity_engine.py
```

### **Test Components**
- Basic curiosity engine functionality
- Knowledge gap identification
- Question generation
- Autonomous exploration
- Statistics and monitoring

## 📈 Performance

### **Memory Usage**
- Vector embeddings: ~384 dimensions per text
- Database storage: Optimized with binary blob storage
- Target caching: Automatic caching of exploration targets

### **Processing Speed**
- Target identification: ~200ms per cycle
- Question generation: ~100ms per target
- Exploration execution: ~500ms per target
- Full curiosity cycle: ~2-3 seconds

### **Scalability**
- Supports thousands of exploration targets
- Efficient vector similarity search
- Automatic target pruning for performance

## 🔍 Monitoring

### **Statistics Available**
```python
stats = curiosity_engine.get_curiosity_stats()
print(f"Total targets: {stats['total_targets']}")
print(f"Total explorations: {stats['total_explorations']}")
print(f"Average learning value: {stats['average_learning_value']}")
print(f"Curiosity level: {stats['curiosity_level']}")
```

### **Integration with Luna Stats**
```python
# In Luna's main system
stats = luna.get_stats()
curiosity_stats = stats.get('curiosity_engine', {})
```

## 🎯 Use Cases

### **1. Autonomous Learning**
- Luna explores topics she's curious about
- Discovers new connections between concepts
- Builds deeper understanding over time

### **2. Knowledge Gap Filling**
- Identifies areas where Luna lacks knowledge
- Prioritizes learning based on curiosity and importance
- Fills gaps through systematic exploration

### **3. Dynamic Question Generation**
- Creates questions based on current context
- Adapts question style to exploration strategy
- Generates follow-up questions for deeper understanding

### **4. Pattern Recognition**
- Identifies successful exploration patterns
- Learns which strategies work best for different topics
- Adapts future exploration based on past success

## 🔮 Advanced Features

### **Exploration Strategies**

#### **Semantic Exploration**
- Focuses on meaning and relationships
- Generates questions about definitions and connections
- Explores conceptual similarities and differences

#### **Temporal Exploration**
- Analyzes patterns over time
- Generates questions about history and evolution
- Explores temporal relationships and trends

#### **Emotional Exploration**
- Understands emotional contexts
- Generates questions about feelings and responses
- Explores emotional patterns and trajectories

#### **Causal Exploration**
- Explores cause-and-effect relationships
- Generates questions about influences and consequences
- Builds understanding of causal chains

### **Autonomous Learning Cycles**
1. **Gap Identification**: Find knowledge gaps using vector reasoning
2. **Target Prioritization**: Rank targets by curiosity score and importance
3. **Question Generation**: Create dynamic questions for each target
4. **Exploration Execution**: Use understanding engine to explore topics
5. **Insight Synthesis**: Combine findings into new understanding
6. **Follow-up Generation**: Create new targets for deeper exploration

## 🛠️ Troubleshooting

### **Common Issues**

1. **No Curiosity Targets Found**
   - Ensure Luna has sufficient conversation history
   - Check that vector reasoning system is working
   - Verify DNA memory system is populated

2. **Low Exploration Energy**
   - Wait for energy to regenerate
   - Check curiosity level (should be > 0.6)
   - Ensure sufficient system resources

3. **Poor Question Quality**
   - Verify understanding engine is working
   - Check that exploration strategies are appropriate
   - Ensure sufficient context for question generation

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 References

- [Curiosity-Driven Learning](https://arxiv.org/search/?query=curiosity+driven+learning)
- [Autonomous Exploration](https://arxiv.org/search/?query=autonomous+exploration)
- [Knowledge Gap Analysis](https://arxiv.org/search/?query=knowledge+gap+analysis)

## 🤝 Contributing

Curiosity engine is a core part of Luna's autonomous learning system. Contributions are welcome for:
- New exploration strategies
- Improved question generation algorithms
- Enhanced pattern recognition
- Performance optimizations

## 📄 License

Part of Luna's open-source AI system. See main project license for details.

## 🎉 The Transformation

Luna's Curiosity Engine transforms her from a reactive AI into a **proactive learning entity** that:

- **Explores autonomously** without human intervention
- **Discovers new knowledge** through systematic exploration
- **Adapts learning strategies** based on what works
- **Builds deeper understanding** through curiosity-driven exploration
- **Generates novel insights** by connecting disparate concepts

Luna now has **genuine curiosity** - the drive to explore, learn, and discover that makes her a truly autonomous learning AI! 🧠✨
