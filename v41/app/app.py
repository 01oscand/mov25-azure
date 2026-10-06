from flask import Flask, request, redirect, url_for, render_template_string
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import json
import os
import requests
import uuid

app = Flask(__name__)

STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT"]
CONTAINER_NAME = os.getenv("CONTAINER_NAME", "felanmalningar")
FLOW_URL = os.environ["POWER_AUTOMATE_URL"]
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")

credential = DefaultAzureCredential(
    managed_identity_client_id=AZURE_CLIENT_ID
)

blob_service = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
    credential=credential
)

container = blob_service.get_container_client(CONTAINER_NAME)


def current_user():
    return request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")


FORM_HTML = """
<!doctype html>
<html lang="sv">
<head>
    <meta charset="utf-8">
    <title>Nordvik Fastigheter - Felanmälan</title>
</head>
<body>
    <h1>Nordvik Fastigheter</h1>
    <h2>Felanmälan</h2>

    <p>Inloggad som: {{ user }}</p>
    <p><a href="/mina">Mina felanmälningar</a></p>

    <form method="post"
          action="/submit"
          enctype="multipart/form-data">

        <label>Rubrik</label><br>
        <input type="text" name="title" required>
        <br><br>

        <label>Fastighet</label><br>
        <input type="text" name="property" required>
        <br><br>

        <label>Kategori</label><br>
        <select name="category" required>
            <option>Värme</option>
            <option>Vatten</option>
            <option>Lås</option>
            <option>El</option>
            <option>Ventilation</option>
            <option>Övrigt</option>
        </select>
        <br><br>

        <label>Beskrivning</label><br>
        <textarea name="description" rows="7" required></textarea>
        <br><br>

        <label>Bild</label><br>
        <input type="file"
               name="image"
               accept=".jpg,.jpeg,.png"
               required>
        <br><br>

        <button type="submit">Skicka felanmälan</button>
    </form>
</body>
</html>
"""


@app.route("/")
def index():
    user = current_user()

    if not user:
        return "Ingen autentiserad användare.", 401

    return render_template_string(
        FORM_HTML,
        user=user
    )


@app.route("/submit", methods=["POST"])
def submit():
    user = current_user()

    if not user:
        return "Ej autentiserad.", 401

    title = request.form["title"]
    description = request.form["description"]
    category = request.form["category"]
    property_name = request.form["property"]
    image = request.files["image"]

    if not image.filename:
        return "Bild saknas.", 400

    filename = secure_filename(image.filename)

    allowed = {"jpg", "jpeg", "png"}
    extension = filename.rsplit(".", 1)[-1].lower()

    if extension not in allowed:
        return "Ogiltig filtyp.", 400

    ticket_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    image_blob = f"images/{ticket_id}-{filename}"

    container.upload_blob(
        name=image_blob,
        data=image.stream,
        overwrite=False,
        content_settings=ContentSettings(
            content_type=image.content_type
        )
    )

    data = {
        "id": ticket_id,
        "timestamp": timestamp,
        "title": title,
        "description": description,
        "category": category,
        "property": property_name,
        "tenant_email": user,
        "image_blob": image_blob,
        "status": "Ny"
    }

    report_blob = f"reports/{ticket_id}.json"

    container.upload_blob(
        name=report_blob,
        data=json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        overwrite=False,
        content_settings=ContentSettings(
            content_type="application/json"
        )
    )

    try:
        requests.post(
            FLOW_URL,
            json=data,
            timeout=10
        ).raise_for_status()
    except Exception as e:
        app.logger.error(f"Power Automate error: {e}")

    return f"""
    <h2>Felanmälan mottagen</h2>
    <p>Ärende-ID: {ticket_id}</p>
    <p><a href="/">Ny felanmälan</a></p>
    <p><a href="/mina">Mina felanmälningar</a></p>
    """


@app.route("/mina")
def mina():
    user = current_user()

    if not user:
        return "Ej autentiserad.", 401

    my_reports = []

    for blob in container.list_blobs(
        name_starts_with="reports/"
    ):
        content = container.download_blob(
            blob.name
        ).readall()

        data = json.loads(
            content.decode("utf-8")
        )

        if data.get("tenant_email") == user:
            my_reports.append(data)

    html = """
    <h1>Mina felanmälningar</h1>
    <p>Inloggad som: {{ user }}</p>

    {% for item in reports %}
        <hr>
        <strong>{{ item.title }}</strong><br>
        Fastighet: {{ item.property }}<br>
        Kategori: {{ item.category }}<br>
        Status: {{ item.status }}<br>
        Ärende-ID: {{ item.id }}
    {% else %}
        <p>Inga felanmälningar.</p>
    {% endfor %}

    <p><a href="/">Tillbaka</a></p>
    """

    return render_template_string(
        html,
        user=user,
        reports=my_reports
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000
    )