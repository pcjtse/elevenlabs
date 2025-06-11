import os
import glob
from pydub import AudioSegment
import argparse

def combine_audio_files(input_dir="audio_output", output_file="combined_conversation.mp3", silence_duration=1000):
    """
    Combines all MP3 files in the input directory into a single MP3 file.
    Files are combined in order based on their filename prefix (assumed to be numerical).
    
    Args:
        input_dir (str): Directory containing MP3 files to combine
        output_file (str): Path to save the combined audio file
        silence_duration (int): Duration of silence between clips in milliseconds
    """
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return False
    
    # Get all MP3 files in the directory
    mp3_files = glob.glob(os.path.join(input_dir, "*.mp3"))
    
    if not mp3_files:
        print(f"Error: No MP3 files found in '{input_dir}'.")
        return False
    
    # Sort files by their numerical prefix
    mp3_files.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))
    
    print(f"Found {len(mp3_files)} audio files to combine.")
    
    # Create silence segment
    silence = AudioSegment.silent(duration=silence_duration)
    
    # Start with an empty audio segment
    combined = AudioSegment.empty()
    
    # Add each audio file with silence in between
    for i, mp3_file in enumerate(mp3_files):
        print(f"Adding file {i+1}/{len(mp3_files)}: {os.path.basename(mp3_file)}")
        
        # Load the audio file
        try:
            audio = AudioSegment.from_mp3(mp3_file)
            
            # Add silence if this isn't the first file
            if i > 0:
                combined += silence
            
            # Add the audio
            combined += audio
            
        except Exception as e:
            print(f"Error processing file {mp3_file}: {e}")
            print("Skipping this file and continuing...")
    
    # Export the combined audio
    try:
        combined.export(output_file, format="mp3")
        print(f"\nSuccessfully combined audio files into: {output_file}")
        print(f"Total duration: {len(combined) / 1000:.2f} seconds")
        return True
    except Exception as e:
        print(f"Error exporting combined audio: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Combine multiple MP3 files into a single conversation audio file")
    parser.add_argument("--input_dir", default="audio_output", help="Directory containing MP3 files to combine")
    parser.add_argument("--output_file", default="combined_conversation.mp3", help="Output file path")
    parser.add_argument("--silence", type=int, default=1000, help="Silence duration between clips in milliseconds")
    
    args = parser.parse_args()
    
    print("Audio Combiner for ElevenLabs Conversation Generator")
    print("==================================================")
    
    if combine_audio_files(args.input_dir, args.output_file, args.silence):
        print("Audio combination completed successfully!")
    else:
        print("Audio combination failed.")

if __name__ == "__main__":
    main() 