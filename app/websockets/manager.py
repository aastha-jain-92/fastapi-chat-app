import redis

from app.services.redis_service import get_redis
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # {username: [websockets]}

    async def connect(self, username, websocket):
        await websocket.accept()
        self.active_connections.setdefault(username, []).append(websocket)
        redis = await get_redis()
        await redis.publish("presence",json.dumps({"username": username, "status": "online"}))

    async def disconnect(self, username, websocket):
        if username in self.active_connections:
            self.active_connections[username].remove(websocket)

            if not self.active_connections[username]:
                del self.active_connections[username]
                
                redis = await get_redis()
                await redis.publish("presence", json.dumps({
                    "user": username,
                    "status": "offline"
                }))

    # -----------------------------
    # SEND TO USER (ALL DEVICES)
    # -----------------------------
    async def send_personal_message(self, data: dict, username):
        if username in self.active_connections:
            for connection in self.active_connections[username]:
                try:
                    await connection.send_text(json.dumps(data))
                except RuntimeError:
                    pass
                
    async def broadcast(self, data: dict):
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(data))
                except RuntimeError:
                    pass

     # -----------------------------
    # PUBLISH MESSAGE TO REDIS
    # -----------------------------
    async def publish_message(self, data: dict):
        """
        data = {
            "sender": "A",
            "receiver": "B",
            "message": "hello"
        }
        """
        redis = await get_redis()
        await redis.publish("chat", json.dumps(data))
    
    # -----------------------------
    # REDIS SUBSCRIBER
    # -----------------------------
    async def subscribe(self):
        redis = await get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe("chat")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])
            msg_type = data.get("type")

        # -----------------------
        # HANDLE TYPING EVENT
        # -----------------------
            if msg_type == "typing":
                receiver = data["receiver"]

                payload = {
                "type": "typing",
                "sender": data["sender"]
                }

                if receiver in self.active_connections:
                    for conn in self.active_connections[receiver]:
                        try:
                            await conn.send_text(json.dumps(payload))
                        except RuntimeError:
                            pass

        # -----------------------
        # HANDLE NORMAL MESSAGE
        # -----------------------
            elif msg_type == "message":
                sender = data["sender"]
                receiver = data["receiver"]
                msg = data.get("message", "")

                payload = {
                "type": "message",
                "sender": sender,
                "message": msg
                }

            # send to receiver
                if receiver in self.active_connections:
                    for conn in self.active_connections[receiver]:
                        try:
                            await conn.send_text(json.dumps(payload))
                        except RuntimeError:
                            pass

            # sync sender devices
                if sender in self.active_connections:
                    for conn in self.active_connections[sender]:
                        try:
                            await conn.send_text(json.dumps(payload))
                        except RuntimeError:
                            pass
manager = ConnectionManager()