from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Officer
from scheduler import assign_counters, shift_summary
from datetime import datetime
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[
                   "*"], allow_methods=["*"], allow_headers=["*"])

# Global officer list
officers: List[Officer] = []

# Counters
counters_arrival = [f"AC{i}" for i in range(1, 41)] + ["AM41", "AM43"]
counters_departure = [f"DC{i}" for i in range(1, 37)] + ["DM37A", "DM37C"]

# WebSocket manager


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

# Add or update officer dynamically


@app.post("/officer")
async def add_update_officer(officer: dict):
    # Check if officer exists
    for o in officers:
        if o.id == officer.get("id"):
            # update existing
            o.name = officer.get("name", o.name)
            o.type = officer.get("type", o.type)
            o.start_time = datetime.fromisoformat(
                officer.get("start_time", o.start_time.isoformat()))
            o.end_time = datetime.fromisoformat(
                officer.get("end_time", o.end_time.isoformat()))
            o.actual_arrival = datetime.fromisoformat(
                officer.get("actual_arrival", o.actual_arrival.isoformat()))
            o.actual_leave = datetime.fromisoformat(
                officer.get("actual_leave", o.actual_leave.isoformat()))
            o.zones = officer.get("zones", o.zones)
            break
    else:
        # add new officer
        o = Officer(
            id=officer.get("id"),
            name=officer.get("name"),
            type=officer.get("type", "SOS"),
            start_time=datetime.fromisoformat(officer.get("start_time")),
            end_time=datetime.fromisoformat(officer.get("end_time")),
            actual_arrival=datetime.fromisoformat(
                officer.get("actual_arrival")),
            actual_leave=datetime.fromisoformat(officer.get("actual_leave")),
            zones=officer.get("zones", [])
        )
        officers.append(o)

    # Broadcast updated schedule to all WebSocket clients
    await broadcast_current_schedule()
    return {"status": "success"}

# Function to broadcast current schedule for all counters


async def broadcast_current_schedule():
    now = datetime.now()
    counters = counters_arrival + counters_departure
    schedule = assign_counters(officers, counters, now)
    await manager.broadcast(schedule)

# WebSocket endpoint for live updates


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Optional: shift summary endpoint


@app.get("/shift-summary/{mode}")
def get_shift_summary(mode: str):
    if mode == "arrival-morning":
        start, end = datetime(2026, 2, 15, 10, 0), datetime(
            2026, 2, 15, 21, 45)
        counters = counters_arrival
    elif mode == "arrival-night":
        start, end = datetime(2026, 2, 15, 22, 0), datetime(2026, 2, 16, 9, 45)
        counters = counters_arrival
    elif mode == "departure-morning":
        start, end = datetime(2026, 2, 15, 10, 0), datetime(
            2026, 2, 15, 21, 45)
        counters = counters_departure
    elif mode == "departure-night":
        start, end = datetime(2026, 2, 15, 22, 0), datetime(2026, 2, 16, 9, 45)
        counters = counters_departure
    else:
        return {"error": "Invalid mode"}
    summary = shift_summary(officers, counters, start, end)
    return summary
