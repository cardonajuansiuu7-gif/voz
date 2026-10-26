import os

import requests
from flask import Flask, Response, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB por subida

FISH_API = "https://api.fish.audio"
# Modelo del plan gratis de Fish Audio (según su documentación)
FISH_MODEL = os.environ.get("FISH_MODEL", "s2.1-pro-free")


def get_key():
    """La clave llega desde la página en cada petición. El servidor no la guarda ni la registra."""
    return request.headers.get("X-Fish-Key", "").strip()


def explain(status, text):
    if status == 401:
        return "La API key no es válida. Revísala en fish.audio/app/api-keys."
    if status == 402:
        return "Te quedaste sin créditos o el plan no permite esta acción."
    if status == 503:
        return "El servicio de Fish Audio está saturado. Intenta de nuevo en un momento."
    return f"Fish Audio respondió con error {status}: {text[:300]}"


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/voices")
def create_voice():
    key = get_key()
    if not key:
        return jsonify(error="Pega tu API key de Fish Audio en el cuadro de arriba."), 401

    files = request.files.getlist("audios")
    if not files:
        return jsonify(error="Sube al menos un audio de tu voz."), 400

    data = {
        "type": "tts",
        "title": (request.form.get("title") or "Mi voz").strip()[:80],
        "train_mode": "fast",
        "visibility": "private",
        "enhance_audio_quality": "true",
    }
    # La transcripción es opcional: si no se envía, Fish Audio la detecta sola.
    # Solo se acepta con un único audio para que el texto corresponda a ese audio.
    transcript = (request.form.get("texts") or "").strip()
    if transcript and len(files) == 1:
        data["texts"] = transcript

    multipart = [
        ("voices", (f.filename or "voz.mp3", f.stream, f.mimetype or "audio/mpeg"))
        for f in files
    ]

    try:
        r = requests.post(
            f"{FISH_API}/model",
            headers={"Authorization": f"Bearer {key}"},
            data=data,
            files=multipart,
            timeout=180,
        )
    except requests.RequestException as e:
        return jsonify(error=f"No se pudo conectar con Fish Audio: {e}"), 502

    if r.status_code not in (200, 201):
        return jsonify(error=explain(r.status_code, r.text)), r.status_code

    j = r.json()
    return jsonify(id=j.get("_id"), title=j.get("title"), state=j.get("state"))


@app.post("/api/tts")
def tts():
    key = get_key()
    if not key:
        return jsonify(error="Pega tu API key de Fish Audio en el cuadro de arriba."), 401

    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    voice_id = (body.get("reference_id") or "").strip()
    if not text:
        return jsonify(error="Escribe el texto que quieres convertir en voz."), 400
    if not voice_id:
        return jsonify(error="Elige una voz primero."), 400

    try:
        speed = min(2.0, max(0.5, float(body.get("speed", 1))))
    except (TypeError, ValueError):
        speed = 1.0

    payload = {
        "text": text,
        "reference_id": voice_id,
        "format": "mp3",
        "normalize": True,
        "prosody": {"speed": speed, "volume": 0, "normalize_loudness": True},
    }
    lang = (body.get("language") or "").strip()
    if lang and lang != "auto":
        payload["language"] = lang

    try:
        r = requests.post(
            f"{FISH_API}/v1/tts",
            headers={"Authorization": f"Bearer {key}", "model": FISH_MODEL},
            json=payload,
            timeout=300,
        )
    except requests.RequestException as e:
        return jsonify(error=f"No se pudo conectar con Fish Audio: {e}"), 502

    if r.status_code != 200:
        return jsonify(error=explain(r.status_code, r.text)), r.status_code

    return Response(r.content, mimetype="audio/mpeg")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
