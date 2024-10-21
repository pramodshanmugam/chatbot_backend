from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from datetime import datetime
import requests

import requests

import requests

import requests
import json

def send_to_ollama(prompt):
    """
    Sends a prompt to the locally running Ollama API and returns the bot's response.
    Handles multiple JSON objects returned by the API.
    """
    url = "http://localhost:11434/api/generate"  # Ollama API endpoint

    # Payload that is sent to Ollama (adjust this to fit Ollama's API requirements)
    payload = {
        "model": "llama3.2",  # Model you're using
        "prompt": prompt      # The user's prompt
    }

    # Making a POST request to the local Ollama API
    try:
        response = requests.post(url, json=payload)

        # Split the response text by newlines (assuming newline-delimited JSON objects)
        raw_responses = response.text.strip().splitlines()

        # Concatenate all the 'response' fields from each JSON object
        bot_response = ""
        for raw_json in raw_responses:
            # Parse each JSON object
            try:
                json_obj = json.loads(raw_json)
                bot_response += json_obj.get("response", "")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON object: {e}")
                continue

        return bot_response.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return "Error: Unable to get response from Ollama API"


@api_view(['POST'])
def chat(request):
    message = request.data.get('message')
    session_id = request.data.get('session_id')  # Get session_id from request
    print(session_id)

    # Get or create session based on session_id
    session, created = ChatSession.objects.get_or_create(session_id=session_id)

    # Store user's message
    ChatMessage.objects.create(session=session, role='user', content=message)

    # Get bot response from Ollama (or a placeholder API)
    bot_response = send_to_ollama(message)

    # Store bot's message
    ChatMessage.objects.create(session=session, role='bot', content=bot_response)

    return Response({"response": bot_response})

@api_view(['GET'])
def chat_history(request):
    session_id = request.query_params.get('session_id')  # Get session_id from query params
    session = ChatSession.objects.filter(session_id=session_id).first()

    if session:
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        return Response([{'role': m.role, 'content': m.content, 'timestamp': m.timestamp} for m in messages])
    else:
        return Response([])
