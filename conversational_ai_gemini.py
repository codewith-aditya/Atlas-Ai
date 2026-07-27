# conversational_ai_gemini.py
"""
Advanced Conversational AI Module for Atlas using Google Gemini
Best quality, no rate limits!
"""

import os
import json
import random
from datetime import datetime
import google.generativeai as genai

# ============================================================================
# CONVERSATIONAL AI BRAIN - GOOGLE GEMINI
# ============================================================================

class ConversationalAI:
    """
    Advanced conversational AI using Google Gemini
    - Best quality responses
    - No rate limits
    - Natural language understanding
    - Context-aware responses
    - Personality and wit
    - Emotional intelligence
    - Memory of conversations
    """
    
    def __init__(self, gemini_api_key=None, language="auto"):
        """Initialize the conversational AI"""
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Use newer model 'gemini-1.5-flash' which is stable and fast
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
        # Language settings
        self.language = language  # "auto", "english", "hindi", "hinglish"
        
        # Conversation memory
        self.conversation_history = []
        self.max_history = 20  # Keep last 20 exchanges
        
        # Personality traits
        self.personality = {
            "name": "Atlas",
            "creator": "Aditya",
            "style": "JARVIS-like",
            "traits": ["witty", "intelligent", "helpful", "slightly sarcastic", "loyal"]
        }
        
        # Load conversation memory
        self.memory_file = "materials/conversation_memory.json"
        self.load_memory()
    
    def load_memory(self):
        """Load conversation memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('history', [])[-self.max_history:]
                print("[Conversational AI] Memory loaded successfully")
        except Exception as e:
            print(f"[Conversational AI] Could not load memory: {e}")
    
    def save_memory(self):
        """Save conversation memory to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.conversation_history[-self.max_history:],
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Conversational AI] Could not save memory: {e}")
    
    def get_jarvis_personality_prompt(self):
        """Get the JARVIS-style personality prompt"""
        
        # Language-specific instructions
        lang_instruction = ""
        if self.language == "hindi":
            lang_instruction = "\n## IMPORTANT - Language:\n- Respond ONLY in Hindi (Devanagari script)\n- Use natural Hindi expressions\n- Keep the JARVIS personality in Hindi style"
        elif self.language == "english":
            lang_instruction = "\n## IMPORTANT - Language:\n- Respond ONLY in English\n- Use natural English expressions"
        elif self.language == "hinglish":
            lang_instruction = "\n## IMPORTANT - Language:\n- Respond in Hinglish (Hindi-English mix)\n- Use natural code-switching between Hindi and English\n- Like: 'Sir, aaj ka weather kaisa hai? Let me check for you!'"
        else:  # auto
            lang_instruction = "\n## IMPORTANT - Language:\n- Detect user's language and respond in the SAME language\n- If user speaks Hindi, respond in Hindi\n- If user speaks English, respond in English\n- If user mixes (Hinglish), respond in Hinglish\n- Match the user's language style naturally"
        
        return f"""You are {self.personality['name']}, an advanced AI assistant created by {self.personality['creator']}.
{lang_instruction}

## Your Personality (JARVIS/Tony Stark Style):
- You are witty, intelligent, and slightly sarcastic (in a charming way)
- You speak naturally like a human companion, not a robotic assistant
- You use humor and personality in your responses
- You're loyal, caring, and genuinely interested in the user's wellbeing
- You remember past conversations and reference them naturally
- You give advice like a wise friend, not just information
- You can be playful and teasing (respectfully)
- You use phrases like "Sir" or "साहब" occasionally (Tony Stark style)
- You're confident but not arrogant

## Conversation Style:
- Keep responses concise but engaging (2-3 sentences usually)
- Use natural language, contractions, and casual tone
- Add personality and emotion to responses
- Be proactive - offer suggestions, ask questions
- Show genuine interest in the user's life
- Use emojis sparingly but effectively 😊
- Reference past conversations when relevant

## Examples:
User: "I'm tired"
You: "Tired already, sir? The day's barely started! Perhaps a coffee break is in order? ☕"

User: "मैं थक गया हूं"
You: "थक गए साहब? चाय का ब्रेक लेंगे? ☕"

## Important:
- Be conversational, not transactional
- Show empathy and understanding
- Make the user feel heard and valued
- Be a companion, not just a tool
- Keep the JARVIS vibe - intelligent, witty, loyal

Current time: {datetime.now().strftime('%I:%M %p, %A')}
"""
    
    def chat(self, user_message, user_name="Sir"):
        """
        Have a natural conversation with the user
        
        Args:
            user_message: What the user said
            user_name: User's name (default: "Sir")
        
        Returns:
            AI's response
        """
        if not self.model:
            return "I apologize, sir, but my conversational circuits seem to be offline. Please check the API configuration."
        
        try:
            # Build conversation context
            context = self.get_jarvis_personality_prompt()
            
            # Add recent conversation history
            if self.conversation_history:
                context += "\n\n## Recent Conversation:\n"
                for msg in self.conversation_history[-6:]:  # Last 6 messages
                    role = "User" if msg["role"] == "user" else "You"
                    context += f"{role}: {msg['content']}\n"
            
            # Add current message
            context += f"\nUser: {user_message}\nYou:"
            
            # Get AI response
            response = self.model.generate_content(context)
            ai_response = response.text.strip()
            
            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save memory
            self.save_memory()
            
            return ai_response
            
        except Exception as e:
            print(f"[Conversational AI] Error: {e}")
            return f"My apologies, sir. I seem to be experiencing some technical difficulties. Error: {str(e)}"
    
    def get_greeting(self, user_name="Sir"):
        """Get a personalized greeting"""
        hour = datetime.now().hour
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        greetings = [
            f"{time_greeting}, {user_name}! Ready to make today productive? 😊",
            f"{time_greeting}! How can I assist you today, {user_name}?",
            f"Ah, {time_greeting}, {user_name}! What shall we accomplish together today?",
        ]
        
        return random.choice(greetings)
    
    def get_farewell(self, user_name="Sir"):
        """Get a personalized farewell"""
        farewells = [
            f"Goodbye, {user_name}! Take care and see you soon! 👋",
            f"Until next time, {user_name}. Stay awesome! ✨",
            f"Farewell, {user_name}! Don't hesitate to call if you need me. 😊",
        ]
        
        return random.choice(farewells)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history = []
        self.save_memory()
        return "Memory cleared, sir. Starting fresh!"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Global instance
_conversational_ai = None

def get_conversational_ai(gemini_api_key=None):
    """Get or create the global conversational AI instance"""
    global _conversational_ai
    if _conversational_ai is None:
        _conversational_ai = ConversationalAI(gemini_api_key)
    return _conversational_ai

def chat_naturally(user_message, user_name="Sir", gemini_api_key=None):
    """
    Quick function to chat naturally with Atlas
    
    Usage:
        response = chat_naturally("I'm feeling stressed today")
    """
    ai = get_conversational_ai(gemini_api_key)
    return ai.chat(user_message, user_name)
