import os
import time
import json
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

class ConversationGenerator:
    def __init__(self):
        self.voices = self.get_available_voices()
        self.conversation = []
        self.agent_voice = None
        self.customer_voice = None
    
    def get_available_voices(self):
        try:
            return Voices.from_api()
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
    def list_available_voices(self):
        if not self.voices:
            print("No voices available or couldn't retrieve voices.")
            return
        
        print("\nAvailable Voices:")
        print("----------------")
        for i, voice in enumerate(self.voices):
            print(f"{i+1}. {voice.name}")
    
    def select_voices(self):
        self.list_available_voices()
        
        if not self.voices:
            print("Using default voice names since no voices could be retrieved.")
            self.agent_voice = "Daniel"
            self.customer_voice = "Rachel"
            return
        
        # Agent voice selection
        while True:
            try:
                agent_choice = int(input("\nSelect voice number for the agent: ")) - 1
                if 0 <= agent_choice < len(self.voices):
                    self.agent_voice = self.voices[agent_choice]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Customer voice selection
        while True:
            try:
                customer_choice = int(input("Select voice number for the customer: ")) - 1
                if 0 <= customer_choice < len(self.voices):
                    self.customer_voice = self.voices[customer_choice]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        print(f"\nSelected voices: Agent = {self.agent_voice.name}, Customer = {self.customer_voice.name}")
    
    def create_conversation(self):
        print("\nLet's create a conversation between an agent and a customer.")
        print("Type 'done' when you've finished adding all lines to the conversation.")
        
        line_number = 1
        while True:
            print(f"\nLine {line_number}:")
            role = input("Who is speaking? (agent/customer/done): ").lower()
            
            if role == "done":
                break
            
            if role not in ["agent", "customer"]:
                print("Invalid role. Please enter 'agent' or 'customer'.")
                continue
            
            text = input(f"Enter {role}'s line: ")
            if not text:
                print("Text cannot be empty. Please try again.")
                continue
            
            self.conversation.append({"role": role, "text": text})
            line_number += 1
        
        return self.conversation
    
    def save_conversation_to_file(self, filename="conversation.json"):
        if not self.conversation:
            print("No conversation to save.")
            return
        
        with open(filename, "w") as f:
            json.dump(self.conversation, f, indent=4)
        
        print(f"\nConversation saved to {filename}")
    
    def load_conversation_from_file(self, filename="conversation.json"):
        try:
            with open(filename, "r") as f:
                self.conversation = json.load(f)
            
            print(f"\nConversation loaded from {filename}")
            self.print_conversation()
            return True
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return False
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}.")
            return False
    
    def print_conversation(self):
        if not self.conversation:
            print("No conversation to display.")
            return
        
        print("\nCurrent Conversation:")
        print("--------------------")
        for i, line in enumerate(self.conversation):
            print(f"{i+1}. {line['role'].capitalize()}: {line['text']}")
    
    def generate_audio(self, output_dir="audio_output", play_audio=True):
        if not self.conversation:
            print("No conversation to generate audio for.")
            return
        
        if not self.agent_voice or not self.customer_voice:
            print("Voices not selected. Please select voices first.")
            self.select_voices()
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("\nGenerating conversation audio files...")
        
        for i, line in enumerate(self.conversation):
            role = line["role"]
            text = line["text"]
            
            # Select voice based on role
            voice = self.agent_voice if role == "agent" else self.customer_voice
            
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
                filename = f"{output_dir}/{i+1:02d}_{role}_{text[:20].replace(' ', '_').replace('?', '').replace('!', '')}.mp3"
                
                # Initialize audio data for saving
                audio_data = bytes()
                
                # Stream and collect audio data
                print("Streaming audio...")
                for chunk in audio_stream:
                    if play_audio:
                        # In a real application, you would play this chunk in real-time
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

def main():
    print("ElevenLabs API Conversation Generator (Streaming)")
    print("===============================================")
    
    generator = ConversationGenerator()
    
    while True:
        print("\nMenu:")
        print("1. Create new conversation")
        print("2. Load conversation from file")
        print("3. Save current conversation to file")
        print("4. Display current conversation")
        print("5. Select voices")
        print("6. Generate audio")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            generator.create_conversation()
        elif choice == "2":
            filename = input("Enter filename to load (default: conversation.json): ") or "conversation.json"
            generator.load_conversation_from_file(filename)
        elif choice == "3":
            filename = input("Enter filename to save (default: conversation.json): ") or "conversation.json"
            generator.save_conversation_to_file(filename)
        elif choice == "4":
            generator.print_conversation()
        elif choice == "5":
            generator.select_voices()
        elif choice == "6":
            output_dir = input("Enter output directory (default: audio_output): ") or "audio_output"
            play_option = input("Play audio while streaming? (y/n, default: y): ").lower() or "y"
            play_audio = play_option.startswith("y")
            generator.generate_audio(output_dir, play_audio)
        elif choice == "7":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 