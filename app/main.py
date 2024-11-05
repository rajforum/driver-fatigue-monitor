from dotenv import load_dotenv
from app import create_app
from app.modules.data_collection import capture_video


load_dotenv()  # Load environment variables

app = create_app()

if __name__ == 'app.main':
    app.run(debug=True)  # Set debug=False in production

    # Start the camera capture when the app is run
    capture_video()

