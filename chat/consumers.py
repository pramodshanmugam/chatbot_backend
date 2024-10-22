import json
import httpx
import asyncio  # <-- Add this import for asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        message = json.loads(text_data).get('message')
        session_id = json.loads(text_data).get('session_id')

        # Send the user's message to the Ollama API
        async for bot_message in self.send_to_ollama(message):
            await self.send(text_data=json.dumps({
                'message': bot_message
            }))

    async def send_to_ollama(self, prompt):
        """
        Sends a prompt to the locally running Ollama API and streams the response.
        """
        url = "http://localhost:11434/api/generate"  # Ollama API endpoint

        payload = {
            "model": "llama3.2",  # Model you're using
            "prompt": prompt      # The user's prompt
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=payload) as response:
                    async for raw_chunk in response.aiter_lines():
                        if raw_chunk:
                            try:
                                # Parse each JSON object from the line
                                json_obj = json.loads(raw_chunk)
                                # print(json_obj)
                                # Yield each 'response' segment as soon as it arrives
                                bot_message = json_obj.get("response", "")
                                await asyncio.sleep(0)  # Yield control to the event loop
                                yield bot_message

                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON object: {e}")
                                continue

        except httpx.RequestError as e:
            print(f"Error calling Ollama API: {e}")
            yield "Error: Unable to get response from Ollama API"
