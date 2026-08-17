import sys
from fastapi.testclient import TestClient
from src.presentation.api.app import app
from src.presentation.desktop.controllers.main_controller import MainController

client = TestClient(app)

response = client.get("/api/v1/relints")
print("STATUS CODE:", response.status_code)
data = response.json()
print("IS LIST:", isinstance(data, list))
print("ITEM COUNT:", len(data))
if len(data) > 0:
    first = data[0]
    print("FIRST ITEM KEYS:", list(first.keys()))
    print("FIRST ITEM SOURCE FILE:", first.get("source_file"))
    print("FIRST ITEM METHOD:", first.get("extraction_method"))
    print("FIRST ITEM PARTICIPANTS COUNT:", len(first.get("participants", [])))
