import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import requests

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send the response back to WebSocket as it's generated
        async for response_chunk in self.send_to_ollama(message):
            await self.send(text_data=json.dumps({
                'message': response_chunk
            }))

    async def send_to_ollama(self, prompt):
        """
        Sends a prompt to the locally running Ollama API and streams the response
        as it's generated.
        """
        url = "http://localhost:11434/api/generate"  # Ollama API endpoint

        payload = {
            "model": "llama3.2",  # Model you're using
            "prompt": prompt      # The user's prompt
        }

        try:
            response = requests.post(url, json=payload, stream=True)

            # Asynchronously yield the response as it's received
            for raw_chunk in response.iter_lines():
                if raw_chunk:  # If there's a line of data
                    try:
                        # Parse each JSON object from the line
                        json_obj = json.loads(raw_chunk.decode('utf-8'))

                        # Yield each 'response' segment as soon as it arrives
                        await asyncio.sleep(0)  # Yield control back to the event loop
                        yield json_obj.get("response", "")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON object: {e}")
                        continue

        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            yield "Error: Unable to get response from Ollama API"
