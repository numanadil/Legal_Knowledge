import asyncio
import websockets
import json

#WS ok 
#BNS ok
#BSA ok
#IT ok
#WS


async def send_message():
    url = "ws:/127.0.0.1:8001/ws/extension/All"  # your WebSocket URL
    async with websockets.connect(url) as websocket:
        message = {"data": "OTP SCAM on elderly people"}
        await websocket.send(json.dumps(message))
        print("Message sent:", message)

        # Optional: receive a reply from server
        reply = await websocket.recv()
        print("Reply from server:", reply)

# Run the async function
asyncio.run(send_message())
