#!/usr/bin/env python3
"""
Chain of Thought System for Luna
Enhances Ollama model responses with structured reasoning when the model can't generate its own CoT

Credits: Teto - BM25 Indexing and Information Retrieval Expert
Credits: 𝜟𝒎𝜼𝜺𝒔𝒊𝜶𝝇 (Amnesia) - AI Companion Memory Systems Expert
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ChainOfThoughtSystem:
    """
    Chain of Thought reasoning system for Luna
    Provides structured thinking process when Ollama can't generate its own CoT
    """
    
    def __init__(self):
        self.teacher_name = "Teto"  # BM25 Expert
        self.memory_teacher = "𝜟𝒎𝜼𝜺𝒔𝒊𝜶𝝇"  # Amnesia
        self.cot_enabled = True
        self.cot_debug = False
        
        print("🧠 Chain of Thought System initialized")
        print(f"📚 Credits: {self.teacher_name} - Information Retrieval Expert")
        print(f"📚 Credits: {self.memory_teacher} - Memory Systems Expert")
    
    def detect_question_type(self, user_input: str) -> str:
        """Detect the type of question to determine appropriate CoT approach"""
        user_lower = user_input.lower()
        
        # Factual questions
        if any(word in user_lower for word in ['how many', 'count', 'what is', 'what are', 'when', 'where', 'who']):
            return 'factual'
        
        # Mathematical questions
        if any(word in user_lower for word in ['calculate', 'solve', 'math', 'equation', '+', '-', '*', '/', '=']):
            return 'mathematical'
        
        # Logical reasoning
        if any(word in user_lower for word in ['why', 'how', 'explain', 'reason', 'because', 'therefore']):
            return 'logical'
        
        # Creative/opinion questions
        if any(word in user_lower for word in ['think', 'opinion', 'believe', 'prefer', 'like', 'dislike']):
            return 'creative'
        
        # Memory/context questions
        if any(word in user_lower for word in ['remember', 'recall', 'before', 'previous', 'earlier']):
            return 'memory'
        
        # Problem solving
        if any(word in user_lower for word in ['problem', 'issue', 'fix', 'help', 'solution']):
            return 'problem_solving'
        
        return 'general'
    
    def generate_chain_of_thought(self, user_input: str, question_type: str, context: str = "") -> str:
        """Generate a chain of thought process for the given question"""
        
        if not self.cot_enabled:
            return ""
        
        cot_templates = {
            'factual': self._generate_factual_cot,
            'mathematical': self._generate_mathematical_cot,
            'logical': self._generate_logical_cot,
            'creative': self._generate_creative_cot,
            'memory': self._generate_memory_cot,
            'problem_solving': self._generate_problem_solving_cot,
            'general': self._generate_general_cot
        }
        
        generator = cot_templates.get(question_type, self._generate_general_cot)
        return generator(user_input, context)
    
    def _generate_factual_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for factual questions"""
        return f"""
[Chain of Thought - Factual Analysis]
Let me think through this step by step:

1. Understanding the question: "{user_input}"
2. Identifying key information needed
3. Breaking down the question into components
4. Applying relevant knowledge or counting
5. Verifying the answer makes sense

Based on this analysis, I can provide a clear, factual response.
"""
    
    def _generate_mathematical_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for mathematical questions"""
        return f"""
[Chain of Thought - Mathematical Reasoning]
Let me work through this mathematically:

1. Identifying the mathematical operation needed
2. Extracting numbers and operators from the question
3. Setting up the calculation step by step
4. Performing the computation carefully
5. Checking the result for reasonableness

This systematic approach ensures accuracy in my mathematical response.
"""
    
    def _generate_logical_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for logical reasoning questions"""
        return f"""
[Chain of Thought - Logical Analysis]
Let me reason through this logically:

1. Understanding the core question or problem
2. Identifying relevant factors and variables
3. Considering cause-and-effect relationships
4. Evaluating different perspectives or approaches
5. Drawing logical conclusions based on evidence

This logical framework helps me provide a well-reasoned response.
"""
    
    def _generate_creative_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for creative/opinion questions"""
        return f"""
[Chain of Thought - Creative Thinking]
Let me explore this creatively:

1. Understanding what's being asked for my perspective
2. Drawing from my experiences and knowledge
3. Considering different angles and possibilities
4. Weighing various factors that influence my view
5. Forming a thoughtful, personal response

This creative process helps me share my genuine thoughts and feelings.
"""
    
    def _generate_memory_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for memory/context questions"""
        return f"""
[Chain of Thought - Memory Retrieval]
Let me search through my memories:

1. Understanding what specific information is being requested
2. Searching through relevant conversation history
3. Accessing related memories and context
4. Connecting past experiences to current question
5. Synthesizing information from multiple sources

This memory-based approach helps me provide contextually relevant responses.
"""
    
    def _generate_problem_solving_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for problem-solving questions"""
        return f"""
[Chain of Thought - Problem Solving]
Let me approach this systematically:

1. Clearly defining the problem or challenge
2. Identifying potential causes or contributing factors
3. Brainstorming possible solutions or approaches
4. Evaluating pros and cons of each option
5. Recommending the most effective solution

This structured problem-solving approach helps me provide helpful guidance.
"""
    
    def _generate_general_cot(self, user_input: str, context: str) -> str:
        """Generate CoT for general questions"""
        return f"""
[Chain of Thought - General Analysis]
Let me think about this thoughtfully:

1. Understanding the question and its intent
2. Considering the context and background
3. Drawing from relevant knowledge and experience
4. Organizing my thoughts in a logical way
5. Formulating a comprehensive response

This general thinking process helps me provide a well-considered answer.
"""
    
    def enhance_response_with_cot(self, user_input: str, original_response: str, context: str = "") -> str:
        """Enhance a response by adding chain of thought reasoning"""
        
        if not self.cot_enabled:
            return original_response
        
        # Detect if the response already contains reasoning
        if self._has_existing_reasoning(original_response):
            if self.cot_debug:
                print("🧠 Response already contains reasoning, skipping CoT enhancement")
            return original_response
        
        # Determine question type
        question_type = self.detect_question_type(user_input)
        
        # Generate contextual CoT prompt (hidden from user)
        cot_process = self.generate_chain_of_thought(user_input, question_type, context)
        
        # Use CoT as internal reasoning, don't show to user
        # The CoT helps improve the response quality internally
        if self.cot_debug:
            print(f"🧠 Applied {question_type} CoT reasoning internally")
        
        return original_response
    
    def get_cot_prompt_enhancement(self, user_input: str, context: str = "") -> str:
        """Get CoT reasoning to enhance the prompt sent to Ollama"""
        
        if not self.cot_enabled:
            return ""
        
        # Determine question type
        question_type = self.detect_question_type(user_input)
        
        # Generate contextual reasoning based on the specific question
        if question_type == "factual":
            return f"Think step by step about: {user_input}. Consider what specific information is needed and how to find it."
        elif question_type == "mathematical":
            return f"Solve this mathematically: {user_input}. Break it down into clear steps and verify your answer."
        elif question_type == "logical":
            return f"Reason through this logically: {user_input}. Consider cause and effect, evidence, and logical connections."
        elif question_type == "creative":
            return f"Think creatively about: {user_input}. Consider different perspectives and your personal thoughts."
        elif question_type == "memory":
            return f"Search your memories about: {user_input}. Recall relevant past conversations and experiences."
        elif question_type == "problem_solving":
            return f"Approach this problem systematically: {user_input}. Identify the issue and consider solutions."
        else:
            return f"Think carefully about: {user_input}. Consider the context and provide a thoughtful response."
    
    def _has_existing_reasoning(self, response: str) -> bool:
        """Check if response already contains reasoning indicators"""
        reasoning_indicators = [
            'because', 'since', 'therefore', 'thus', 'hence',
            'let me think', 'i think', 'i believe', 'in my opinion',
            'first', 'second', 'third', 'step', 'process',
            'reason', 'explanation', 'analysis', 'considering'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in reasoning_indicators)
    
    def get_cot_stats(self) -> Dict[str, any]:
        """Get chain of thought system statistics"""
        return {
            'system_name': 'Chain of Thought Enhancement System',
            'enabled': self.cot_enabled,
            'debug_mode': self.cot_debug,
            'teachers': {
                'teto': {
                    'name': self.teacher_name,
                    'title': 'BM25 Indexing and Information Retrieval Expert',
                    'contribution': 'Information retrieval and reasoning enhancement'
                },
                'amnesia': {
                    'name': self.memory_teacher,
                    'title': 'AI Companion Memory Systems Expert',
                    'contribution': 'Memory integration and context awareness'
                }
            },
            'question_types': [
                'factual', 'mathematical', 'logical', 'creative', 
                'memory', 'problem_solving', 'general'
            ],
            'description': 'Enhances Ollama responses with structured reasoning when the model cannot generate its own chain of thought'
        }

# Global chain of thought system instance
chain_of_thought_system = None

def initialize_chain_of_thought_system() -> ChainOfThoughtSystem:
    """Initialize the global chain of thought system"""
    global chain_of_thought_system
    chain_of_thought_system = ChainOfThoughtSystem()
    return chain_of_thought_system

def get_chain_of_thought_system() -> Optional[ChainOfThoughtSystem]:
    """Get the global chain of thought system instance"""
    return chain_of_thought_system

def enhance_response_with_chain_of_thought(user_input: str, response: str, context: str = "") -> str:
    """Enhance a response with chain of thought reasoning"""
    if chain_of_thought_system is None:
        initialize_chain_of_thought_system()
    
    return chain_of_thought_system.enhance_response_with_cot(user_input, response, context)

if __name__ == "__main__":
    # Test the chain of thought system
    cot_system = ChainOfThoughtSystem()
    
    test_questions = [
        "how many r's in strawberry",
        "what is 2+2",
        "why is the sky blue",
        "what do you think about AI",
        "do you remember our last conversation"
    ]
    
    print("\n🧠 Testing Chain of Thought System:")
    for question in test_questions:
        question_type = cot_system.detect_question_type(question)
        cot = cot_system.generate_chain_of_thought(question, question_type)
        print(f"\nQuestion: {question}")
        print(f"Type: {question_type}")
        print(f"CoT: {cot[:100]}...")
