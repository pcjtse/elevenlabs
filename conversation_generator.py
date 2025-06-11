import os
import time
from elevenlabs import stream, save, set_api_key
from elevenlabs.api import Voices
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    print("Error: API key not found. Please add your ElevenLabs API key to a .env file.")
    print("ELEVENLABS_API_KEY=your_api_key_here")
    exit(1)

# Set the API key
set_api_key(api_key)

# Get available voices
try:
    voices = Voices.from_api()
    # Select voices for agent and customer
    agent_voice = next((v for v in voices if v.name == "Daniel"), voices[0])
    customer_voice = next((v for v in voices if v.name == "Rachel"), voices[1] if len(voices) > 1 else voices[0])
    
    print(f"Agent voice: {agent_voice.name}")
    print(f"Customer voice: {customer_voice.name}")
except Exception as e:
    print(f"Error getting voices: {e}")
    print("Using default voices instead.")
    agent_voice = "Daniel"
    customer_voice = "Rachel"

# Conversation script
conversation = [
    {"role": "agent", "text": "Thank you for calling customer support. My name is Alex. How may I assist you today?"},
    {"role": "customer", "text": "Hi Alex, I'm having trouble with my recent order. It's been a week and I haven't received any shipping confirmation."},
    {"role": "agent", "text": "I apologize for the inconvenience. I'd be happy to look into that for you. Could you please provide your order number?"},
    {"role": "customer", "text": "Yes, it's order number 78924. I placed it last Monday."},
    {"role": "agent", "text": "Thank you for that information. Let me check the status of your order in our system. Please give me a moment."},
    {"role": "agent", "text": "I've located your order. It appears there was a slight delay in processing due to one item being temporarily out of stock. However, I see that your order has now been shipped and should arrive within the next two days. You should receive an email confirmation shortly."},
    {"role": "customer", "text": "That's a relief. I was concerned because I need those items for an upcoming event this weekend."},
    {"role": "agent", "text": "I completely understand your concern. Rest assured, based on the shipping information, your order will arrive before the weekend. Is there anything else I can help you with today?"},
    {"role": "customer", "text": "No, that's all I needed to know. Thank you for your help."},
    {"role": "agent", "text": "You're very welcome. Thank you for your patience and for being our valued customer. If you have any other questions, don't hesitate to reach out. Have a wonderful day!"}
]

# Function to generate and save audio for each line of the conversation
def generate_conversation(conversation_list, output_dir="audio_output", play_audio=True):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("\nGenerating conversation audio files...")
    
    for i, line in enumerate(conversation_list):
        role = line["role"]
        text = line["text"]
        
        # Select voice based on role
        voice = agent_voice if role == "agent" else customer_voice
        
        # Print current line being processed
        print(f"\nProcessing: {role.capitalize()}: {text}")
        
        try:
            # Generate audio using streaming
            audio_stream = stream(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2",
                stream=True
            )
            
            # Create filename for saving
            filename = f"{output_dir}/{i+1:02d}_{role}_{text[:20].replace(' ', '_')}.mp3"
            
            # Initialize audio data for saving
            audio_data = bytes()
            
            # Stream and collect audio data
            print("Streaming audio...")
            for chunk in audio_stream:
                if play_audio:
                    # In a real application, you would play this chunk
                    # For demonstration purposes, we're just printing progress
                    print(".", end="", flush=True)
                audio_data += chunk
            
            # Save the collected audio data
            with open(filename, 'wb') as f:
                f.write(audio_data)
            
            print(f"\nSaved: {filename}")
            
            # Small delay to avoid API rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error generating audio for line {i+1}: {e}")
    
    print("\nConversation generation complete!")
    print(f"Audio files saved in '{output_dir}' directory.")

# Main execution
if __name__ == "__main__":
    print("ElevenLabs API Conversation Generator (Streaming)")
    print("===============================================")
    
    # Generate the conversation
    generate_conversation(conversation) 