from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from home.admin import custom_admin
from home import views as home_views

urlpatterns = [
    # Main app routes
    path('', include('home.urls')),

    # Custom admin and default admin
    path('kenya-admin/', custom_admin.urls),
    path('admin/', admin.site.urls),

    # Admin dashboard
    path('admin-dashboard/', home_views.admin_dashboard, name='admin-dashboard'),

    # Social Authentication
    path('social-auth/', include('social_django.urls', namespace='social_auth')),

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='home/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='home/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='home/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='home/password_reset_complete.html'), name='password_reset_complete'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
