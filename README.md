# Driver Fatigue Monitoring Solution

This project is a **Driver Fatigue Monitoring Solution** that detects driver fatigue in real-time using biometric and visual data. The application processes input from camera modules and wearable devices, runs it through machine learning models, and triggers alerts when signs of fatigue are detected.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run Locally](#run-locally)
- [License](#license)

## Project Overview

The **Driver Fatigue Monitoring Solution** aims to reduce road accidents by detecting early signs of driver fatigue. The solution captures and processes data from multiple sources (camera and wearable devices), applies fatigue detection algorithms, and triggers notifications when certain fatigue thresholds are crossed.

## Features
- **Real-Time Fatigue Detection**: Detects fatigue based on input from eye movement, head tilt, and heart rate.
- **Alerts and Notifications**: Generates real-time alerts if fatigue levels exceed safe thresholds.
- **Modular Architecture**: The project is divided into modular components, allowing for easy testing, maintenance, and future scalability.
- **Firebase Integration**: Stores user data, authentication, and analytics.
  
## Technologies Used
- **Python 3.x**: Main programming language for the backend.
- **Flask**: Web framework for the API.
- **OpenCV**: Captures and processes image data.
- **scikit-learn**: Machine learning model development.
- **Firebase**: Database, authentication, and analytics.

## Installation

### Prerequisites
- Python 3.x
- [Firebase project setup](https://console.firebase.google.com/)
  
### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rajforum/driver-fatigue-monitor.git
   cd driver-fatigue-monitor
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # For Linux/macOS
   venv\Scripts\activate      # For Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure Firebase**:
   - To set up Firebase credentials, generate private key from Firbase >> Service accounts
   - Replace the path accordingly 

## Configuration

- **Set Up Environment Variables**:
  Create a `.env` file and add environment variables as needed for your local setup.
  
## Run Locally

To run the Flask application:
```bash
flask run
```
The application will start at `http://127.0.0.1:5000`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
