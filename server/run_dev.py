from app import create_app, schemas

app = create_app()

if __name__ == "__main__":
    schemas.init_app(app)
    app.run(debug=True)
