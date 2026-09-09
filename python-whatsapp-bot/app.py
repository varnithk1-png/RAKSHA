from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json

app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

@app.route('/api/victims')
def get_victims():
    file_path = os.path.join('data', 'live_victims.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"type": "FeatureCollection", "features": []})

@app.route('/api/clear_victim', methods=['POST'])
def clear_victim():
    data = request.get_json()
    victim_id = data.get('victim_id')
    file_path = os.path.join('data', 'live_victims.json')
    
    if os.path.exists(file_path) and victim_id:
        with open(file_path, 'r') as f:
            geojson = json.load(f)
        
        updated_features = [
            f for f in geojson.get('features', [])
            if str(f.get('properties', {}).get('victim_id')) != str(victim_id)
        ]
        geojson['features'] = updated_features
        
        with open(file_path, 'w') as f:
            json.dump(geojson, f, indent=2)
            
        return jsonify({"status": "success", "message": f"Victim {victim_id} cleared"})
    
    return jsonify({"status": "error", "message": "Victim not found"}), 400

if __name__ == '__main__':
    app.run(port=8000, debug=True)
