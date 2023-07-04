# Stock Price Prediction

This README file provides a comprehensive guide on setting up and running the Django project. It includes the necessary steps and information to ensure a smooth installation and execution of the project.

## Requirements

To run this Django project, you need to have the following prerequisites:

- Python (version 3.6 or higher)
- Django (version 3.0 or higher)
- Other project-specific requirements listed in the `requirements.txt` file

## Installation

To install and set up the project, please follow the steps below:

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/Atif1727/Stock_price_pridiction.git

2. Change to the project directory:
    ```shell
    cd Kukbit
3. Create a virtual environment (optional but recommended):
    ```shell
    python3 -m venv env
4. Activate the virtual environment:
    For Windows:
    ```shell
    .\env\Scripts\activate
    ```
    For Unix or Linux:
    ```shell
    source env/bin/activate
    
5. Install project dependencies from the requirements.txt file:
    ```shell
    pip install -r requirements.txt
6. Set up the database:
    ```shell
    python manage.py migrate

## Usage
Once the installation steps are completed successfully, you can now run the Django project. Follow the steps below:

1. Start the development server:
    ```shell
    python manage.py runserver
    
2. Open your web browser and visit http://localhost:8000/ to access the project.