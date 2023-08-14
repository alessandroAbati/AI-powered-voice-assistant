# AI-Powered Voice Assistant

This repository contains code for an AI-powered voice assistant that can interact with users, provide information, and assist with tasks. The project is based on the excellent work of the [Bing-GPT-Voice-Assistant](https://github.com/Ai-Austin/Bing-GPT-Voice-Assistant) repository by [Ai-Austin](https://github.com/Ai-Austin), which served as the foundation for this project. It has been extended to include additional features and capabilities.

## Features

- **Wake Words**: The voice assistant responds to the wake words "ok bing" or "ok chat."

- **Chat Interaction**: With the wake word recognized, users can engage in a conversation with the voice assistant. It uses GPT-3 to provide context-aware responses.

- **Precise Response**: For certain scenarios, the voice assistant utilizes a precise conversation style when interacting with the user.

- **Speech Synthesis**: Responses from the voice assistant are synthesized using Amazon Polly, providing a natural and human-like voice.

## Requirements

To use this voice assistant, you need to fulfill the following requirements:

1. **OpenAI API Key**: You must have an OpenAI API key to enable the GPT-3 chat capabilities. Get your API key by visiting the [OpenAI website](https://beta.openai.com/signup/).

2. **AWS Account and Polly Access**: The voice synthesis feature is powered by Amazon Polly. You need an AWS account and API credentials for Polly to use this feature.

## Getting Started

### Using Conda (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/alessandroAbati/AI-powered-voice-assistant.git
   cd AI-powered-voice-assistant

2. Set up virtual environment with Conda using the provided environment.yml file:

   ```bash
   conda env create -f environment.yml
   conda activate voice-assistant-env

3. Replace [paste your OpenAI API key here] in main.py with your actual OpenAI API key.
4. Run the voice assistant:
   ```bash
   python main.py

### Using Pip

1. Clone the repository:

   ```bash
   git clone https://github.com/alessandroAbati/AI-powered-voice-assistant.git
   cd AI-powered-voice-assistant

2. Set up a virtual environment (optional but recommended)::

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate

3. Install the required packages using pip:
   
   ```bash
   pip install -r requirements.txt

4. Replace [paste your OpenAI API key here] in main.py with your actual OpenAI API key.
   
5. Run the voice assistant:
   ```bash
   python main.py

### Usage

1. Start the voice assistant by running main.py.

2. Use the wake word ("ok bing" or "ok chat") to start the assistant based on the AI you want to use.
   
3. Speak your prompt.

4. The voice assistant will respond based on the prompt using either GPT-3 or Bing AI.

5. Enjoy the interactions with your AI-powered voice assistant!
