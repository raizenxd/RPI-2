# Web Camera Human Detection Feature

## Overview
The Web Camera Human Detection system is a cutting-edge application that leverages artificial intelligence to detect human presence in real-time. Designed with a user-friendly interface, this system is ideal for surveillance, security, and monitoring purposes. It offers powerful features like email notifications, user management, Google Drive integration, and video recording.

---

## Features

### 1. Real-Time Human Detection
- Uses advanced AI models to detect human presence with high accuracy.
- Provides instant notifications when a human is detected.

### 2. Email Notifications
- Automatically sends email alerts to notify users of human detection.
- Customizable email templates and recipient lists.

### 3. User Management
- Supports multiple users with role-based access control.
- Allows administrators to add, edit, or remove users.

### 4. Google Drive Integration
- Seamlessly connects to Google Drive for cloud storage.
- Automatically uploads recorded videos and snapshots to a designated Drive folder.

### 5. Video Recorder
- Records video footage when a human is detected.
- Stores videos locally and/or in Google Drive.
- Includes playback and export functionalities.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/webcam-human-detection.git
   cd webcam-human-detection
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Google Drive Integration**:
   - Obtain API credentials from Google Cloud Console.
   - Save the credentials file (`credentials.json`) in the project root.

4. **Run the Application**:
   ```bash
   python app.py
   ```

---

## Primary Instructions

### For RCLONE
Open a new terminal and type this command:
```bash
rclone mount gdrive: ~/Desktop/gdrive
```

### For CAMERA RECORDER
**NOTE**: If you're running other Python code, kindly close it. Open a new terminal and type this command:
```bash
sudo python3 /home/pi/Desktop/RPI-2/web-camera-recorder-master/server.py
```

### For CAMERA DETECTION
**NOTE**: If you're running other Python code, kindly close it. Open a new terminal and type this command:
```bash
sudo python3 /home/pi/Desktop/RPI-2/Cam/main.py
```

---

## Configuration

- **Email Notifications**: Configure SMTP settings in the `config.yaml` file.
- **AI Model**: Customize the detection sensitivity in `settings.py`.
- **User Management**: Admins can manage users through the web interface.
- **Google Drive**: Set the target folder for uploads in the settings.

---

## Usage

1. Launch the application using the command line.
2. Access the web interface via `http://localhost:8000`.
3. Configure detection and notification settings as required.
4. Start monitoring and enjoy the automated features!

---

## Requirements

- Python 3.8+
- OpenCV
- TensorFlow or PyTorch (for AI model)
- Google API Client Library
- SMTP server for email notifications

---

## Roadmap

- Add support for additional AI models.
- Enhance user interface for better usability.
- Enable integration with other cloud storage providers.
- Introduce mobile app notifications.

---

## Contribution
We welcome contributions from the community! Please submit pull requests or report issues on our GitHub repository.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

## Contact
For any questions or support, please contact us at support@yourcompany.com.

