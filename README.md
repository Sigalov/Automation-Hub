
# [PractiTest Connector]
A Django-based application designed to bridge PractiTest with AWS SQS, facilitating the creation of JSON configurations for desired test executions.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kaltura/practitest-connector.git
   ```
2. Navigate to the project directory and install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run migrations to set up the database:
   ```
   python manage.py migrate
   ```
4. Start the Django development server:
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

