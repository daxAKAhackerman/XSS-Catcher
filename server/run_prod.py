from app import create_app, schemas
from waitress import serve

app = create_app()

if __name__ == "__main__":
    schemas.init_app(app)
    serve(app, host="0.0.0.0", port=8080)
