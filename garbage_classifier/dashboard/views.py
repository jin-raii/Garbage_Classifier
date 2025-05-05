from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import UploadImageForm
from PIL import Image
import numpy as np
import os
import uuid
from django.conf import settings
import requests
import json
from tensorflow.keras.models import load_model
from django.utils import timezone
from .models import UserProfile

from dotenv import load_dotenv

load_dotenv()

model_path = os.path.join(settings.BASE_DIR, 'dashboard/model/', 'garbage_model_fixed.keras')
print(f"Model loading from: {os.path.join(settings.BASE_DIR, 'dashboard/mobileNet_model', 'garbage_test.h5')}")
model = load_model(model_path)
class_names = [
    'battery',
    'biological',
    'brown-glass',
    'cardboard',
    'clothes',
    'green-glass',
    'metal',
    'paper',
    'plastic',
    'shoes',
    'trash',
    'white-glass'
]

recycling_dict = {
    'clothes': 'recyclable',
    'plastic': 'non-recyclable',
    'shoes': 'recyclable',
    'trash': 'non-recyclable',
    'brown-glass': 'non-recyclable',
    'paper': 'non-recyclable',
    'metal': 'non-recyclable',
    'white-glass': 'non-recyclable',
    'battery': 'non-recyclable',
    'biological': 'non-recyclable',
    'green-glass': 'non-recyclable',
    'cardboard': 'non-recyclable'
}

TOKEN_COST = 40
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

def predict_image(image_file, model, class_names):
    try:
        img = Image.open(image_file).convert('RGB')
        resized_img = img.resize((256, 256))
        img_arr = np.array(resized_img) / 255.0
        img_array = np.expand_dims(img_arr, axis=0)
        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        confidence = prediction[0][predicted_class_index]
        predicted_class_name = class_names[predicted_class_index]
        return predicted_class_name, confidence
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error", 0.0

@login_required
def upload_image(request):
    user_profile = UserProfile.objects.get(user=request.user)
    now = timezone.now().date()
    if now.month > user_profile.last_token_reset.month or now.year > user_profile.last_token_reset.year:
        user_profile.tokens = 1000
        user_profile.last_token_reset = now
        user_profile.save()

    predicted_class = None
    confidence = None
    uploaded_image_url = None
    form = UploadImageForm()

    if request.method == 'POST':
        if user_profile.tokens < TOKEN_COST:
            messages.error(request, f"You need at least {TOKEN_COST} tokens to classify an image. Please purchase more tokens.")
            return redirect('buy_tokens')

        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                image_file = form.cleaned_data['image']
                predicted_class_temp, confidence_temp = predict_image(image_file, model, class_names)
                user_profile.tokens -= TOKEN_COST
                user_profile.save()

                file_extension = os.path.splitext(image_file.name)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
                file_url = os.path.join(settings.MEDIA_URL, unique_filename)

                with open(file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

                predicted_class = predicted_class_temp
                confidence = f'{confidence_temp * 100:.2f}%'
                uploaded_image_url = file_url

                messages.success(request, f"Image classified successfully! You have {user_profile.tokens} tokens remaining.")

            except Exception as e:
                messages.error(request, f"Error processing your image: {str(e)}")

    context = {
        'form': form,
        'predicted_class': predicted_class,
        'confidence': confidence,
        'uploaded_image_url': uploaded_image_url,
        'remaining_tokens': user_profile.tokens,
        'token_cost': TOKEN_COST,
        'recycling_type': recycling_dict.get(predicted_class, '') if predicted_class else '',
    }
    return render(request, 'upload.html', context)

@login_required
def profile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'user': user,
        'remaining_tokens': user_profile.tokens
    }
    return render(request, 'profile.html', context)

@login_required
def buy_tokens(request):
    user_profile = UserProfile.objects.get(user=request.user)
    context = {
        'remaining_tokens': user_profile.tokens
    }
    return render(request, 'dashboard/buy_token.html', context)

def get_weather_data(latitude, longitude):
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key,
        'units': 'metric'
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding weather JSON.")
        return {}
    return {}

def get_aqi_data(latitude, longitude):
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    api_url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_key}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        aqi_data = response.json()
        aqi_value = aqi_data.get('list', [{}])[0].get('main', {}).get('aqi')
        components = aqi_data.get('list', [{}])[0].get('components', {})
        return {'aqi': aqi_value, 'components': components}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching AQI data: {e}")
    except json.JSONDecodeError:
        print("Error decoding AQI JSON.")
    return {}

@login_required
def location_and_aqi(request):
    latitude_str = request.GET.get('latitude')
    longitude_str = request.GET.get('longitude')

    if latitude_str and longitude_str:
        try:
            latitude = float(latitude_str)
            longitude = float(longitude_str)
            aqi_data = get_aqi_data(latitude, longitude)
            weather_data = get_weather_data(latitude, longitude)

            user_profile = UserProfile.objects.get(user=request.user)
            remaining_tokens = user_profile.tokens

            data = {
                'latitude': latitude,
                'longitude': longitude,
                'aqi_value': aqi_data.get('aqi'),
                'aqi_components': aqi_data.get('components'),
                'remaining_tokens': remaining_tokens,
                'temperature': weather_data.get('main', {}).get('temp'),
                'weather_description': weather_data.get('weather', [{}])[0].get('description'),
                'humidity': weather_data.get('main', {}).get('humidity'),
                'location_name': weather_data.get('name') + ", " + weather_data.get('sys', {}).get('country') if weather_data.get('name') else None,
            }
            return JsonResponse(data)
        except ValueError:
            return JsonResponse({'error': 'Invalid latitude or longitude.'}, status=400)
    else:
        context = {
            'error': 'Location not provided by the browser.'
        }
        return render(request, 'location_aqi.html', context, status=400)