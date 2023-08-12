# Import necessary libraries
import openai
import asyncio
import re
import whisper #To be removed
import boto3
import pydub
import platform
from pydub import playback
import speech_recognition as sr
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
import numpy as np
from pywhispercpp.model import Model

# Initialize the OpenAI API
openai.api_key = "[paste your OpenAI API key here]"

# Create a recognizer object and wake word variables
recognizer = sr.Recognizer()
BING_WAKE_WORD = "bing"  # Wake word for Bing AI
GPT_WAKE_WORD = "gpt"  # Wake word for Chat GPT

# Function to get wake word
def get_wake_word(phrase):
    if BING_WAKE_WORD in phrase.lower():
        return BING_WAKE_WORD
    elif GPT_WAKE_WORD in phrase.lower():
        return GPT_WAKE_WORD
    else:
        return None

# Function to synthesize speech into audio using Amazon Polly
def synthesize_speech(text):
    polly = boto3.client('polly', region_name='eu-west-2')
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='pcm',
        VoiceId='Arthur',
        Engine='neural'
    )

    audio_data = response['AudioStream'].read()
    return audio_data

# Function to reproduce the audio
def play_audio(synthesize_data):
    # Convert the audio data to numpy array and calculate required padding
    audio = np.frombuffer(synthesize_data, dtype=np.int16)
    sample_width = 2  # Assuming 16-bit audio
    channels = 1  # Mono audio
    padding = (len(audio) % (sample_width * channels))
    if padding > 0:
        padding = (sample_width * channels) - padding
        audio = np.pad(audio, (0, padding), mode='constant')

    playback.play(pydub.AudioSegment(
        data=audio.tobytes(),
        sample_width=sample_width,
        frame_rate=16000,
        channels=channels
    ))

# Function to handle cookies
def get_cookies(url):
    import browser_cookie3
    # List of supported browsers
    browsers = [
        browser_cookie3.edge,
    ]
    for browser_fn in browsers:
        try:
            cookies = []
            cj = browser_fn(domain_name=url)
            for cookie in cj:
                cookies.append(cookie.__dict__)
            return cookies
        except:
            continue

# Check the platform and set the event loop policy if running on Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Get cookies for Bing website
cookies = get_cookies('.bing.com')
# Load the Whisper model using whispercpp wrap
whisper_model = Model('tiny')

# Main function for the voice assistant
async def main():
    while True:
        # Listening for wake words
        with sr.Microphone(sample_rate=16000) as source:
            recognizer.adjust_for_ambient_noise(source)
            print("\nWaiting for wake words 'ok bing' or 'ok chat'...")

            while True:
                audio = recognizer.listen(source)
                audio = audio.get_wav_data()
                audio_data = (np.frombuffer(audio, dtype=np.int16).astype(np.float32)) / (2 ** 15)

                try:
                    result = whisper_model.transcribe(media=audio_data.flatten())
                    phrase = ""
                    for segment in result:
                        phrase += segment.text
                    print(f"You said: {phrase}")
                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print("Not a wake word. Try again.")
                except Exception as e:
                    print("Error transcribing audio:", e)
                    continue

            # Synthesize and play the wake word acknowledgment
            synthesize_speech_data = synthesize_speech('What can I help you with?')
            play_audio(synthesize_speech_data)

            print("Speak a prompt...")
            # Listening for user input
            audio = recognizer.listen(source)
            audio = audio.get_wav_data()
            audio_data = (np.frombuffer(audio, dtype=np.int16).astype(np.float32)) / (2 ** 15)

            try:
                result = whisper_model.transcribe(audio_data.flatten())
                user_input = result["text"]
                print(f"You said: {user_input}")
            except Exception as e:
                print("Error transcribing audio:", e)
                continue

            # Process the user input based on the wake word
            if wake_word == BING_WAKE_WORD:
                bot = Chatbot(cookies=cookies)
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)
                # Select only the bot response from the response dictionary
                for message in response["item"]["messages"]:
                    if message["author"] == "bot":
                        bot_response = message["text"]
                # Remove [^#^] citations in response
                bot_response = re.sub('\[\^\d+\^\]', '', bot_response)

            else:
                # Send prompt to GPT-3.5-turbo API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                    ],
                    temperature=0.5,
                    max_tokens=150,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    n=1,
                    stop=["\nUser:"],
                )

                bot_response = response["choices"][0]["message"]["content"]

            print("Bot's response:", bot_response)
            # Synthesize and play the bot's response
            synthesize_bot_response_data = synthesize_speech(bot_response)
            play_audio(synthesize_bot_response_data)
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
