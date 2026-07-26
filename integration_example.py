# integration_example.py
"""
Example of how to use Google Search and Gemini AI in Atlas
"""

from google_search import GoogleSearch
from gemini_ai import GeminiAI

def search_and_explain(query):
    """Search Google and get AI explanation"""
    
    # Initialize modules
    search = GoogleSearch()
    gemini = GeminiAI()
    
    print(f"\n🔍 Searching for: {query}")
    print("=" * 50)
    
    # Perform search
    results = search.search(query, num_results=3)
    
    if results:
        print(f"\n✅ Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['snippet'][:100]}...")
            print()
        
        # Use Gemini to explain
        context = "\n".join([f"{r['title']}: {r['snippet']}" for r in results])
        explanation = gemini.answer_question(
            f"Based on these search results, explain {query} in simple terms",
            context=context
        )
        
        print("\n🤖 AI Explanation:")
        print("=" * 50)
        print(explanation)
    else:
        print("❌ No results found")


def ask_gemini(question):
    """Ask Gemini AI a question"""
    gemini = GeminiAI()
    
    print(f"\n❓ Question: {question}")
    print("=" * 50)
    
    answer = gemini.answer_question(question)
    
    print("\n🤖 Answer:")
    print("=" * 50)
    print(answer)


if __name__ == "__main__":
    # Example 1: Search and explain
    search_and_explain("What is machine learning?")
    
    # Example 2: Direct AI question
    ask_gemini("How does photosynthesis work?")
