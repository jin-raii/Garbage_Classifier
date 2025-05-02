from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

model_path = os.path.join(settings.BASE_DIR, 'dashboard/mobileNet_model/', 'garbage_test.h5')
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


def predict_image(image_file, model, class_names):

    print(f'Model input shape: {model.layers[0].input_shape}')
    try:
        img = Image.open(image_file).convert('RGB')
        print('Image shape: ', img.size)
        resized_img = img.resize((224, 224))
        print('Resized image : ', resized_img.size)
        img_arr = np.array(resized_img) / 255.0
        img_array = np.expand_dims(img_arr, axis=0)
        print(f'Input array shape: {img_array.shape}')
        prediction = model.predict(img_array)
        predicted_class_index = np.argmax(prediction)
        confidence = prediction[0][predicted_class_index]

        predicted_class_name = class_names[predicted_class_index]
        print(f'Raw prediction: {prediction}')
        print(f'Predicted class index: {predicted_class_index}')
        print(f'Predicted class name: {predicted_class_name}')
        print(f'Confidence score: {confidence * 100:.2f}%')

        return predicted_class_name, confidence
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error", 0.0

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

@login_required
def upload_image(request):
    # Check for monthly token reset
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
                
                # Deduct tokens only after successful prediction
                user_profile.tokens -= TOKEN_COST
                user_profile.save()
                
                # Save the uploaded image
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
                
                # Display success message
                messages.success(request, f"Image classified successfully! You have {user_profile.tokens} tokens remaining.")
                
            except Exception as e:
                messages.error(request, f"Error processing your image: {str(e)}")

    # Pass token information to the template
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

def get_user_location_from_ip(request):
    try:
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        response.raise_for_status()
        location_data = response.json()
        latitude = location_data.get('lat')
        longitude = location_data.get('lon')
        return latitude, longitude
    except requests.exceptions.RequestException as e:
        print(f"Error getting location from IP: {e}")
        return None, None
    except json.JSONDecodeError:
        print("Error decoding location JSON.")
        return None, None

def get_aqi_data(latitude, longitude):
    api_key = settings.OPENWEATHERMAP_API_KEY
    if latitude is not None and longitude is not None and api_key:
        api_url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={api_key}' # corrected variable name
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            aqi_data = response.json()
            aqi_value = aqi_data.get('list', [{}])[0].get('main', {}).get('aqi')
            return aqi_value
        except requests.exceptions.RequestException as e:
            print(f"Error fetching AQI data: {e}")
        except json.JSONDecodeError:
            print("Error decoding AQI JSON.")
    return None

@login_required
def location_and_aqi(request):
    latitude, longitude = get_user_location_from_ip(request)
    aqi_value = get_aqi_data(latitude, longitude)

    user_profile = UserProfile.objects.get(user=request.user) 
    remaining_tokens = user_profile.tokens  

    context = {
        'latitude': latitude,
        'longitude': longitude,
        'aqi_value': aqi_value,
        'remaining_tokens': remaining_tokens,  
    }
    return render(request, 'location_aqi.html', context)