# Calendar App

A web-based application built with Django that allows users to securely sign in using their Microsoft accounts and view their Outlook Calendar events. The app integrates with Microsoft Graph API for authentication and calendar access, providing a user-friendly dashboard to display upcoming events.

---

## Features

- **Microsoft Login Integration**  
  Sign in using your Microsoft account with OAuth2 authentication.

- **Secure OAuth2 with Microsoft Graph**  
  Uses Microsoft's official Graph API for secure and reliable access to calendar data.

- **Display Calendar Events**  
  View your next 10 upcoming Outlook Calendar events in a clean and organized interface.

- **User-Friendly Dashboard**  
  Intuitive design with Bootstrap for seamless navigation and interaction.

- **Environment Variable Support**  
  Configuration settings are managed securely using a `.env` file.

- **Django Best Practices**  
  Follows Django's recommended project structure, including views, templates, and URL routing.

---

## 📸 Screenshot

![Calendar View](screenshots/calender%20app.png)

---

## Technologies Used

- **Backend Framework**: Django 5.1  
- **Frontend**: Bootstrap 5, Font Awesome  
- **API Integration**: Microsoft Graph API  
- **Environment Management**: Python Dotenv  
- **Database**: SQLite (default for development)  
- **HTTP Requests**: Python `requests` library  

---

## Setup Instructions

Follow these steps to set up and run the project locally:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/yourusername/calendar-app.git
   cd calendar-app
   ```

2. **Create a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**  
   Create a `.env` file in the project root and add the following variables:
   ```env
   SECRET_KEY=your-django-secret-key
   MICROSOFT_CLIENT_ID=your-microsoft-client-id
   MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
   MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback/
   MICROSOFT_AUTHORITY=https://login.microsoftonline.com/common
   MICROSOFT_SCOPE=Calendars.Read Calendars.ReadWrite User.Read
   ```

5. **Run Migrations**  
   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server**  
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**  
   Open your browser and navigate to `http://localhost:8000`.

---

## Environment Variables Needed

The following environment variables are required to run the project:

- `SECRET_KEY`: Django's secret key for cryptographic signing.  
- `MICROSOFT_CLIENT_ID`: Your Microsoft app's client ID.  
- `MICROSOFT_CLIENT_SECRET`: Your Microsoft app's client secret.  
- `MICROSOFT_REDIRECT_URI`: Redirect URI for OAuth2 callback.  
- `MICROSOFT_AUTHORITY`: Microsoft login authority URL.  
- `MICROSOFT_SCOPE`: Permissions required for accessing calendar data.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**Iyiola Olubusola**  
Feel free to reach out for questions or contributions:  
- GitHub: [BUSOLA12](https://github.com/BUSOLA12)  
- Email: iyiolaolubusola@gmail.com

---

Contributions are welcome! Please open an issue or submit a pull request if you'd like to improve the project.
