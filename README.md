# ElevenLabs Conversation Generator

This application uses the ElevenLabs API to generate realistic audio conversations between a customer service agent and a customer.

## Features

- Generate audio for pre-defined conversations
- Create custom conversations through an interactive CLI
- Save and load conversations from JSON files
- Select different voices for the agent and customer
- Generate and save audio files for each line of dialogue
- Combine individual audio files into a single conversation file
- **NEW:** Stream audio in real-time using ElevenLabs' streaming API
- **NEW:** Live playback of conversations with PyAudio

## Requirements

- Python 3.7+
- ElevenLabs API key (sign up at https://elevenlabs.io)
- FFmpeg (required for pydub to combine audio files)
- PortAudio (required for PyAudio for live streaming playback)

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install FFmpeg (required for the audio combiner):
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Mac**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

4. Install PortAudio (required for PyAudio):
   - **Windows**: Should be included with the PyAudio wheel
   - **Mac**: `brew install portaudio`
   - **Linux**: `sudo apt install portaudio19-dev`

5. Create a `.env` file in the root directory with your ElevenLabs API key:

```
ELEVENLABS_API_KEY=your_api_key_here
```

## Usage

### Simple Conversation Generator (Streaming)

Run the basic conversation generator with a predefined script:

```bash
python conversation_generator.py
```

This will generate audio files for a predefined customer service conversation using the ElevenLabs streaming API and save them in the `audio_output` directory.

### Custom Conversation Generator (Streaming)

Run the interactive conversation generator to create your own conversations:

```bash
python custom_conversation.py
```

This provides a menu-driven interface where you can:

1. Create a new conversation
2. Load a conversation from a file (try using the included `sample_conversation.json`)
3. Save the current conversation to a file
4. Display the current conversation
5. Select voices for the agent and customer
6. Generate audio files for the conversation using streaming

### Live Conversation Player (Real-time Streaming)

For real-time streaming and playback of conversations:

```bash
python stream_conversation.py
```

This provides a specialized player that:

1. Loads conversations from JSON files
2. Selects voices for the agent and customer
3. Plays the conversation with real-time audio streaming and playback
4. Optionally saves the audio files while playing

### Combining Audio Files

After generating individual audio files, you can combine them into a single conversation file:

```bash
python combine_audio.py
```

Optional arguments:
- `--input_dir`: Directory containing the MP3 files (default: `audio_output`)
- `--output_file`: Path for the combined audio file (default: `combined_conversation.mp3`)
- `--silence`: Duration of silence between clips in milliseconds (default: 1000)

Example:
```bash
python combine_audio.py --input_dir audio_output --output_file final_conversation.mp3 --silence 800
```

## Example Conversation

The default conversation is a customer service interaction about an order status:

- **Agent**: "Thank you for calling customer support. My name is Alex. How may I assist you today?"
- **Customer**: "Hi Alex, I'm having trouble with my recent order. It's been a week and I haven't received any shipping confirmation."
- **Agent**: "I apologize for the inconvenience. I'd be happy to look into that for you. Could you please provide your order number?"
- ...and so on.

A sample technical support conversation is also included in `sample_conversation.json`.

## Audio Output

Audio files are saved in the `audio_output` directory (or a custom directory of your choice) with filenames indicating the line number, speaker role, and the beginning of the text.

Example: `01_agent_Thank_you_for_call.mp3`

## Streaming vs. Non-Streaming

This application has been updated to use ElevenLabs' streaming API, which offers several advantages:

- **Real-time processing**: Audio is generated and can be played in chunks as they arrive
- **Faster perceived response**: The first chunks of audio can be played before the entire audio is generated
- **More efficient resource usage**: Streaming requires less memory as the entire audio doesn't need to be stored at once
- **Better user experience**: Users hear the audio sooner, making the interaction feel more responsive 