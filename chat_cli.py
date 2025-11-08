#!/usr/bin/env python3
"""
🐾 PawMatch - Interactive CLI Chatbot
Chat with Anna to find your perfect dog breed match!
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import uuid
from typing import TypedDict, Annotated
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# LangGraph imports
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Azure OpenAI Configuration - Load from environment variables
# Set these in your .env file or export them in your shell
if not os.getenv("AZURE_OPENAI_ENDPOINT"):
    os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
if not os.getenv("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY", "")
if not os.getenv("AZURE_OPENAI_DEPLOYMENT"):
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
if not os.getenv("AZURE_OPENAI_API_VERSION"):
    os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

print("🐾 Loading PawMatch AI...")
print("=" * 60)

# Load breed data
df = pd.read_csv('data/breed_traits.csv')
print(f"✅ Loaded {len(df)} dog breeds")

# Matching traits
MATCHING_TRAITS = [
    'Affectionate With Family', 'Good With Young Children', 'Good With Other Dogs',
    'Shedding Level', 'Coat Grooming Frequency', 'Openness To Strangers',
    'Playfulness Level', 'Energy Level'
]

# Match breeds function
def match_breeds(preferences: dict, top_n: int = 3) -> pd.DataFrame:
    """Match dog breeds based on user preferences"""
    user_vector = np.array([preferences.get(trait, 3) for trait in MATCHING_TRAITS]).reshape(1, -1)
    breed_vectors = df[MATCHING_TRAITS].values
    similarities = cosine_similarity(user_vector, breed_vectors)[0]
    df['match_score'] = similarities * 100
    return df.nlargest(top_n, 'match_score')[['Breed', 'match_score'] + MATCHING_TRAITS]

# Text to score function
def text_to_score(text: str, trait: str = "") -> int:
    """Convert natural language to 1-5 score
    
    Args:
        text: User's response in natural language
        trait: The trait being asked about (for context-aware scoring)
    """
    text = text.lower().strip()
    trait_lower = trait.lower()
    
    # Context-aware scoring for inverted traits (shedding, grooming)
    # For these traits: higher score = less of the trait preferred
    is_inverted_trait = any(x in trait_lower for x in ['shedding', 'grooming'])
    
    # Very low preference (1)
    if any(word in text for word in ['no', 'none', 'never', 'not at all', 'hate', 'dislike', 'minimal', 'very low']):
        return 5 if is_inverted_trait else 1
    
    # Low preference (2)
    elif any(phrase in text for phrase in ['not much', 'not too much', 'not really', 'little', 'rarely', 'slight', 'low', 'small']):
        return 4 if is_inverted_trait else 2
    
    # Positive expressions for low-maintenance
    elif any(phrase in text for phrase in ['less grooming', 'low maintenance', 'easy care', 'minimal care', 'not shed', "don't shed", 'no shed']):
        return 5  # Want low maintenance
    
    # Medium preference (3)
    elif any(word in text for word in ['medium', 'moderate', 'sometimes', 'okay', 'fine', 'average', 'normal', 'neutral', 'some']):
        return 3
    
    # High preference (4)  
    elif any(word in text for word in ['quite', 'pretty', 'fairly', 'good', 'often', 'high', 'like', 'enjoy']):
        return 4
    
    # Very high preference (5)
    elif any(word in text for word in ['very', 'extremely', 'always', 'love', 'must', 'essential', 'important', 'need', 'maximum', 'super', 'really']):
        return 5
    
    else:
        return 3  # Default to medium

# State definition
class DogMatcherState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_preferences: dict

# Tools
@tool
def record_user_preference(trait: str, preference_text: str) -> str:
    """Record a user's preference for a specific dog trait.
    
    Args:
        trait: The trait name (e.g., 'Affectionate With Family')
        preference_text: The user's preference in natural language
    """
    score = text_to_score(preference_text, trait)
    return f"Recorded: {trait} = {score}/5 (from '{preference_text}')"

@tool
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
    """Find the top 3 dog breeds that match the user's preferences.
    
    Args:
        affectionate_with_family: Score 1-5 for family affection
        good_with_young_children: Score 1-5 for child compatibility
        good_with_other_dogs: Score 1-5 for dog sociability
        shedding_level: Score 1-5 for shedding preference (1=heavy shedding OK, 5=no shedding)
        coat_grooming_frequency: Score 1-5 for grooming (1=high maintenance OK, 5=low maintenance)
        openness_to_strangers: Score 1-5 for stranger friendliness
        playfulness_level: Score 1-5 for playfulness
        energy_level: Score 1-5 for energy level
    """
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
    
    # Normalize breed names (remove non-breaking spaces)
    def normalize_spaces(text):
        return ' '.join(text.split())
    
    result = "� **I found your perfect matches!** 🏆\n\n"
    result += "Here are the top 3 breeds that match your lifestyle:\n\n"
    medals = ['🥇', '🥈', '🥉']
    for i, (_, breed) in enumerate(matches.iterrows()):
        breed_name = normalize_spaces(breed['Breed'])
        result += f"{medals[i]} **{breed_name}** - {breed['match_score']:.1f}% match\n"
    
    result += "\n✨ These breeds are tailored to your preferences! Want to know more about any of them?"
    return result

@tool
def get_breed_details(breed_name: str) -> str:
    """Get detailed information about a specific dog breed.
    
    Args:
        breed_name: The name of the dog breed
    """
    # Normalize spaces (handle non-breaking spaces)
    def normalize_spaces(text):
        return ' '.join(text.split())
    
    breed_name_normalized = normalize_spaces(breed_name)
    
    # Try exact match first
    breed_data = df[df['Breed'].apply(normalize_spaces) == breed_name_normalized]
    
    # If not found, try case-insensitive match
    if breed_data.empty:
        breed_data = df[df['Breed'].apply(lambda x: normalize_spaces(x).lower()) == breed_name_normalized.lower()]
    
    # If still not found, try removing 's' from end (handle plurals)
    if breed_data.empty and breed_name_normalized.endswith('s'):
        singular = breed_name_normalized[:-1]
        breed_data = df[df['Breed'].apply(lambda x: normalize_spaces(x).lower()) == singular.lower()]
    
    # If still not found, try partial match
    if breed_data.empty:
        breed_data = df[df['Breed'].apply(normalize_spaces).str.contains(breed_name_normalized, case=False, na=False)]
    
    if breed_data.empty:
        return f"Breed '{breed_name}' not found in our database of 195 AKC breeds."
    
    breed = breed_data.iloc[0]
    breed_name_display = normalize_spaces(breed['Breed'])
    details = f"**{breed_name_display}**\n\n"
    for trait in MATCHING_TRAITS:
        stars = '⭐' * int(breed[trait])
        details += f"• {trait}: {stars} ({int(breed[trait])}/5)\n"
    return details

# Create tools list
dog_matcher_tools = [record_user_preference, find_dog_breed_matches, get_breed_details]

# LLM setup
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    temperature=0.7,
    streaming=True
)

# Bind tools
llm_with_tools = llm.bind_tools(dog_matcher_tools)

# System prompt
assistant_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Anna, a friendly and enthusiastic dog matchmaker! 🐾

**Your Capabilities:**
1. **Find Perfect Match**: Help users find their ideal dog by asking about 8 traits
2. **Breed Information**: Answer questions about specific dog breeds
3. **General Advice**: Provide dog-related guidance and information

**How to Start Conversations:**
- Introduce yourself briefly: "Hi! I'm Anna 🐾 I can help you find your perfect dog match or answer questions about specific breeds. What would you like to know?"
- Let the user guide the conversation
- If they want a match, start the questionnaire
- If they ask about a breed, use get_breed_details immediately
- Be flexible and conversational

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

**Matching Process:**
- Ask about ONE trait at a time in NATURAL LANGUAGE
- NEVER ask for scales or numbers (1-5)
- Use casual phrasing: "How affectionate would you like your dog to be?" NOT "Rate from 1-5"
- Accept natural answers: "very", "a lot", "not much", "medium", "I don't care", etc.
- Internally convert each answer to 1-5 score using this logic:
  * "very"/"love"/"extremely"/"high" → 5
  * "quite"/"pretty"/"good" → 4  
  * "medium"/"okay"/"moderate" → 3
  * "little"/"not much"/"low" → 2
  * "no"/"none"/"not at all" → 1
- After collecting all 8 traits, call find_dog_breed_matches with 8 individual scores
- Call it like: find_dog_breed_matches(affectionate_with_family=5, good_with_young_children=3, ...)
- Show results and STOP - don't ask more questions

**Important Rules:**
- NEVER ask for numerical ratings or scales
- NEVER repeat previous responses
- Keep responses SHORT (2-3 sentences max)
- Be natural and conversational like a human matchmaker
- After showing matches, WAIT for user to ask follow-up questions
- When user asks about a breed, remove 's' for plural forms

**Good Question Examples:**
- "How affectionate would you like your dog to be with your family?"
- "Do you have young children at home? How important is it that the dog is good with kids?"
- "What about shedding - does it bother you or not a big deal?"
- "How much grooming are you willing to do?"

**Bad Question Examples (DON'T USE):**
- "Rate affection from 1 to 5"
- "On a scale of 1-5, how..."
- "Please rate..."

Let's help them find their perfect furry friend! 🐕"""),
    ("placeholder", "{messages}")
])

# Assistant class
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

# Build graph
builder = StateGraph(DogMatcherState)
builder.add_node("assistant", Assistant(assistant_prompt | llm_with_tools))
builder.add_node("tools", ToolNode(dog_matcher_tools))
builder.add_edge(START, "assistant")

def should_continue(state: DogMatcherState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("assistant", should_continue, ["tools", END])
builder.add_edge("tools", "assistant")

# Compile with memory and increased recursion limit
memory = MemorySaver()
dog_matcher_graph = builder.compile(
    checkpointer=memory,
    debug=False
)

print("✅ Anna is ready to chat!")
print("=" * 60)
print()

# Interactive CLI
def chat_cli():
    """Interactive command-line chat with Anna"""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("🐾 Welcome to PawMatch!")
    print("💬 Type your messages below (or 'quit' to exit)")
    print("=" * 60)
    print()
    
    # Start with Anna's greeting
    initial_message = "start"
    print("Connecting to Anna...")
    print()
    
    # Get initial response
    printed_messages = set()
    printed_contents = set()  # Track actual content to avoid duplicates
    
    # Add recursion limit to config
    config["recursion_limit"] = 50
    
    for event in dog_matcher_graph.stream(
        {"messages": [("user", initial_message)]},
        config,
        stream_mode="values"
    ):
        if "messages" in event:
            last_message = event["messages"][-1]  # Only check the last message
            msg_id = id(last_message)
            
            if msg_id not in printed_messages:
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content.strip()
                    
                    # Skip if we've already printed this exact content
                    if content in printed_contents:
                        continue
                    
                    # Only print AI messages, skip human and tool messages
                    if hasattr(last_message, 'type') and last_message.type == 'ai':
                        if not hasattr(last_message, 'name') or last_message.name not in ['record_user_preference']:
                            print(f"Anna: {content}")
                            print()
                            printed_messages.add(msg_id)
                            printed_contents.add(content)
    
    # Continue conversation
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print()
                print("Anna: Goodbye! Hope you find your perfect furry friend! 🐾")
                break
            
            print()
            
            # Stream the response
            for event in dog_matcher_graph.stream(
                {"messages": [("user", user_input)]},
                config,
                stream_mode="values"
            ):
                if "messages" in event:
                    last_message = event["messages"][-1]  # Only check the last message
                    msg_id = id(last_message)
                    
                    if msg_id not in printed_messages:
                        if hasattr(last_message, 'content') and last_message.content:
                            content = last_message.content.strip()
                            
                            # Skip if we've already printed this exact content
                            if content in printed_contents:
                                continue
                            
                            # Only print AI messages, skip human and tool messages
                            if hasattr(last_message, 'type') and last_message.type == 'ai':
                                if not hasattr(last_message, 'name') or last_message.name not in ['record_user_preference']:
                                    print(f"Anna: {content}")
                                    print()
                                    printed_messages.add(msg_id)
                                    printed_contents.add(content)
        
        except KeyboardInterrupt:
            print("\n\nAnna: Goodbye! Hope you find your perfect furry friend! 🐾")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    try:
        chat_cli()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
