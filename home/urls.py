from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from . import views
from .views import (
    EventListView, EventCreateView, EventUpdateView,
    EventDeleteView, attend_event, merchandise_list,
    merchandise_detail, CustomLoginView,
    all_communities, community_detail, logged_out_view
)

urlpatterns = [
    # General
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logged-out/', logged_out_view, name='logged_out'),

    # Email Verification
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify-email'),
    path('email-sent/', TemplateView.as_view(template_name='home/email_sent.html'), name='email-sent'),
    path('email-verified/', TemplateView.as_view(template_name='home/email_verified.html'), name='email-verified'),

    # User Profile
    path('profile/update/', views.profile_update, name='profile-update'),
    path('profile/<str:username>/', views.profile, name='profile'),

    # Communities
    path('communities/', all_communities, name='all_communities'),
    path('communities/<slug:slug>/', community_detail, name='community_detail'),

    # Search and Category
    path('category/<str:category>/', views.skater_category, name='skater_category'),
    path('search/', views.search_skaters, name='search_skaters'),

    # Events
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/new/', EventCreateView.as_view(), name='event-create'),
    path('events/<int:pk>/', views.event_detail, name='event-detail'),
    path('events/<int:pk>/edit/', EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    path('events/<int:pk>/attend/', attend_event, name='event-attend'),

    # Seller & Merchandise
    path('become-seller/', views.become_seller, name='become_seller'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller-profile/update/', views.update_seller_profile, name='update_seller_profile'),
    path('merchandise/', merchandise_list, name='merchandise_list'),
    path('merchandise/add/', views.add_merchandise, name='add_merchandise'),
    path('merchandise/<int:pk>/', merchandise_detail, name='merchandise_detail'),
    path('merchandise/<int:pk>/edit/', views.edit_merchandise, name='edit_merchandise'),
    path('merchandise/<int:pk>/delete/', views.delete_merchandise, name='delete_merchandise'),
    path('merchandise/<int:pk>/toggle/', views.toggle_merchandise, name='toggle_merchandise'),
]
