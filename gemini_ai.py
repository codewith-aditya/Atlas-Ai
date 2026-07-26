# gemini_ai.py
"""
Google Gemini AI integration for Atlas
Provides advanced AI responses using Gemini API
"""

import os
import google.generativeai as genai

class GeminiAI:
    def __init__(self, api_key=None):
        """Initialize Gemini AI with API key"""
        self.api_key = api_key or self.load_api_key()
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("[GeminiAI] Initialized successfully")
        else:
            print("[GeminiAI] API key not found")
            self.model = None
    
    def load_api_key(self):
        """Load Gemini API key from config file"""
        config_file = os.path.join('materials', 'api_keys.txt')
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"[GeminiAI] Error loading API key: {e}")
        return None
    
    def generate_response(self, prompt, max_tokens=500):
        """
        Generate AI response using Gemini
        
        Args:
            prompt (str): User prompt/question
            max_tokens (int): Maximum response length
        
        Returns:
            str: AI generated response
        """
        if not self.model:
            return "Gemini AI is not configured. Please add your API key."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[GeminiAI] Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def chat(self, message, context=None):
        """
        Chat with Gemini AI
        
        Args:
            message (str): User message
            context (str, optional): Previous conversation context
        
        Returns:
            str: AI response
        """
        if context:
            prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
        else:
            prompt = message
        
        return self.generate_response(prompt)
    
    def analyze_image(self, image_path, question="What do you see in this image?"):
        """
        Analyze an image using Gemini Vision
        
        Args:
            image_path (str): Path to image file
            question (str): Question about the image
        
        Returns:
            str: Image analysis
        """
        if not self.model:
            return "Gemini AI is not configured."
        
        try:
            # Use Gemini Pro Vision for image analysis
            vision_model = genai.GenerativeModel('gemini-pro-vision')
            
            # Load image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            # Generate response
            response = vision_model.generate_content([question, img])
            return response.text
        except Exception as e:
            print(f"[GeminiAI] Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"
    
    def summarize_text(self, text, max_length=200):
        """
        Summarize long text
        
        Args:
            text (str): Text to summarize
            max_length (int): Maximum summary length
        
        Returns:
            str: Summarized text
        """
        prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
        return self.generate_response(prompt)
    
    def answer_question(self, question, context=None):
        """
        Answer a specific question
        
        Args:
            question (str): User's question
            context (str, optional): Additional context
        
        Returns:
            str: Answer
        """
        if context:
            prompt = f"Context: {context}\n\nQuestion: {question}\n\nProvide a clear and concise answer:"
        else:
            prompt = f"Question: {question}\n\nProvide a clear and concise answer:"
        
        return self.generate_response(prompt)


# Test function
if __name__ == "__main__":
    gemini = GeminiAI()
    
    # Test chat
    response = gemini.chat("What is artificial intelligence?")
    print("Chat Response:", response)
    
    # Test question answering
    answer = gemini.answer_question("What is the capital of France?")
    print("\nQuestion Answer:", answer)
