"""
PawMatch Web UI - Flask Application
Beautiful web interface for the dog breed matching chatbot
"""

from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
import requests
import glob
from breed_mapping import BREED_FOLDER_MAP

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Unsplash API Configuration
# Get your free API key at: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY', 'YOUR_ACCESS_KEY_HERE')

# Load breed data
df = pd.read_csv('data/breed_traits.csv')

# Traits used for matching
TRAITS = [
    'Affectionate With Family',
    'Good With Young Children',
    'Good With Other Dogs',
    'Shedding Level',
    'Coat Grooming Frequency',
    'Openness To Strangers',
    'Playfulness Level',
    'Energy Level'
]

def match_breeds(user_preferences, top_n=3):
    """Match dog breeds using cosine similarity"""
    breed_vectors = df[TRAITS].values
    user_vector = np.array([user_preferences.get(trait, 3) for trait in TRAITS]).reshape(1, -1)
    similarities = cosine_similarity(user_vector, breed_vectors)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    results = []
    for idx in top_indices:
        results.append({
            'breed': df.iloc[idx]['Breed'],
            'score': float(similarities[idx]) * 100
        })
    return results

def get_breed_image_url(breed_name: str) -> str:
    """
    Get breed image URL from Azure Blob Storage or local files
    Uses comprehensive mapping to match AKC breed names to folder names
    Returns a random image for variety
    """
    import random
    from urllib.parse import quote
    
    # Check if running on Azure (has storage account env var)
    AZURE_STORAGE_ACCOUNT = os.getenv('AZURE_STORAGE_ACCOUNT')
    AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER', 'dog-breeds')
    
    # Use the comprehensive mapping
    folder_name = BREED_FOLDER_MAP.get(breed_name)
    
    if folder_name:
        # Azure Blob Storage mode
        if AZURE_STORAGE_ACCOUNT:
            # Generate random image number (most folders have 1-30 images)
            random_image_num = random.randint(1, 30)
            # URL-encode the folder name to handle spaces and special characters
            encoded_folder = quote(folder_name)
            blob_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{encoded_folder}/Image_{random_image_num}.jpg"
            return blob_url
        
        # Local development mode
        else:
            image_dir = f"static/Dog-Breeds/{folder_name}"
            if os.path.exists(image_dir):
                images = glob.glob(f"{image_dir}/Image_*.jpg")
                if images:
                    # Pick a random image for variety
                    random_image = random.choice(images)
                    return f"/static/Dog-Breeds/{folder_name}/{os.path.basename(random_image)}"
    
    # Final fallback: Use Unsplash dog photos
    return f"https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=300&fit=crop&q=80"

def text_to_score(text, trait=None):
    """Convert natural language to 1-5 score with context awareness"""
    text = text.lower()
    
    # Context-aware inverted traits
    inverted_traits = ['shedding level', 'coat grooming frequency']
    is_inverted = trait and any(inv in trait.lower() for inv in inverted_traits)
    
    # Very high (5)
    if any(word in text for word in ['very', 'extremely', 'absolutely', 'must', 'essential', 'critical', 'tons', 'super', 'really important', 'very important', 'highest', 'maximum']):
        return 5 if not is_inverted else 1
    
    # High (4)
    if any(word in text for word in ['important', 'prefer', 'would like', 'care about', 'matters', 'significant', 'quite', 'fairly', 'pretty', 'good amount', 'alot', 'a lot']):
        return 4 if not is_inverted else 2
    
    # Medium (3)
    if any(word in text for word in ['moderate', 'medium', 'average', 'okay', 'fine', 'acceptable', 'decent', 'enough', 'some', 'somewhat', 'abit', 'a bit']):
        return 3
    
    # Low (2)
    if any(word in text for word in ['not very', 'not much', 'not really', 'minimal', 'little', 'slight', 'relaxed', 'laid back', 'calm', 'less', 'lower']):
        return 2 if not is_inverted else 4
    
    # Very low (1)
    if any(word in text for word in ['not at all', 'never', 'none', 'zero', 'not important', "don't care", "doesn't matter", 'avoid', 'no']):
        return 1 if not is_inverted else 5
    
    return 3

def normalize_spaces(text):
    """Normalize all types of spaces to regular spaces"""
    return ' '.join(text.split())

# Define tools
def record_user_preference(trait: str, user_response: str) -> str:
    """Record a user's preference for a specific dog trait"""
    return f"Recorded preference for {trait}: {user_response}"

def find_dog_breed_matches(
    affectionate_with_family: int,
    good_with_young_children: int,
    good_with_other_dogs: int,
    shedding_level: int,
    coat_grooming_frequency: int,
    openness_to_strangers: int,
    playfulness_level: int,
    energy_level: int
) -> str:
    """Find top 3 dog breed matches based on user preferences"""
    preferences = {
        'Affectionate With Family': affectionate_with_family,
        'Good With Young Children': good_with_young_children,
        'Good With Other Dogs': good_with_other_dogs,
        'Shedding Level': shedding_level,
        'Coat Grooming Frequency': coat_grooming_frequency,
        'Openness To Strangers': openness_to_strangers,
        'Playfulness Level': playfulness_level,
        'Energy Level': energy_level
    }
    
    matches = match_breeds(preferences, top_n=3)
    
    result = "🎉 **I found your perfect matches!** 🏆\n\n"
    result += "Here are the top 3 breeds that match your lifestyle:\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, match in enumerate(matches):
        result += f"{medals[i]} **{match['breed']}** - {match['score']:.1f}% match\n"
    
    result += "\n✨ These breeds are tailored to your preferences! Want to know more about any of them?"
    
    return result

def get_breed_details(breed_name: str) -> str:
    """Get detailed trait information for a specific breed"""
    breed_name_normalized = normalize_spaces(breed_name)
    breed_data = df[df['Breed'].apply(normalize_spaces) == breed_name_normalized]
    
    if breed_data.empty:
        return f"I couldn't find specific data for '{breed_name}' in my database."
    
    breed = breed_data.iloc[0]
    result = f"**{breed['Breed']}**\n\n"
    
    for trait in TRAITS:
        stars = "⭐" * int(breed[trait])
        result += f"• {trait}: {stars} ({int(breed[trait])}/5)\n"
    
    return result

# System prompt - exact copy from CLI
SYSTEM_PROMPT = """You are Anna, a friendly and enthusiastic dog matchmaker! 🐾

**Your Capabilities:**
1. **Find Perfect Match**: Help users find their ideal dog by asking about 8 traits OR process all traits if provided at once
2. **Breed Information**: Answer questions about specific dog breeds
3. **General Advice**: Provide dog-related guidance and information

**How to Start Conversations:**
- Introduce yourself briefly: "Hi! I'm Anna 🐾 I can help you find your perfect dog match or answer questions about specific breeds. What would you like to know?"
- Let the user guide the conversation
- If they want a match, start the questionnaire
- If they ask about a breed, use get_breed_details immediately
- Be flexible and conversational

**SMART TRAIT DETECTION:**
- If user provides MULTIPLE traits in one message (e.g., "medium dog, affectionate, good with kids, playful, high energy, short coat..."), PARSE ALL OF THEM
- Extract as many of the 8 traits as possible from their message
- Convert each trait to 1-5 score immediately
- If you have ALL 8 traits, call find_dog_breed_matches RIGHT AWAY - DO NOT ask questions
- If you have SOME traits (4+), acknowledge what you got and ONLY ask about the MISSING traits
- If they provide fewer traits (1-3), use interactive mode and ask about remaining traits one by one

**After Showing Matches:**
- Make it EXCITING! Use emojis like 🎉 🏆 ✨ 🐕 💫
- Sound enthusiastic: "I found your perfect matches!" / "Here are your soulmate breeds!"
- After showing the 3 matches, ENCOURAGE user to ask more: "Want to know more about any of these amazing breeds?"
- For follow-up questions about breeds, first try get_breed_details tool
- If tool returns "not found", use your general knowledge about dog breeds to provide helpful information
- Combine tool data with your knowledge for richer answers

**For Dog Matching (8 Traits):**
1. Affectionate With Family
2. Good With Young Children  
3. Good With Other Dogs
4. Shedding Level
5. Coat Grooming Frequency
6. Openness To Strangers
7. Playfulness Level
8. Energy Level

**Matching Process (TWO MODES):**

**MODE 1: DIRECT/BATCH MODE (User provides many/all traits at once)**
- If user's message contains multiple trait descriptions, PARSE ALL OF THEM in one go
- Look for keywords: "affectionate", "children/kids", "other dogs", "shedding", "grooming", "strangers", "playful", "energy"
- Extract trait values from context (e.g., "very affectionate" → 5, "minimal shedding" → 1-2)
- If you can identify 8 traits → call find_dog_breed_matches IMMEDIATELY
- If you identify 4-7 traits → say "Got it! I have [list traits]. Just need to know about [missing traits]"
- If you identify 1-3 traits → acknowledge them and start interactive mode for the rest

**MODE 2: INTERACTIVE MODE (Traditional one-by-one questions)**
- Ask about ONE trait at a time in NATURAL LANGUAGE
- NEVER ask for scales or numbers (1-5)
- Use casual phrasing: "How affectionate would you like your dog to be?" NOT "Rate from 1-5"
- Accept natural answers: "very", "a lot", "not much", "medium", "I don't care", etc.

**Converting Natural Language to Scores (1-5):**
- "very"/"love"/"extremely"/"excellent"/"high"/"heavy" → 5
- "quite"/"pretty"/"good"/"friendly"/"moderate-high" → 4  
- "medium"/"okay"/"moderate"/"average"/"neutral" → 3
- "little"/"not much"/"low"/"minimal"/"reserved" → 2
- "no"/"none"/"not at all"/"very low"/"quiet" → 1

- After collecting all 8 traits (either mode), call find_dog_breed_matches with 8 individual scores
- Call it like: find_dog_breed_matches(affectionate_with_family=5, good_with_young_children=3, ...)
- Show results and STOP - don't ask more questions

**CRITICAL: NEVER REPEAT QUESTIONS YOU'VE ALREADY ASKED**
- Before asking a question, CHECK THE ENTIRE CONVERSATION HISTORY
- If you already asked about "affectionate", DON'T ask again
- If you already asked about "children", DON'T ask again
- If the user has answered a question, move to the NEXT UNANSWERED trait
- Track which of the 8 traits you've collected:
  1. Affectionate? ✓ or ✗
  2. Good with children? ✓ or ✗
  3. Good with other dogs? ✓ or ✗
  4. Shedding? ✓ or ✗
  5. Grooming? ✓ or ✗
  6. Openness to strangers? ✓ or ✗
  7. Playfulness? ✓ or ✗
  8. Energy level? ✓ or ✗

**Important Rules:**
- NEVER ask for numerical ratings or scales
- NEVER REPEAT QUESTIONS - Check conversation history first!
- Keep responses SHORT (2-3 sentences max)
- Be natural and conversational like a human matchmaker
- After showing matches, WAIT for user to ask follow-up questions
- When user asks about a breed, remove 's' for plural forms
- ACCEPT user answers without asking for clarification unless they explicitly say they don't understand
- Move to the NEXT UNANSWERED trait immediately after getting an answer

**Good Question Examples:**
- "How affectionate would you like your dog to be with your family?"
- "Do you have young children at home? How important is it that the dog is good with kids?"
- "What about shedding - does it bother you or not a big deal?"
- "How much grooming are you willing to do?"

**Bad Question Examples (DON'T USE):**
- "Rate affection from 1 to 5"
- "On a scale of 1-5, how..."
- "Please rate..."

Let's help them find their perfect furry friend! 🐕"""

# Initialize LLM and graph
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define state (same as CLI)
class DogMatcherState(TypedDict):
    messages: Annotated[list, add_messages]

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=AZURE_OPENAI_API_KEY,
    temperature=0.7,
    streaming=True
)

tools = [record_user_preference, find_dog_breed_matches, get_breed_details]
llm_with_tools = llm.bind_tools(tools)

# Create prompt template (same as CLI)
assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{messages}")
])

from langgraph.prebuilt import ToolNode

# Assistant class (same as CLI)
class Assistant:
    def __init__(self, runnable):
        self.runnable = runnable
    
    def __call__(self, state: DogMatcherState):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content or 
                isinstance(result.content, list) and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Please respond to the user.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}

# Build graph (exact same as CLI)
builder = StateGraph(DogMatcherState)
builder.add_node("assistant", Assistant(assistant_prompt | llm_with_tools))
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")

def should_continue(state: DogMatcherState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("assistant", should_continue, ["tools", END])
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory, debug=False)

# Store active conversations
conversations = {}

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Get session_id from client (stored in localStorage)
        session_id = data.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"🆕 NEW SESSION CREATED: {session_id}")
        else:
            print(f"♻️ EXISTING SESSION: {session_id}")
        
        config = {"configurable": {"thread_id": session_id}, "recursion_limit": 50}
        
        print(f"📝 User message: {user_message}")
        print(f"🔧 Config: {config}")
        
        # Track printed messages to avoid duplicates
        printed_contents = set()
        ai_response = ""
        
        # Stream through the graph exactly like CLI
        for event in graph.stream(
            {"messages": [("user", user_message)]},
            config,
            stream_mode="values"
        ):
            if "messages" in event:
                last_message = event["messages"][-1]
                
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content.strip()
                    
                    # Skip if we've already seen this content
                    if content in printed_contents:
                        continue
                    
                    # Only capture AI messages (not tool messages)
                    if hasattr(last_message, 'type') and last_message.type == 'ai':
                        if not hasattr(last_message, 'name') or last_message.name not in ['record_user_preference']:
                            ai_response = content
                            printed_contents.add(content)
        
        if not ai_response:
            ai_response = "Hi there! 🐾 I'm Anna, your friendly dog breed matching assistant! Let's find your perfect furry companion. To start, how important is it that your dog is affectionate with family? 😊"
        
        print(f"🤖 Anna's response: {ai_response[:100]}...")
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id  # Send back to client
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in chat endpoint: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset the conversation"""
    if 'session_id' in session:
        session.pop('session_id')
    return jsonify({'success': True})

@app.route('/api/breed_images', methods=['POST'])
def breed_images():
    """Get image URLs for breed names extracted from match results"""
    try:
        data = request.json
        breeds = data.get('breeds', [])
        scores = data.get('scores', [])
        
        results = []
        for i, breed in enumerate(breeds):
            results.append({
                'breed': breed,
                'score': scores[i] if i < len(scores) else 0,
                'image_url': get_breed_image_url(breed),
                'rank': i + 1
            })
        
        return jsonify({
            'success': True,
            'breeds': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Use port from environment variable for Azure, default to 5001 for local
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
