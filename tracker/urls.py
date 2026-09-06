from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Notifications (simple in-app + offline phone)
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/read-all/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),

    # Medicine
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/add/', views.medicine_add, name='medicine_add'),
    path('medicines/edit/<int:pk>/', views.medicine_edit, name='medicine_edit'),
    path('medicines/delete/<int:pk>/', views.medicine_delete, name='medicine_delete'),

    # Food
    path('foods/', views.food_list, name='food_list'),
    path('foods/add/', views.food_add, name='food_add'),
    path('foods/edit/<int:pk>/', views.food_edit, name='food_edit'),
    path('foods/delete/<int:pk>/', views.food_delete, name='food_delete'),
]
