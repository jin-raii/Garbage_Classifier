
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('profile/', views.profile, name='profile'),
    path('buy_tokens/', views.buy_tokens, name='buy_tokens'), 

]