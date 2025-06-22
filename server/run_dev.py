from app import create_app, models

app = create_app()

if __name__ == "__main__":
    models.init_app(app)
    app.run(debug=True)
