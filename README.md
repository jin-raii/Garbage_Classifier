### Garbage Classification Kaggle Link : [Notebook Link](https://www.kaggle.com/code/jinrai/gragbage-classifier)
### Model Link : [Drive Link](https://drive.google.com/drive/folders/1GslR2Hw9k7YF1Y6zhIgcd0adAcmAM85A?usp=drive_link)

# Garbage Classification App

## Overview

This web application allows users to upload images of waste and classifies them into different categories. It uses a Django backend with TensorFlow for image classification.

## Features

* **Image Upload:** Users can upload images of waste materials.
* **Garbage Classification:** The application classifies the uploaded images into the following categories:
    * Metal
    * White-glass
    * Biological
    * Paper
    * Brown-glass
    * Battery
    * Trash
    * Cardboard
    * Shoes
    * Clothes
    * Plastic
    * Green-glass
* **Classification Results:** The application displays the classification result to the user.
* **Backend:** Django-based with TensorFlow for image classification.
* **Authentication:** Google login and signup using django-allauth.
* **Models**: Uses MobileNet and VGG16 architectures.

## Technologies Used

* **Frontend:**
    * HTML
    * CSS
    * JavaScript
* **Backend:**
    * Python
    * Django
    * TensorFlow
    * MobileNet
    * VGG16
    * django-allauth
    * uv

## Dataset

The application is trained on a dataset with the following distribution:

* Metal: 769
* White-glass: 775
* Biological: 985
* Paper: 1050
* Brown-glass: 607
* Battery: 945
* Trash: 697
* Cardboard: 891
* Shoes: 1977
* Clothes: 5325
* Plastic: 865
* Green-glass: 629
* Total dataset count: 15515

## Setup

1.  **Clone this repository:**
    * Clone the repository to your local machine.
2.  **Set up the backend (Django) using `uv`:**
    * Ensure you have Python installed. It is highly recommended to use a virtual environment. `uv` will help manage this.
    * Install `uv`:
        ```bash
        # Follow instructions on [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv) to install uv
        ```
    * Create and activate a virtual environment using `uv`:
        ```bash
        uv sync
        source .venv/bin/activate # On Linux/macOS
        .venv\Scripts\activate # On Windows
        ```
    * Install the required Python packages using `uv`:
        ```bash
        uv pip install -r requirements.txt
        ```
    
    * Run the Django development server:
        ```bash
        python3 manage.py runserver
        ```
    * The server will be accessible at `http://localhost:8000`.
3.  **Set up the frontend:**
    * The frontend files (HTML, CSS, JavaScript) can be served by the Django development server.
## Code Structure

* `templates` : Contains the HTML structure for the web application.
* `garbage_classifier/` :
    * Contains the Django project. This includes:
        * Django project settings (`settings.py`).
        * URL configurations (`urls.py`).
        

## Workflow

1.  The user uploads an image of waste through the frontend.
2.  The frontend sends the image to the Django backend.
3.  The Django backend receives the image and preprocesses it.
4.  The Django backend uses the TensorFlow models to classify the image.
5.  The Django backend sends the classification result back to the frontend.
6.  The frontend displays the result to the user.

## Backend (Django)

* The Django backend handles user authentication, image uploads, and garbage classification.
* **Authentication:**
    * Uses `django-allauth` to provide Google login and signup functionality. This handles user registration, login, and social authentication.
* **Image Handling:**
    * Django views and forms are used to handle image uploads from the frontend.
* **Garbage Classification:**
    * The Django backend integrates with TensorFlow to perform the image classification.
    * **Models:**
        * **MobileNet:** A lightweight convolutional neural network (CNN) suitable for efficient image classification.
        * **VGG16:** A deeper CNN known for its accuracy in image classification.
    * TensorFlow is used to:
        * Load the pre-trained MobileNet and VGG16 models.
        * Preprocess the uploaded images.
        * Perform the classification.
        * Return the results to the frontend.

## Notes

* This application classifies uploaded images of waste into different categories.
* The backend uses Django with TensorFlow, MobileNet, and VGG16.
* Google login and signup are integrated using django-allauth.
* The setup instructions now recommend using `uv` for environment and dependency management.
* New developers cloning the project need to run `python manage.py migrate` and `python manage.py createsuperuser`.  They also need to ensure the `django-allauth` settings are correctly configured, including obtaining and setting the Google Client ID and Secret.
* Setting up the backend requires Python, Django, TensorFlow, and other libraries, along with the MobileNet and VGG16 model files.
