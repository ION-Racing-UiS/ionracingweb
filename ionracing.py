from app import app
import os

if __name__ == "__main__":
    print(os.getcwd())
    app.run(host="0.0.0.0", port=443, ssl_context=("cert.pem", "key.pem"), debug=False)
