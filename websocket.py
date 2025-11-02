"""
WebSocket module for real-time communication
"""
from fastapi import WebSocket
from typing import Dict, List
import json
from datetime import datetime


class ConnectionManager:
    """WebSocket connection manager for real-time tracking"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "drivers": [],      # Driver location updates
            "dispatchers": [],  # Dispatcher monitoring
            "riders": []        # Rider ride tracking
        }

    async def connect(self, websocket: WebSocket, client_type: str):
        await websocket.accept()
        if client_type not in self.active_connections:
            self.active_connections[client_type] = []
        self.active_connections[client_type].append(websocket)

    def disconnect(self, websocket: WebSocket, client_type: str):
        if client_type in self.active_connections:
            self.active_connections[client_type].remove(websocket)

    async def broadcast(self, message: str, client_type: str = None):
        """Broadcast message to all clients of specific type or all types"""
        if client_type and client_type in self.active_connections:
            for connection in self.active_connections[client_type]:
                try:
                    await connection.send_text(message)
                except Exception:
                    # Remove dead connections
                    self.active_connections[client_type].remove(connection)
        else:
            # Broadcast to all types
            for client_list in self.active_connections.values():
                for connection in client_list:
                    try:
                        await connection.send_text(message)
                    except Exception:
                        # Remove dead connections
                        for client_type, connections in self.active_connections.items():
                            if connection in connections:
                                connections.remove(connection)
                                break


# Global connection manager instance
manager = ConnectionManager()
