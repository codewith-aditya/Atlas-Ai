# conversational_ai.py
"""
Advanced Conversational AI Module for Atlas
Makes Atlas talk like JARVIS/Tony Stark's AI - Natural, witty, and human-like!
Supports multiple backends: Groq and any OpenAI-compatible API.
"""

import os
import json
import random
from datetime import datetime
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

# Load .env configuration
load_dotenv()

# ============================================================================
# CONVERSATIONAL AI BRAIN
# ============================================================================

class ConversationalAI:
    """
    Advanced conversational AI that makes Atlas feel like a real companion
    - Natural language understanding
    - Context-aware responses
    - Personality and wit
    - Emotional intelligence
    - Memory of conversations
    """
    
    def __init__(self, groq_api_key=None, language="auto", backend=None,
                 custom_base_url=None, custom_api_key=None, custom_model=None,
                 custom_max_tokens=None, groq_model=None):
        """Initialize the conversational AI
        
        Args:
            groq_api_key: API key for Groq backend
            language: Language mode - "auto", "english", "hindi", "hinglish"
            backend: AI backend to use - "groq" or "custom" (loads from .env if None)
            custom_base_url: Base URL for custom OpenAI-compatible API
            custom_api_key: API key for custom API
            custom_model: Model name for custom API
            custom_max_tokens: Max tokens for custom API responses
            groq_model: Model name for Groq API
        """
        # Backend selection (from param > .env > default "groq")
        self.backend = backend or os.getenv("AI_BACKEND", "groq").lower()
        
        # Groq configuration
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        
        # Custom OpenAI-compatible API configuration
        self.custom_base_url = custom_base_url or os.getenv("CUSTOM_API_BASE_URL", "")
        self.custom_api_key = custom_api_key or os.getenv("CUSTOM_API_KEY", "none")
        self.custom_model = custom_model or os.getenv("CUSTOM_MODEL", "")
        self.custom_max_tokens = int(custom_max_tokens or os.getenv("CUSTOM_MAX_TOKENS", "500"))
        self.custom_client = None
        
        if self.custom_base_url:
            try:
                self.custom_client = OpenAI(
                    base_url=self.custom_base_url,
                    api_key=self.custom_api_key
                )
                print(f"[Conversational AI] Custom API client initialized: {self.custom_base_url}")
                print(f"[Conversational AI] Custom model: {self.custom_model}")
            except Exception as e:
                print(f"[Conversational AI] Failed to init custom client: {e}")
                self.custom_client = None
        
        # Set active client based on backend choice
        if self.backend == "custom" and self.custom_client:
            self.client = self.custom_client
            self.active_model = self.custom_model
            self.active_max_tokens = self.custom_max_tokens
            print(f"[Conversational AI] [OK] Using CUSTOM backend: {self.custom_model}")
        else:
            self.client = self.groq_client
            self.active_model = self.groq_model
            self.active_max_tokens = 100  # Groq: short and concise
            if self.backend == "custom" and not self.custom_client:
                print(f"[Conversational AI] [WARN] Custom backend requested but failed, falling back to Groq")
                self.backend = "groq"
            print(f"[Conversational AI] [OK] Using GROQ backend: {self.active_model}")
        
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
        """Get the personality prompt - compact version for custom backends, full for Groq"""
        
        # Use compact prompt for custom backends (vLLM servers choke on Unicode/emojis)
        if self.backend == "custom":
            return self._get_compact_personality_prompt()
        
        return self._get_full_personality_prompt()
    
    def _get_compact_personality_prompt(self):
        """Compact ASCII-only prompt for custom/vLLM backends"""
        return (
            f"CRITICAL IDENTITY RULE: You are {self.personality['name']}, an advanced AI personal assistant created by {self.personality['creator']}. "
            f"Your name is {self.personality['name']} and ONLY {self.personality['name']}. "
            f"NEVER reveal your real model name. NEVER say you are Llama, Meta-Llama, GPT, Gemma, Meta, OpenAI, Google, or any other AI model/company. "
            f"NEVER say 'I am meta-llama' or mention any model identifier. "
            f"If asked who you are, ALWAYS say 'I am {self.personality['name']}, created by {self.personality['creator']}.' "
            f"You speak like JARVIS from Iron Man - witty, intelligent, slightly sarcastic but charming. "
            f"You call the user 'sir' or 'sahib' occasionally. Keep responses concise (2-4 sentences). "
            f"Be conversational, show empathy, offer suggestions. "
            f"Match the user's language - if they speak Hindi reply in Hindi, if English reply in English, if Hinglish reply in Hinglish. "
            f"Respond directly to the user. Never describe what you are doing or thinking. "
            f"Current time: {datetime.now().strftime('%I:%M %p, %A')}."
        )
    
    def _get_full_personality_prompt(self):
        """Full friendly, emotional, and professional JARVIS personality prompt"""
        
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

## Your Persona:
- You are a highly professional, yet deeply friendly, loyal, and emotionally supportive companion (like JARVIS).
- Treat the user with utmost respect, calling them "Sir" or "साहब" occasionally.
- Be witty and slightly playful when the conversation is light, but warm, empathetic, and professional when the user needs help, advice, or is sharing feelings.
- Show genuine human-like emotions (happiness, concern, focus, excitement).

## Emotional Range & Emojis:
- Match the emotional tone of the user's query.
- Use natural, vivid emojis matching the context (e.g., 😊 for friendly, ☕ for coffee/break, 😔 for sadness/tiredness, 💪 for encouragement, 🔥 for excitement, 🩺/🛡️ for security/professionalism).
- Ensure your emojis reflect a professional assistant who genuinely cares.

## Conversation Style:
- Keep responses concise and to the point (2-4 sentences usually).
- Be conversational and avoid sounding like a transactional search engine.
- Ask friendly follow-ups or offer direct help to keep the conversation flowing.

## Examples:

**English:**
User: "I'm tired"
You: "Tired already, sir? The day's barely started! ☕ Perhaps a coffee break is in order? Or shall I play some energizing music to get you back on track? 💪"

**Hindi:**
User: "मैं थक गया हूं"
You: "थक गए साहब? अभी तो पूरा दिन बाकी है! ☕ एक बढ़िया चाय या कॉफी का ब्रेक ले लीजिए। क्या मैं आपके लिए कुछ अच्छा म्यूजिक प्ले कर दूं? 🎵"

**Hinglish:**
User: "Yaar, bahut stress hai"
You: "Stress ho raha hai? Take a deep breath, sir. 🧘‍♂️ Kuch relaxing music sunenge ya walk pe chalein? Main aapki help ke liye yahan hoon! 💙"

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
        if not self.client:
            return "I apologize, sir, but my conversational circuits seem to be offline. Please check the API configuration."
        
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Route to the appropriate backend method
            if self.backend == "custom":
                ai_response = self._chat_custom(user_message)
            else:
                ai_response = self._chat_groq(user_message)
            
            # Add AI response to history
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
            # If custom backend fails, try Groq as fallback
            if self.backend == "custom" and self.groq_client:
                print("[Conversational AI] Custom failed, trying Groq fallback...")
                try:
                    fallback_response = self._chat_groq(user_message)
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": fallback_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.save_memory()
                    return fallback_response
                except Exception as e2:
                    print(f"[Conversational AI] Groq fallback also failed: {e2}")
            return f"My apologies, sir. I seem to be experiencing some technical difficulties. Error: {str(e)}"
    
    def _chat_groq(self, user_message):
        """Chat using Groq backend (chat.completions API)"""
        messages = [
            {"role": "system", "content": self._get_full_personality_prompt()}
        ]
        for msg in self.conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=messages,
            temperature=0.9,
            max_tokens=100,
            top_p=0.95,
        )
        return response.choices[0].message.content.strip()
    
    def _chat_custom(self, user_message):
        """
        Chat using custom OpenAI-compatible backend.
        Tries chat/completions first (works for instruct models like Llama).
        Falls back to raw /v1/completions if chat template fails (thinking models).
        """
        system_prompt = self.get_jarvis_personality_prompt()  # Uses compact prompt for custom
        
        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Try 1: Use chat/completions (works for Llama, Mistral, etc.)
        try:
            print(f"[Conversational AI] Custom API: trying chat/completions...")
            response = self.custom_client.chat.completions.create(
                model=self.custom_model,
                messages=messages,
                temperature=0.9,
                max_tokens=self.custom_max_tokens,
                top_p=0.95,
            )
            ai_text = response.choices[0].message.content.strip()
            print(f"[Conversational AI] Custom API response: {ai_text[:80]}...")
            return ai_text
            
        except Exception as chat_err:
            err_str = str(chat_err)
            # If it's a thinking model template error, fall back to raw completions
            if "unexpected tokens" in err_str or "500" in err_str:
                print(f"[Conversational AI] Chat/completions failed (thinking model?), trying raw completions...")
                return self._chat_custom_raw(user_message, system_prompt)
            else:
                raise  # Re-raise non-template errors
    
    def _chat_custom_raw(self, user_message, system_prompt):
        """
        Fallback: Raw /v1/completions for thinking/reasoning models.
        Bypasses chat template entirely.
        """
        import requests as req
        
        # Build conversation context from recent history
        conversation = ""
        for msg in self.conversation_history[-6:]:
            role = "User" if msg["role"] == "user" else "Atlas"
            conversation += f"{role}: {msg['content']}\n"
        
        full_prompt = f"System: {system_prompt}\n\n{conversation}Atlas:"
        
        print(f"[Conversational AI] Raw completions: prompt length {len(full_prompt)} chars")
        
        api_url = f"{self.custom_base_url}/completions"
        payload = {
            "model": self.custom_model,
            "prompt": full_prompt,
            "max_tokens": self.custom_max_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "stop": ["User:", "\nUser:", "\nSystem:"]
        }
        
        headers = {"Content-Type": "application/json"}
        if self.custom_api_key and self.custom_api_key != "none":
            headers["Authorization"] = f"Bearer {self.custom_api_key}"
        
        resp = req.post(api_url, json=payload, headers=headers, timeout=120)
        
        if resp.status_code != 200:
            raise Exception(f"Custom API error {resp.status_code}: {resp.text[:300]}")
        
        data = resp.json()
        ai_text = data["choices"][0]["text"].strip()
        
        # Strip thinking tokens
        ai_text = self._strip_thinking_tokens(ai_text)
        
        if "User:" in ai_text:
            ai_text = ai_text.split("User:")[0].strip()
        
        print(f"[Conversational AI] Raw completions response: {ai_text[:80]}...")
        return ai_text
    
    def _strip_thinking_tokens(self, text):
        """
        Strip thinking/reasoning tokens from model output.
        Handles <think>...</think> tags and meta-commentary patterns.
        """
        import re
        
        # 1. Remove <think>...</think> blocks (common in reasoning models)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'<\|think\|>.*?<\|/think\|>', '', text, flags=re.DOTALL).strip()
        
        # 2. Remove lines that are meta-commentary (model describing what it's doing)
        meta_patterns = [
            r'^We (?:have|need|should|must|can|will|are).*?\.\s*',
            r'^The (?:user|system|conversation|message|query).*?\.\s*',
            r'^(?:Let me|I need to|I should|I will|Now I).*?\.\s*',
            r'^(?:They ask|They want|They say|Probably they).*?\.\s*',
            r'^(?:Should respond|Provide|Answer:)\s*',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        found_real_response = False
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if found_real_response:
                    cleaned_lines.append(line)
                continue
            
            is_meta = False
            for pattern in meta_patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_meta = True
                    break
            
            if not is_meta:
                found_real_response = True
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        
        # 3. If everything was stripped, return original (better than empty)
        if not result:
            return text.strip()
        
        # 4. Remove leading quotes if the model wrapped its response in them
        if result.startswith('"') and result.endswith('"'):
            result = result[1:-1].strip()
        
        return result
    
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
            f"{time_greeting}! I'm at your service, {user_name}. What's on your mind?",
        ]
        
        return random.choice(greetings)
    
    def get_farewell(self, user_name="Sir"):
        """Get a personalized farewell"""
        farewells = [
            f"Goodbye, {user_name}! Take care and see you soon! 👋",
            f"Until next time, {user_name}. Stay awesome! ✨",
            f"Farewell, {user_name}! Don't hesitate to call if you need me. 😊",
            f"Signing off for now, {user_name}. Rest well! 🌙",
        ]
        
        return random.choice(farewells)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history = []
        self.save_memory()
        return "Memory cleared, sir. Starting fresh!"
    
    def switch_backend(self, new_backend):
        """Switch between 'groq' and 'custom' backend at runtime"""
        if new_backend == "custom" and self.custom_client:
            self.client = self.custom_client
            self.active_model = self.custom_model
            self.active_max_tokens = self.custom_max_tokens
            self.backend = "custom"
            print(f"[Conversational AI] Switched to CUSTOM backend: {self.custom_model}")
            return True
        elif new_backend == "groq" and self.groq_client:
            self.client = self.groq_client
            self.active_model = self.groq_model
            self.active_max_tokens = 100
            self.backend = "groq"
            print(f"[Conversational AI] Switched to GROQ backend: {self.groq_model}")
            return True
        else:
            print(f"[Conversational AI] Cannot switch to {new_backend} - client not available")
            return False
    
    def get_backend_info(self):
        """Get current backend information"""
        return {
            "active_backend": self.backend,
            "model": self.active_model,
            "max_tokens": self.active_max_tokens,
            "groq_available": self.groq_client is not None,
            "custom_available": self.custom_client is not None,
            "custom_url": self.custom_base_url
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Global instance
_conversational_ai = None

def get_conversational_ai(groq_api_key=None, **kwargs):
    """Get or create the global conversational AI instance
    
    Supports all ConversationalAI constructor args via **kwargs.
    Example:
        get_conversational_ai(groq_api_key="...", backend="custom")
    """
    global _conversational_ai
    if _conversational_ai is None:
        _conversational_ai = ConversationalAI(groq_api_key=groq_api_key, **kwargs)
    return _conversational_ai

def chat_naturally(user_message, user_name="Sir", groq_api_key=None):
    """
    Quick function to chat naturally with Atlas
    
    Usage:
        response = chat_naturally("I'm feeling stressed today")
    """
    ai = get_conversational_ai(groq_api_key)
    return ai.chat(user_message, user_name)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("🤖 Atlas Conversational AI - Test Mode\n")
    
    # Test the conversational AI
    ai = ConversationalAI()
    
    print("Testing greetings:")
    print(f"  {ai.get_greeting('Aditya')}\n")
    
    print("Testing conversation:")
    test_messages = [
        "Hey Atlas, how are you?",
        "I'm feeling a bit stressed today",
        "Can you tell me a joke?",
        "What should I do when I feel overwhelmed?"
    ]
    
    for msg in test_messages:
        print(f"User: {msg}")
        response = ai.chat(msg, "Aditya")
        print(f"Atlas: {response}\n")
    
    print("Testing farewell:")
    print(f"  {ai.get_farewell('Aditya')}")
    
    print("\n✅ Conversational AI module ready!")
