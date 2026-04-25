from flask import Flask, render_template, send_file, jsonify
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
GEOJSON_PATH = (BASE_DIR / "../../data/fruit_fly_detections.geojson").resolve()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/geojson")
def geojson():
    print("BASE_DIR:", BASE_DIR)
    print("LOOKING FOR:", GEOJSON_PATH)
    print("EXISTS:", GEOJSON_PATH.exists())

    if not GEOJSON_PATH.exists():
        return jsonify({
            "error": "GeoJSON file not found",
            "expected_path": str(GEOJSON_PATH)
        }), 404

    # Do NOT json.load() here.
    # Large GeoJSON files can make the route look like it is not loading.
    return send_file(
        GEOJSON_PATH,
        mimetype="application/geo+json",
        as_attachment=False,
        download_name="fruit_fly_data.geojson"
    )


if __name__ == "__main__":
    print("BASE_DIR:", BASE_DIR)
    print("LOOKING FOR:", GEOJSON_PATH)
    print("EXISTS:", GEOJSON_PATH.exists())
    app.run(debug=True, port=5000)
