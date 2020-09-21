from django.urls import path
from . import views

urlpatterns = [
	path('',views.update_handler, name = 'update_handler')
]