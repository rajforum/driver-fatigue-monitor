from app import create_app
from app.config import Config
from definition import SSL_CERT_PATH, SSL_KEY_PATH

if __name__ == 'app.main':
    app = create_app()
    
    app.run(
        ssl_context=(SSL_CERT_PATH, SSL_KEY_PATH),
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.IS_DEVELOPMENT
    )