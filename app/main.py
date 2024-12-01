from app import create_app
from definition import SSL_CERT_PATH, SSL_KEY_PATH, HOST, PORT, IS_DEVELOPMENT
from app.modules.data_collection import capture_video

if __name__ == 'app.main':
    app = create_app()

    app.run(
        ssl_context=(SSL_CERT_PATH, SSL_KEY_PATH),
        host=HOST,
        port=PORT,
        debug=IS_DEVELOPMENT
    )