# Interactive Photo Slideshow

## Overview
Interactive Photo Slideshow is a web-based application that allows users to create, manage, and display photo slideshows interactively. It utilizes Flask as the backend framework and includes HTML, CSS, and JavaScript for the frontend.

## Features
- User authentication system
- Interactive slideshow creation
- Admin panel for managing users and slideshows
- Responsive UI with CSS and JavaScript

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.x
- pip (Python package manager)

### Setup
1. Clone this repository:
   ```sh
   git clone <repository-url>
   cd course-project-project-k-group-61-main
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000/`

## File Structure
```
course-project-project-k-group-61-main/
│── app.py                   # Main application script
│── requirements.txt         # Dependencies
│── static/                  # Static files (CSS, videos, etc.)
│   ├── styles.css
│   ├── videos/
│       ├── output_video.mp4
│── templates/               # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── admin.html
│   ├── preview.html
│── opt/render/.postgresql/  # Database SSL certificates
│── .gitignore               # Git ignore file
```
