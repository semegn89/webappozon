from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="Simple Working API")

# ПРОСТОЙ CORS - разрешаем всё
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ПРОСТОЕ хранилище - будет сбрасываться, но работать стабильно
models = [
    {"id": 1, "name": "Test Model 1", "description": "Test", "category": "test", "brand": "Test", "code": "T1", "is_active": True, "created_at": "2024-01-01T00:00:00Z"},
    {"id": 2, "name": "Test Model 2", "description": "Test", "category": "test", "brand": "Test", "code": "T2", "is_active": True, "created_at": "2024-01-01T00:00:00Z"},
    {"id": 3, "name": "Test Model 3", "description": "Test", "category": "test", "brand": "Test", "code": "T3", "is_active": True, "created_at": "2024-01-01T00:00:00Z"},
]

files = [
    {"id": 1, "model_id": 1, "filename": "test.pdf", "file_size": 1024, "mime_type": "application/pdf", "comment": "", "created_at": "2024-01-01T00:00:00Z"},
]

tickets = [
    {"id": 1, "subject": "Test Ticket", "description": "Test", "status": "open", "priority": "normal", "user_id": 1, "model_id": 1, "created_at": "2024-01-01T00:00:00Z"},
]

messages = [
    {"id": 1, "ticket_id": 1, "user_id": 1, "message": "Test message", "created_at": "2024-01-01T00:00:00Z"},
]

# ПРОСТЫЕ ENDPOINTS
@app.get("/")
def root():
    return {"message": "Simple API works"}

@app.get("/api/v1/models")
def get_models():
    return {"models": models}

@app.post("/api/v1/models")
def create_model(data: dict):
    new_id = max([m["id"] for m in models], default=0) + 1
    new_model = {
        "id": new_id,
        "name": data.get("name", "New Model"),
        "description": data.get("description", ""),
        "category": data.get("category", ""),
        "brand": data.get("brand", ""),
        "code": data.get("code", f"M{new_id}"),
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }
    models.append(new_model)
    return new_model

@app.get("/api/v1/models/{model_id}")
def get_model(model_id: int):
    for model in models:
        if model["id"] == model_id:
            return model
    raise HTTPException(404, "Model not found")

@app.put("/api/v1/models/{model_id}")
def update_model(model_id: int, data: dict):
    for i, model in enumerate(models):
        if model["id"] == model_id:
            models[i].update({
                "name": data.get("name", model["name"]),
                "description": data.get("description", model["description"]),
                "category": data.get("category", model["category"]),
                "brand": data.get("brand", model["brand"]),
                "code": data.get("code", model["code"]),
            })
            return models[i]
    raise HTTPException(404, "Model not found")

@app.delete("/api/v1/models/{model_id}")
def delete_model(model_id: int):
    for i, model in enumerate(models):
        if model["id"] == model_id:
            models.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Model not found")

@app.get("/api/v1/models/{model_id}/files")
def get_model_files(model_id: int):
    return [f for f in files if f["model_id"] == model_id]

@app.post("/api/v1/models/{model_id}/files")
def upload_file(model_id: int, data: dict):
    new_id = max([f["id"] for f in files], default=0) + 1
    new_file = {
        "id": new_id,
        "model_id": model_id,
        "filename": data.get("filename", "file.pdf"),
        "file_size": data.get("file_size", 1024),
        "mime_type": data.get("mime_type", "application/pdf"),
        "comment": data.get("comment", ""),
        "created_at": "2024-01-01T00:00:00Z"
    }
    files.append(new_file)
    return new_file

@app.get("/api/v1/tickets")
def get_tickets():
    return {"tickets": tickets}

@app.post("/api/v1/tickets")
def create_ticket(data: dict):
    new_id = max([t["id"] for t in tickets], default=0) + 1
    new_ticket = {
        "id": new_id,
        "subject": data.get("subject", "New Ticket"),
        "description": data.get("description", ""),
        "status": "open",
        "priority": "normal",
        "user_id": data.get("user_id", 1),
        "model_id": data.get("model_id"),
        "created_at": "2024-01-01T00:00:00Z"
    }
    tickets.append(new_ticket)
    return new_ticket

@app.get("/api/v1/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise HTTPException(404, "Ticket not found")

@app.get("/api/v1/tickets/{ticket_id}/messages")
def get_messages(ticket_id: int):
    return [m for m in messages if m["ticket_id"] == ticket_id]

@app.post("/api/v1/tickets/{ticket_id}/messages")
def create_message(ticket_id: int, data: dict):
    new_id = max([m["id"] for m in messages], default=0) + 1
    new_message = {
        "id": new_id,
        "ticket_id": ticket_id,
        "user_id": data.get("user_id", 1),
        "message": data.get("body", data.get("message", "")),
        "created_at": "2024-01-01T00:00:00Z"
    }
    messages.append(new_message)
    return new_message

@app.get("/api/v1/admin/stats")
def get_stats():
    return {
        "models_count": len(models),
        "tickets_count": len(tickets),
        "files_count": len(files),
        "users_count": 1
    }

@app.post("/api/v1/auth/verify")
def verify_auth():
    return {"valid": True, "user": {"id": 1, "name": "Test User"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)