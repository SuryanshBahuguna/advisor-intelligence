import json
from intelligence.vector_store import add_text

print("Starting ingestion...\n")


with open("data/mock_clients.json", "r", encoding="utf-8") as f:
    clients = json.load(f)


for client in clients:
    client_id = client.get("client_id", "unknown_id")
    profile = client.get("profile", {})
    client_name = profile.get("name", "Unknown Client")

    conversations = client.get("conversations", [])

    for convo in conversations:
        date = convo.get("date", "")
        summary = convo.get("summary", "")
        key_points = convo.get("key_points", [])

        if key_points:
            key_points_text = ", ".join(key_points)
        else:
            key_points_text = "None"

        
        text = f"""
Client: {client_name}
Date: {date}
Summary: {summary}
Key Points: {key_points_text}
"""

        
        doc_id = f"{client_id}_{date}"

        
        add_text(doc_id, text, {"client_id": client_id})

    print(f"Indexed conversations for {client_name}")

print("\nIngestion complete.")

