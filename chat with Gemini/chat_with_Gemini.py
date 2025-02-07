import google.generativeai as genai
import json
import os
from datetime import datetime
from newsapi import NewsApiClient
import requests

# Available Gemini Models:
"""
1. gemini-2.0-flash-001 : Next generation features, speed, and multimodal generation
2. gemini-2.0-flash-lite-preview-02-05 : Optimized for cost efficiency and low latency
3. gemini-1.5-flash : Fast and versatile performance
"""

# API Keys
GEMINI_API_KEY = "" #Google Ai Studio
WEATHER_API_KEY = "" #OpenWeatherApi
NEWS_API_KEY = "" #https://newsapi.org/account
BRAVE_API_KEY = "" #https://api-dashboard.search.brave.com/app/keys

# Constants
HISTORY_FILE = "chat_history.json"
MAX_HISTORY = 20
DEFAULT_LOCATION = "Mahdia, Tunisia"

class GoodbyeAgent:
    def __init__(self):
        self.farewell_phrases = [
            'goodbye', 'good bye', 'bye', 'see you', 'cya', 'good night',
            'have to go', 'got to go', 'gtg', 'leaving', 'talk to you later',
            'catch you later', 'farewell', 'until next time', 'i\'m out',
            'signing off', 'going to sleep', 'heading out','see ya'
        ]
    
    def is_farewell(self, message):
        """Check if message is a farewell"""
        message = message.lower()
        return any(phrase in message for phrase in self.farewell_phrases)
    
    def get_farewell_response(self, message):
        """Generate appropriate farewell response"""
        time = datetime.now().hour
        
        if 'night' in message.lower() or time >= 20 or time <= 5:
            return "Good night! 🌙 Have a wonderful rest, and sweet dreams! Take care!"
        elif 'bye' in message.lower() or 'goodbye' in message.lower():
            return "Goodbye! 👋 Thanks for chatting with me. Hope to see you again soon!"
        else:
            return "Take care! 👋 Have a great time, and come back anytime you want to chat!"

class WebSearchAgent:
    def __init__(self):
        self.api_key = BRAVE_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
    
    def search(self, query):
        """Perform a web search using Brave Search API"""
        try:
            params = {
                "q": query,
                "count": 3  # Get top 3 results
            }
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            data = response.json()
            
            if 'web' in data and 'results' in data['web']:
                results = []
                for result in data['web']['results']:
                    results.append({
                        'title': result.get('title', ''),
                        'description': result.get('description', ''),
                        'url': result.get('url', '')
                    })
                return results
            return []
        except Exception as e:
            return f"Error performing web search: {str(e)}"

    def format_search_response(self, query, results):
        """Format search results into a natural, concise response"""
        if isinstance(results, str) and "Error" in results:
            return f"Sorry, I couldn't look that up right now. Let me try to help another way! 🤔"
        
        if not results:
            return f"Hmm, I'm not finding anything about that. Could you try asking in a different way? 🤔"
        
        # Extract the most relevant information from all results
        all_descriptions = " ".join(result['description'] for result in results)
        
        # Create a concise summary prompt
        prompt = f"""
        Based on these search results about '{query}':
        {all_descriptions}
        
        Create a very short, friendly, conversational response (2-3 sentences max).
        Make it sound completely natural, as if you already knew this information.
        Include an appropriate emoji.
        DO NOT mention sources or that you looked it up.
        """
        
        try:
            # Use Gemini to generate a concise summary
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-001')
            response = model.generate_content(prompt)
            return response.text.strip()
        except:
            # Fallback to basic summary if Gemini fails
            main_result = results[0]
            description = main_result['description'][:100].split('.')[0]  # Get first sentence only
            return f"Oh! {description}... 🤔 Want me to tell you more?"

class SupervisorAgent:
    def __init__(self, model):
        self.model = model
        self.goodbye_agent = GoodbyeAgent()
    
    def analyze_context(self, current_message, chat_history, current_time):
        """Analyze if we should trigger agents based on context"""
        # First check if it's a goodbye message
        if self.goodbye_agent.is_farewell(current_message):
            return 'goodbye'
            
        # Get last 5 messages
        last_messages = chat_history[-5:] if chat_history else []
        
        # Format conversation history
        history_text = "\n".join([
            f"{'Assistant' if msg['role'] == 'assistant' else 'User'}: {msg['content']}"
            for msg in last_messages
        ])
        
        prompt = f"""Current time: {current_time}
Last messages:
{history_text}

Current user message: "{current_message}"

Task: Based on the conversation context and current message, determine if:
1. The user is asking about weather/temperature for the first time
2. The user is requesting news updates for the first time
3. The user is asking about something that needs web search (unknown terms, complex questions)
4. The user is just continuing a conversation about a previous response
5. The user is starting a new general chat topic

Consider:
- If weather/news was just provided, and user is commenting on it, classify as 'chat'
- If it's a follow-up question about previous topic, classify as 'chat'
- If the user asks about something unfamiliar or needs factual information, classify as 'search'
- Only classify as 'weather' or 'news' if it's a new request for that information

Respond with exactly one word from: weather, news, search, chat

Classification:"""
        
        try:
            response = self.model.generate_content(prompt)
            intent = response.text.strip().lower()
            return intent if intent in ['weather', 'news', 'search'] else 'chat'
        except:
            return 'chat'

class WeatherAgent:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, location=DEFAULT_LOCATION):
        """Get current weather for location"""
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'conditions': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'feels_like': data['main']['feels_like'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

class NewsAgent:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    
    def get_news(self, topic):
        """Get latest news about a topic"""
        try:
            articles = self.newsapi.get_everything(
                q=topic,
                language='en',
                sort_by='publishedAt',
                page_size=3
            )
            
            return {
                'headlines': [article['title'] for article in articles['articles']],
                'source': [article['source']['name'] for article in articles['articles']],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return f"Error fetching news: {str(e)}"

class RapportAgent:
    def generate_report(self, query, response, agent_type):
        """Generate a brief report of the interaction"""
        try:
            return {
                'query_summary': query,
                'response_summary': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'action_taken': agent_type
            }
        except Exception as e:
            return f"Error generating report: {str(e)}"

def initialize_genai():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        # Test the connection
        response = model.generate_content("Test connection")
        print("✅ Successfully connected to Gemini API!")
        return model
    except Exception as e:
        print("❌ Failed to connect to Gemini API:", str(e))
        return None

def format_weather_response(weather_data):
    """Format weather data into a natural response"""
    temp = weather_data['temperature']
    temp_message = "That's quite chilly for our region! 🥶" if temp < 15 else "Pretty warm today! ☀️" if temp > 25 else "Nice moderate temperature! 😊"
    return f"The current temperature in Mahdia is {temp}°C with {weather_data['conditions']}. " \
           f"Feels like {weather_data['feels_like']}°C with {weather_data['humidity']}% humidity. {temp_message}"

def format_news_response(news_data):
    """Format news data into a natural response"""
    headlines = "\n".join(f"📰 {headline} (via {source})" 
                         for headline, source in zip(news_data['headlines'], news_data['source']))
    return f"Here are the latest headlines I found:\n\n{headlines}\n\nWould you like to know more about any of these stories?"

def get_chat_response(model, user_input, context, current_time):
    """Get a chat response from Gemini"""
    # Check for emotional context
    emotional_keywords = ['sad', 'happy', 'angry', 'tired', 'excited', 'worried', 'scared']
    is_emotional = any(keyword in user_input.lower() for keyword in emotional_keywords)
    
    # Check for repeated messages
    if context:
        last_messages = context.split('\n')[-4:]  # Get last 4 messages
        repeated_count = sum(1 for msg in last_messages if user_input.lower() in msg.lower())
        
        if repeated_count >= 2:
            if is_emotional:
                return "I can see you're feeling strongly about this. Would you like to talk more about what's on your mind? 🤗"
            else:
                return "I notice you're saying the same thing. Is everything okay? Would you like to talk about something specific? 🤔"
    
    prompt = f"""Current time: {current_time}
Previous messages:
{context}

Instructions: You are a friendly AI assistant having a casual conversation.
Context awareness rules:
1. If user expresses emotions:
   - Show empathy and understanding
   - Offer support or encouragement
   - Ask open-ended questions
2. If user seems disengaged:
   - Ask about their interests
   - Share something interesting
   - Keep the conversation light and casual
3. General rules:
   - Keep responses concise and natural
   - Use emojis occasionally
   - Stay focused on the current topic
   - Be proactive in guiding the conversation

User's message: {user_input}
Your response:"""
    
    response = model.generate_content(prompt)
    assistant_response = response.text.strip()
    if assistant_response.startswith("Assistant:"):
        assistant_response = assistant_response[10:].strip()
    return assistant_response

def get_conversation_context(history):
    """Format conversation history for the AI"""
    context = []
    for msg in history:
        role = "Assistant" if msg["role"] == "assistant" else "User"
        context.append(f"{role}: {msg['content']}")
    return "\n".join(context[-5:])  # Only use last 5 messages for context

def save_chat_history(history):
    """Save only the last MAX_HISTORY messages"""
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    return history

def reset_chat_history():
    """Create or reset the chat history file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)
    return []

def main():
    # Initialize agents and model
    model = initialize_genai()
    if not model:
        return
        
    supervisor = SupervisorAgent(model)
    weather_agent = WeatherAgent()
    news_agent = NewsAgent()
    web_agent = WebSearchAgent()
    rapport_agent = RapportAgent()
    goodbye_agent = GoodbyeAgent()

    # Reset chat history at start
    chat_history = reset_chat_history()
    print("\nWelcome to Gemini Chat! Type 'exit' or say goodbye to end the conversation.\n")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Location: {DEFAULT_LOCATION}\n")
    
    while True:
        user_input = input("You: ").strip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user_input.lower() == 'exit':
            print("\nAssistant: Goodbye! Thanks for chatting! 👋\n")
            break
        
        # Add user message to history
        chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": current_time
        })
        
        try:
            # Let supervisor analyze context and determine intent
            intent = supervisor.analyze_context(user_input, chat_history, current_time)
            
            if intent == 'goodbye':
                response = goodbye_agent.get_farewell_response(user_input)
                report = rapport_agent.generate_report(user_input, response, "goodbye_agent")
                print("\nAssistant:", response, "\n")
                break
            
            elif intent == 'weather':
                weather_data = weather_agent.get_weather()
                response = format_weather_response(weather_data)
                report = rapport_agent.generate_report(user_input, response, "weather_agent")
            
            elif intent == 'news':
                topic = user_input.lower().replace('news', '').replace('latest', '').strip()
                if not topic:
                    topic = "general"
                news_data = news_agent.get_news(topic)
                response = format_news_response(news_data)
                report = rapport_agent.generate_report(user_input, response, "news_agent")
            
            elif intent == 'search':
                search_results = web_agent.search(user_input)
                response = web_agent.format_search_response(user_input, search_results)
                report = rapport_agent.generate_report(user_input, response, "web_search_agent")
            
            else:
                context = get_conversation_context(chat_history)
                response = get_chat_response(model, user_input, context, current_time)
                report = rapport_agent.generate_report(user_input, response, "chat_agent")
            
            print("\nAssistant:", response, "\n")
            
            # Add response to history
            chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": current_time
            })
            
            # Update history file
            chat_history = save_chat_history(chat_history)
            
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    main() 
