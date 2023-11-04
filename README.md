# Automation Hub
A Django-based application designed to bridge PractiTest with AWS SQS, facilitating the creation of JSON configurations for desired test executions.
And more automation tools.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kaltura/practitest-connector.git
   ```
2. Navigate to the project directory:
   ```
   cd practitest-connector
   ```
3. Install Node.js and npm. The method will vary depending on your operating system. For example, on Ubuntu:
   ```
   sudo apt update
   sudo apt install nodejs npm
   ```
   Or on macOS with Homebrew:
   ```
   brew install node
   ```
4. Install the required npm packages (if your project has a `package.json`):
   ```
   npm install
   ```
5. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
6. Run migrations to set up the database:
   ```
   python manage.py migrate
   ```
7. Start the Django development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Open your browser and navigate to `http://localhost:8000/`.
2. Click on "Create New Block" button, set all fields that needed and click Start button.

## Features

- **PractiTest Integration**: The application integrates with PractiTest to manage and execute test cases.
- **Block Management**: Users can create, update, and delete services, each service for each Practitest project ID.
- **Dynamic Views**: The application includes dynamic views for listing and managing services.
- **Front-end Interactivity**: Leveraging Vue.js for interactive UI components.
