from app import app
from flask import jsonify

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200