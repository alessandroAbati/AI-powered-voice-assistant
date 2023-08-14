# Import necessary libraries
import openai
import asyncio
import re
import boto3
import pydub
import platform
from pydub import playback
import speech_recognition as sr
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
import numpy as np
from pywhispercpp.model import Model
import yaml

# Initialize the OpenAI API
#openai.api_key = "[paste your OpenAI API key here]"
#Retriving the OpenAI API from the config.yml file
with open('config.yml', 'r') as config_file:
    config_file = yaml.safe_load(config_file)
openai.api_key = config_file['OpenAIapiKey']

# Constants
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

# Function to reproduce the audio
def play_audio(audio_data):
    # Convert the audio data to numpy array and calculate required padding
    audio = np.frombuffer(audio_data, dtype=np.int16)
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

# Class to manage ASR
class ASR:
    def __init__(self, model):
        self.model = model

    def transcribe(self, audio_data):
        try:
            result = self.model.transcribe(media=audio_data.flatten())
            phrase = ""
            for segment in result:
                phrase += segment.text
            return phrase
        except Exception as e:
            print("Error transcribing audio:", e)
            return None

# Class to handle voice synthesis using Amazon Polly
class PollySynthesizer:
    def __init__(self):
        self.polly = boto3.client('polly', region_name='eu-west-2')

    def synthesize_speech(self, text):
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat='pcm',
            VoiceId='Arthur',
            Engine='neural'
        )

        audio_data = response['AudioStream'].read()
        return audio_data

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.cookies = get_cookies('.bing.com')
        self.whisper_model = Model('tiny.en')
        self.asr = ASR(self.whisper_model)
        self.synthesizer = PollySynthesizer()

    def listen_for_wake_word(self):
        print("\nWaiting for wake words 'ok bing' or 'ok chat'...")

        while True:
            with sr.Microphone(sample_rate=16000) as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=10)  # Set a timeout for listening
                audio = audio.get_wav_data()
                audio_data = (np.frombuffer(audio, dtype=np.int16).astype(np.float32)) / (2 ** 15)

                try:
                    phrase = self.asr.transcribe(audio_data)
                    print(f"You said: {phrase}")
                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        return wake_word
                    else:
                        print("Not a wake word. Try again.")
                except:
                    print("Error transcribing audio")
                    continue
            
    def listen_for_user_input(self):
        print("Speak a prompt...")

        with sr.Microphone(sample_rate=16000) as source:
            try:
                audio = self.recognizer.listen(source, timeout=10)  # Set a timeout for listening
                audio = audio.get_wav_data()
                audio_data = (np.frombuffer(audio, dtype=np.int16).astype(np.float32)) / (2 ** 15)

                user_input = self.asr.transcribe(audio_data)
                print(f"You said: {user_input}")
                return user_input
            except sr.WaitTimeoutError:
                print("Listening timeout. No user input detected.")
                return None
            except Exception as e:
                print("Error occurred during user input processing:", e)
                return None

    async def handle_bing_assistant(self, user_input):
        bot = Chatbot(cookies=self.cookies)
        response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)
        # Select only the bot response from the response dictionary
        for message in response["item"]["messages"]:
            if message["author"] == "bot":
                bot_response = message["text"]
        # Remove [^#^] citations in response
        bot_response = re.sub(r'\[\^\d+\^\]', '', bot_response)
        await bot.close()
        return bot_response

    def handle_gpt_assistant(self, user_input):
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
        return bot_response

    async def run(self):
        while True:
            wake_word = self.listen_for_wake_word()
            synthesize_speech_data = self.synthesizer.synthesize_speech('What can I help you with?')
            play_audio(synthesize_speech_data)

            #print("Speak a prompt...")
            user_input = self.listen_for_user_input()

            if wake_word == BING_WAKE_WORD:
                bot_response = await self.handle_bing_assistant(user_input)
            else:
                bot_response = self.handle_gpt_assistant(user_input)

            print("Bot's response:", bot_response)
            synthesize_bot_response_data = self.synthesizer.synthesize_speech(bot_response)
            play_audio(synthesize_bot_response_data)

# Initialize and run the voice assistant
if __name__ == "__main__":
    voice_assistant = VoiceAssistant()
    asyncio.run(voice_assistant.run())


