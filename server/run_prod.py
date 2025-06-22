from app import create_app, models
from waitress import serve

app = create_app()

if __name__ == "__main__":
    models.init_app(app)
    serve(app, host="0.0.0.0", port=8080)
