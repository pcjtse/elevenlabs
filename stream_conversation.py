import os
import json
import time
import pyaudio
import wave
import io
import tempfile
from elevenlabs import stream, set_api_key
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

class LiveConversationPlayer:
    def __init__(self):
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.voices = self.get_available_voices()
        self.conversation = []
        self.agent_voice = None
        self.customer_voice = None
        self.chunk_size = 1024
        self.sample_width = 2  # 16-bit audio
        self.channels = 1  # Mono
        self.rate = 44100  # Sample rate
    
    def get_available_voices(self):
        try:
            return Voices.from_api()
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
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
    
    def select_voices(self):
        if not self.voices:
            print("No voices available. Using default voices.")
            self.agent_voice = "Daniel"
            self.customer_voice = "Rachel"
            return
        
        print("\nAvailable Voices:")
        print("----------------")
        for i, voice in enumerate(self.voices):
            print(f"{i+1}. {voice.name}")
        
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
    
    def play_audio_stream(self, audio_stream):
        """
        Plays audio directly from the stream in real-time
        """
        # We'll use a temporary file to collect the audio chunks
        # This is because the audio chunks from ElevenLabs may not be in a format directly playable by PyAudio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # First, collect all audio chunks
        audio_data = bytes()
        for chunk in audio_stream:
            print(".", end="", flush=True)
            audio_data += chunk
        
        # Save to temporary WAV file for playback
        with open(temp_filename, 'wb') as f:
            f.write(audio_data)
        
        # Open the temporary file for playback
        with wave.open(temp_filename, 'rb') as wf:
            # Get basic info
            sample_width = wf.getsampwidth()
            channels = wf.getnchannels()
            rate = wf.getframerate()
            
            # Open stream
            stream = self.p.open(format=self.p.get_format_from_width(sample_width),
                                 channels=channels,
                                 rate=rate,
                                 output=True)
            
            # Read and play data
            data = wf.readframes(self.chunk_size)
            while data:
                stream.write(data)
                data = wf.readframes(self.chunk_size)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
        
        # Clean up temporary file
        os.unlink(temp_filename)
    
    def play_conversation(self, save_dir=None):
        if not self.conversation:
            print("No conversation to play. Please load a conversation first.")
            return
        
        if not self.agent_voice or not self.customer_voice:
            print("Voices not selected. Please select voices first.")
            self.select_voices()
        
        # Create save directory if specified and it doesn't exist
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        print("\nPlaying conversation...\n")
        
        for i, line in enumerate(self.conversation):
            role = line["role"]
            text = line["text"]
            
            # Select voice based on role
            voice = self.agent_voice if role == "agent" else self.customer_voice
            
            # Print current line before playing
            print(f"{role.capitalize()}: {text}")
            
            try:
                # Generate audio using streaming
                audio_stream = stream(
                    text=text,
                    voice=voice,
                    model="eleven_multilingual_v2",
                    stream=True
                )
                
                # Play the audio stream in real-time
                print("Playing: ", end="", flush=True)
                self.play_audio_stream(audio_stream)
                print(" Done.")
                
                # Save audio if directory specified
                if save_dir:
                    # Re-generate the audio for saving (since we already consumed the stream)
                    audio_stream = stream(
                        text=text,
                        voice=voice,
                        model="eleven_multilingual_v2",
                        stream=True
                    )
                    
                    # Create filename for saving
                    filename = f"{save_dir}/{i+1:02d}_{role}_{text[:20].replace(' ', '_').replace('?', '').replace('!', '')}.mp3"
                    
                    # Initialize audio data for saving
                    audio_data = bytes()
                    for chunk in audio_stream:
                        audio_data += chunk
                    
                    # Save the collected audio data
                    with open(filename, 'wb') as f:
                        f.write(audio_data)
                    
                    print(f"Saved: {filename}")
                
                # Small delay between lines
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing line {i+1}: {e}")
        
        print("\nConversation playback complete!")
    
    def cleanup(self):
        # Terminate PyAudio instance
        self.p.terminate()

def main():
    print("ElevenLabs Live Conversation Player")
    print("=================================")
    
    player = LiveConversationPlayer()
    
    try:
        # Menu loop
        while True:
            print("\nMenu:")
            print("1. Load conversation from file")
            print("2. Select voices")
            print("3. Play conversation (live streaming)")
            print("4. Play and save conversation")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                filename = input("Enter filename to load (default: conversation.json): ") or "conversation.json"
                player.load_conversation_from_file(filename)
            elif choice == "2":
                player.select_voices()
            elif choice == "3":
                player.play_conversation()
            elif choice == "4":
                save_dir = input("Enter directory to save audio files (default: audio_output): ") or "audio_output"
                player.play_conversation(save_dir)
            elif choice == "5":
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    finally:
        # Clean up resources
        player.cleanup()

if __name__ == "__main__":
    main() 