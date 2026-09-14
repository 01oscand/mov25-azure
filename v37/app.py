from flask import Flask, request
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timezone
import json
import os
import uuid

app = Flask(__name__)

STORAGE_ACCOUNT = "stnovatrixoscar"
CONTAINER = "arenden"

credential = DefaultAzureCredential()

account_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"

blob_service = BlobServiceClient(
    account_url=account_url,
    credential=credential
)

container_client = blob_service.get_container_client(CONTAINER)


@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name", "")
    mail = request.form.get("mail", "")
    msg = request.form.get("msg", "")

    ticket_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    data = {
        "id": ticket_id,
        "timestamp": timestamp,
        "name": name,
        "mail": mail,
        "message": msg
    }

    json_blob_name = f"{ticket_id}/arende.json"

    container_client.upload_blob(
        name=json_blob_name,
        data=json.dumps(data, ensure_ascii=False, indent=2),
        overwrite=True
    )

    bild = request.files.get("bild")

    if bild and bild.filename:
        filename = os.path.basename(bild.filename)

        container_client.upload_blob(
            name=f"{ticket_id}/{filename}",
            data=bild.stream,
            overwrite=True
        )

    return "Ärendet har sparats. Tack!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)