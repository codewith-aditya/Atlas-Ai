# ============================================================================
# ATLAS ADVANCED AI BRAIN MODULE
# ============================================================================
# This module provides intelligent context-aware processing, learning capabilities,
# and smart decision-making for the Atlas AI Assistant.
# ============================================================================

import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import threading

# ============================================================================
# CONFIGURATION
# ============================================================================

class AIBrainConfig:
    """Configuration for AI Brain Module"""
    
    # Paths
    MATERIALS_PATH = "materials"
    BRAIN_MEMORY_FILE = os.path.join(MATERIALS_PATH, "brain_memory.json")
    USER_PATTERNS_FILE = os.path.join(MATERIALS_PATH, "user_patterns.json")
    CONTEXT_HISTORY_FILE = os.path.join(MATERIALS_PATH, "context_history.json")
    
    # Memory Settings
    MAX_CONTEXT_MESSAGES = 50
    MAX_PATTERN_ENTRIES = 100
    LEARNING_THRESHOLD = 3  # Minimum occurrences to learn a pattern
    
    # Feature Flags
    ENABLE_EMOTION_DETECTION = True
    ENABLE_PROACTIVE_SUGGESTIONS = True
    ENABLE_PATTERN_LEARNING = True
    ENABLE_CONTEXT_AWARENESS = True


# ============================================================================
# AI BRAIN CLASS
# ============================================================================

class AtlasAIBrain:
    """
    Advanced AI Brain for Atlas Assistant
    
    Features:
    - Context-aware conversation tracking
    - User pattern learning and prediction
    - Emotion detection and empathetic responses
    - Proactive assistance suggestions
    - Smart automation recommendations
    - Conversation summarization
    """
    
    def __init__(self):
        self.config = AIBrainConfig()
        self.lock = threading.Lock()
        
        # Initialize memory structures
        self.context_memory = []
        self.user_patterns = defaultdict(list)
        self.emotion_history = []
        self.automation_stats = defaultdict(int)
        self.conversation_topics = []
        
        # Load existing data
        self._load_brain_memory()
        self._load_user_patterns()
        
        print("[AI Brain] Advanced AI Brain Module initialized successfully! 🧠")
    
    # ========================================================================
    # CORE MEMORY FUNCTIONS
    # ========================================================================
    
    def _load_brain_memory(self):
        """Load brain memory from file"""
        try:
            if os.path.exists(self.config.BRAIN_MEMORY_FILE):
                with open(self.config.BRAIN_MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.context_memory = data.get('context_memory', [])[-self.config.MAX_CONTEXT_MESSAGES:]
                    self.emotion_history = data.get('emotion_history', [])[-50:]
                    self.conversation_topics = data.get('conversation_topics', [])[-20:]
                    print("[AI Brain] Memory loaded successfully")
        except Exception as e:
            print(f"[AI Brain] Error loading memory: {e}")
            self.context_memory = []
            self.emotion_history = []
            self.conversation_topics = []
    
    def _save_brain_memory(self):
        """Save brain memory to file"""
        try:
            with self.lock:
                data = {
                    'context_memory': self.context_memory[-self.config.MAX_CONTEXT_MESSAGES:],
                    'emotion_history': self.emotion_history[-50:],
                    'conversation_topics': self.conversation_topics[-20:],
                    'last_updated': datetime.now().isoformat()
                }
                os.makedirs(self.config.MATERIALS_PATH, exist_ok=True)
                with open(self.config.BRAIN_MEMORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AI Brain] Error saving memory: {e}")
    
    def _load_user_patterns(self):
        """Load learned user patterns"""
        try:
            if os.path.exists(self.config.USER_PATTERNS_FILE):
                with open(self.config.USER_PATTERNS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_patterns = defaultdict(list, data.get('patterns', {}))
                    self.automation_stats = defaultdict(int, data.get('automation_stats', {}))
                    print("[AI Brain] User patterns loaded successfully")
        except Exception as e:
            print(f"[AI Brain] Error loading patterns: {e}")
            self.user_patterns = defaultdict(list)
            self.automation_stats = defaultdict(int)
    
    def _save_user_patterns(self):
        """Save learned user patterns"""
        try:
            with self.lock:
                data = {
                    'patterns': dict(self.user_patterns),
                    'automation_stats': dict(self.automation_stats),
                    'last_updated': datetime.now().isoformat()
                }
                os.makedirs(self.config.MATERIALS_PATH, exist_ok=True)
                with open(self.config.USER_PATTERNS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AI Brain] Error saving patterns: {e}")
    
    # ========================================================================
    # EMOTION DETECTION
    # ========================================================================
    
    def detect_emotion(self, text):
        """
        Detect user emotion from text
        
        Returns: emotion type and confidence score
        """
        if not self.config.ENABLE_EMOTION_DETECTION:
            return "neutral", 0.5
        
        text_lower = text.lower()
        
        # Emotion patterns
        emotions = {
            'happy': ['happy', 'great', 'awesome', 'excellent', 'wonderful', 'good', 'nice', 'love', 'thanks', 'thank you'],
            'sad': ['sad', 'unhappy', 'depressed', 'down', 'upset', 'disappointed', 'terrible', 'awful'],
            'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'hate'],
            'excited': ['excited', 'amazing', 'wow', 'incredible', 'fantastic', 'yay', 'cool'],
            'confused': ['confused', 'don\'t understand', 'what', 'how', 'why', 'help', 'stuck'],
            'stressed': ['stressed', 'worried', 'anxious', 'nervous', 'overwhelmed', 'busy'],
            'grateful': ['thank', 'thanks', 'grateful', 'appreciate', 'thankful']
        }
        
        detected_emotions = {}
        for emotion, keywords in emotions.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                detected_emotions[emotion] = count
        
        if detected_emotions:
            primary_emotion = max(detected_emotions, key=detected_emotions.get)
            confidence = min(detected_emotions[primary_emotion] * 0.3, 1.0)
            
            # Save emotion to history
            self.emotion_history.append({
                'emotion': primary_emotion,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'text_snippet': text[:50]
            })
            
            return primary_emotion, confidence
        
        return "neutral", 0.5
    
    def get_empathetic_response_prefix(self, emotion, confidence):
        """Generate empathetic response based on detected emotion"""
        if confidence < 0.3:
            return ""
        
        responses = {
            'happy': ["I'm glad to hear that! 😊", "That's wonderful! ✨", "Great to see you happy! 🎉"],
            'sad': ["I'm sorry to hear that. 💙", "I understand how you feel. 🤗", "I'm here for you. ❤️"],
            'angry': ["I understand your frustration. 😔", "Let me help you with that. 💪", "I hear you. 🙏"],
            'excited': ["That's amazing! 🚀", "I can feel your excitement! ⚡", "Awesome! 🌟"],
            'confused': ["Let me help clarify that. 💡", "I'll explain it better. 📚", "No worries, I'm here to help! 🤝"],
            'stressed': ["Take a deep breath. 🧘", "Let me help reduce your workload. 💆", "I'm here to assist. 🌈"],
            'grateful': ["You're very welcome! 😊", "Happy to help! ✨", "Anytime! 🤗"]
        }
        
        import random
        return random.choice(responses.get(emotion, [""]))
    
    # ========================================================================
    # CONTEXT AWARENESS
    # ========================================================================
    
    def add_context(self, user_message, bot_response, metadata=None):
        """Add conversation to context memory"""
        if not self.config.ENABLE_CONTEXT_AWARENESS:
            return
        
        context_entry = {
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.context_memory.append(context_entry)
        
        # Extract and save topic
        topic = self._extract_topic(user_message)
        if topic:
            self.conversation_topics.append({
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            })
        
        # Keep only recent context
        if len(self.context_memory) > self.config.MAX_CONTEXT_MESSAGES:
            self.context_memory = self.context_memory[-self.config.MAX_CONTEXT_MESSAGES:]
        
        self._save_brain_memory()
    
    def get_relevant_context(self, current_query, max_results=5):
        """Get relevant past conversations based on current query"""
        if not self.context_memory:
            return []
        
        query_lower = current_query.lower()
        query_words = set(query_lower.split())
        
        scored_contexts = []
        for ctx in self.context_memory[-20:]:  # Check last 20 conversations
            user_msg = ctx['user'].lower()
            bot_msg = ctx['bot'].lower()
            
            # Calculate relevance score
            user_words = set(user_msg.split())
            bot_words = set(bot_msg.split())
            
            common_words = query_words & (user_words | bot_words)
            score = len(common_words)
            
            if score > 0:
                scored_contexts.append((score, ctx))
        
        # Sort by score and return top results
        scored_contexts.sort(reverse=True, key=lambda x: x[0])
        return [ctx for score, ctx in scored_contexts[:max_results]]
    
    def _extract_topic(self, text):
        """Extract main topic from text"""
        # Common topics
        topics = {
            'weather': ['weather', 'temperature', 'rain', 'sunny', 'climate'],
            'music': ['song', 'music', 'play', 'youtube', 'listen'],
            'time': ['time', 'clock', 'hour', 'minute', 'when'],
            'reminder': ['remind', 'reminder', 'remember', 'alert'],
            'automation': ['open', 'close', 'launch', 'start', 'stop'],
            'information': ['what', 'who', 'where', 'search', 'google'],
            'system': ['volume', 'brightness', 'battery', 'cpu', 'ram'],
            'communication': ['whatsapp', 'message', 'send', 'call', 'contact']
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return "general"
    
    # ========================================================================
    # PATTERN LEARNING
    # ========================================================================
    
    def learn_user_pattern(self, action_type, details):
        """Learn user behavior patterns"""
        if not self.config.ENABLE_PATTERN_LEARNING:
            return
        
        hour = datetime.now().hour
        day_of_week = datetime.now().strftime("%A")
        
        pattern_key = f"{action_type}_{hour}_{day_of_week}"
        
        self.user_patterns[action_type].append({
            'details': details,
            'hour': hour,
            'day': day_of_week,
            'timestamp': datetime.now().isoformat()
        })
        
        # Track automation statistics
        self.automation_stats[action_type] += 1
        
        # Keep only recent patterns
        if len(self.user_patterns[action_type]) > self.config.MAX_PATTERN_ENTRIES:
            self.user_patterns[action_type] = self.user_patterns[action_type][-self.config.MAX_PATTERN_ENTRIES:]
        
        self._save_user_patterns()
    
    def get_pattern_suggestions(self):
        """Get proactive suggestions based on learned patterns"""
        if not self.config.ENABLE_PROACTIVE_SUGGESTIONS:
            return []
        
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime("%A")
        
        suggestions = []
        
        # Analyze patterns for current time
        for action_type, patterns in self.user_patterns.items():
            matching_patterns = [
                p for p in patterns
                if p['hour'] == current_hour and p['day'] == current_day
            ]
            
            if len(matching_patterns) >= self.config.LEARNING_THRESHOLD:
                # Extract most common details
                details_counter = Counter([p['details'] for p in matching_patterns])
                most_common = details_counter.most_common(1)[0]
                
                suggestions.append({
                    'action': action_type,
                    'details': most_common[0],
                    'confidence': most_common[1] / len(matching_patterns),
                    'occurrences': most_common[1]
                })
        
        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)
    
    # ========================================================================
    # SMART RESPONSE ENHANCEMENT
    # ========================================================================
    
    def enhance_response(self, user_query, base_response):
        """
        Enhance bot response with context, emotion, and suggestions
        
        Returns: Enhanced response with additional intelligence
        """
        enhanced = base_response
        
        # 1. Detect emotion and add empathetic prefix
        emotion, confidence = self.detect_emotion(user_query)
        empathy_prefix = self.get_empathetic_response_prefix(emotion, confidence)
        
        if empathy_prefix and not any(cmd in base_response.lower() for cmd in ['open', 'close', 'searching', 'playing', 'reminder set']):
            enhanced = f"{empathy_prefix} {enhanced}"
        
        # 2. Add context-aware information
        relevant_context = self.get_relevant_context(user_query, max_results=2)
        
        # 3. Add proactive suggestions (DISABLED - causes unwanted speaking)
        # import random
        # if random.random() < 0.2:  # 20% chance
        #     suggestions = self.get_pattern_suggestions()
        #     if suggestions and not any(cmd in base_response.lower() for cmd in ['open', 'close', 'searching']):
        #         top_suggestion = suggestions[0]
        #         if top_suggestion['confidence'] > 0.6:
        #             enhanced += f"\n\n💡 Suggestion: Based on your routine, you might want to {top_suggestion['action']} now."
        
        return enhanced
    
    # ========================================================================
    # CONVERSATION ANALYSIS
    # ========================================================================
    
    def get_conversation_summary(self, last_n_messages=10):
        """Generate summary of recent conversations"""
        if not self.context_memory:
            return "No conversation history available."
        
        recent = self.context_memory[-last_n_messages:]
        
        # Count topics
        topics = [self._extract_topic(ctx['user']) for ctx in recent]
        topic_counts = Counter(topics)
        
        # Count emotions
        emotions = [self.detect_emotion(ctx['user'])[0] for ctx in recent]
        emotion_counts = Counter(emotions)
        
        summary = f"📊 Conversation Summary (Last {len(recent)} messages):\n"
        summary += f"- Main topics: {', '.join([f'{t} ({c})' for t, c in topic_counts.most_common(3)])}\n"
        summary += f"- Emotional tone: {', '.join([f'{e} ({c})' for e, c in emotion_counts.most_common(3)])}\n"
        summary += f"- Total interactions: {len(self.context_memory)}"
        
        return summary
    
    def get_user_insights(self):
        """Get insights about user behavior"""
        insights = []
        
        # Most used automations
        if self.automation_stats:
            top_automation = max(self.automation_stats.items(), key=lambda x: x[1])
            insights.append(f"🎯 Most used feature: {top_automation[0]} ({top_automation[1]} times)")
        
        # Conversation activity
        if self.context_memory:
            insights.append(f"💬 Total conversations: {len(self.context_memory)}")
        
        # Emotional patterns
        if self.emotion_history:
            recent_emotions = [e['emotion'] for e in self.emotion_history[-20:]]
            emotion_counts = Counter(recent_emotions)
            dominant_emotion = emotion_counts.most_common(1)[0]
            insights.append(f"😊 Recent mood: {dominant_emotion[0]} ({dominant_emotion[1]} times)")
        
        # Active topics
        if self.conversation_topics:
            recent_topics = [t['topic'] for t in self.conversation_topics[-20:]]
            topic_counts = Counter(recent_topics)
            top_topic = topic_counts.most_common(1)[0]
            insights.append(f"📌 Favorite topic: {top_topic[0]} ({top_topic[1]} times)")
        
        return "\n".join(insights) if insights else "Not enough data for insights yet."
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def reset_memory(self):
        """Reset all brain memory (use with caution)"""
        self.context_memory = []
        self.emotion_history = []
        self.conversation_topics = []
        self._save_brain_memory()
        print("[AI Brain] Memory reset successfully")
    
    def export_brain_data(self, export_path=None):
        """Export all brain data for backup"""
        if export_path is None:
            export_path = os.path.join(self.config.MATERIALS_PATH, f"brain_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        data = {
            'context_memory': self.context_memory,
            'user_patterns': dict(self.user_patterns),
            'emotion_history': self.emotion_history,
            'automation_stats': dict(self.automation_stats),
            'conversation_topics': self.conversation_topics,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[AI Brain] Data exported to {export_path}")
        return export_path


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Create global AI Brain instance
ai_brain = None

def get_ai_brain():
    """Get or create AI Brain instance"""
    global ai_brain
    if ai_brain is None:
        ai_brain = AtlasAIBrain()
    return ai_brain


# ============================================================================
# INTEGRATION FUNCTIONS FOR MAIN.PY
# ============================================================================

def process_with_ai_brain(user_query, bot_response, automation_action=None):
    """
    Process conversation through AI Brain
    
    Call this function from main.py after getting bot response
    """
    brain = get_ai_brain()
    
    # Add to context
    metadata = {'automation': automation_action} if automation_action else {}
    brain.add_context(user_query, bot_response, metadata)
    
    # Learn patterns if automation was performed
    if automation_action:
        brain.learn_user_pattern(automation_action, user_query)
    
    # Enhance response
    enhanced_response = brain.enhance_response(user_query, bot_response)
    
    return enhanced_response


def get_proactive_suggestions():
    """Get proactive suggestions for user"""
    brain = get_ai_brain()
    return brain.get_pattern_suggestions()


def get_conversation_insights():
    """Get conversation insights"""
    brain = get_ai_brain()
    return brain.get_user_insights()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("🧠 Testing Atlas AI Brain Module...\n")
    
    # Create brain instance
    brain = AtlasAIBrain()
    
    # Test emotion detection
    print("1. Testing Emotion Detection:")
    test_messages = [
        "I'm so happy today!",
        "This is frustrating",
        "Thank you so much for your help",
        "I'm confused about this"
    ]
    
    for msg in test_messages:
        emotion, confidence = brain.detect_emotion(msg)
        print(f"   '{msg}' -> {emotion} (confidence: {confidence:.2f})")
    
    # Test context awareness
    print("\n2. Testing Context Awareness:")
    brain.add_context("What's the weather?", "checking weather...", {'automation': 'weather'})
    brain.add_context("Play some music", "playing song...", {'automation': 'music'})
    brain.add_context("Tell me about the weather again", "checking weather...", {'automation': 'weather'})
    
    relevant = brain.get_relevant_context("weather forecast")
    print(f"   Found {len(relevant)} relevant contexts for 'weather forecast'")
    
    # Test pattern learning
    print("\n3. Testing Pattern Learning:")
    brain.learn_user_pattern("open_youtube", "open youtube")
    brain.learn_user_pattern("open_youtube", "open youtube")
    brain.learn_user_pattern("open_youtube", "open youtube")
    
    suggestions = brain.get_pattern_suggestions()
    print(f"   Generated {len(suggestions)} suggestions")
    
    # Test insights
    print("\n4. User Insights:")
    print(brain.get_user_insights())
    
    print("\n✅ AI Brain Module test completed!")
