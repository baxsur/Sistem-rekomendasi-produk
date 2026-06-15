from app import create_app

app = create_app()

if __name__ == "__main__":
    # ubah host/port/debug sesuai kebutuhan
    app.run(host="127.0.0.1", port=5000, debug=True)