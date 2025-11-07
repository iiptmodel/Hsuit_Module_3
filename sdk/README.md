# MedAnalyzer Python SDK

This folder contains a minimal Python SDK for interacting with the MedAnalyzer REST API.

Quick start

```python
from sdk.medanalyzer_client import MedAnalyzerClient

client = MedAnalyzerClient(base_url="http://localhost:8000", api_key=None)
session = client.create_session("My API session")
print(session)

# Send a message without file
resp = client.send_message(session_id=session["id"], content="Please review this lab report")
print(resp)
```

Requirements

- Python 3.8+
- requests

Install for development

```powershell
pip install -r sdk/requirements.txt
```
