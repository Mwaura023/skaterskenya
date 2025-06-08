from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Profile, Event, 
    Merchandise, SellerProfile, 
    SkateSpot, Activity, MerchandiseCategory
)

class CustomAdminSite(admin.AdminSite):
    site_header = "Skaters Kenya Administration"
    site_title = "Admin Portal"
    index_title = "Dashboard"
    index_template = "admin/custom_index.html"  # Optional custom dashboard template
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_dashboard), name='admin-dashboard'),
        ]
        return custom_urls + urls
    
    def admin_dashboard(self, request):
        context = {
            'total_users': User.objects.count(),
            'active_events': Event.objects.filter(date__gte=timezone.now()).count(),
            'recent_users': User.objects.order_by('-date_joined')[:5],
            'recent_merchandise': Merchandise.objects.order_by('-date_posted')[:5],
            'opts': self._registry.keys(),
        }
        return self._render_admin_dashboard(request, context)
    
    def _render_admin_dashboard(self, request, context):
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/dashboard.html', context)

# Initialize custom admin site
custom_admin = CustomAdminSite(name='custom_admin')

# Custom Admin Classes
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification'), {'fields': ('email_verified', 'verification_token')}),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skating_type', 'skill_level', 'location')
    list_filter = ('skating_type', 'skill_level')
    search_fields = ('user__username', 'bio', 'location')
    raw_id_fields = ('user',)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'skating_type', 'date', 'creator', 'attendees_count')
    list_filter = ('event_type', 'skating_type', 'date')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('attendees',)
    
    def attendees_count(self, obj):
        return obj.attendees.count()
    attendees_count.short_description = 'Attendees'

class MerchandiseAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'condition', 'available', 'whatsapp_link')
    list_filter = ('category', 'condition', 'available')
    search_fields = ('title', 'description')
    readonly_fields = ('date_posted', 'whatsapp_link')
    
    def whatsapp_link(self, obj):
        if obj.whatsapp_contact:
            return format_html(
                '<a href="https://wa.me/{}?text=Inquiry%20about%20{}" target="_blank">Chat on WhatsApp</a>',
                obj.whatsapp_contact, obj.title
            )
        return "-"
    whatsapp_link.short_description = "WhatsApp"

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'user_type', 'verified', 'created_at')
    list_filter = ('user_type', 'verified')
    search_fields = ('business_name', 'description')
    filter_horizontal = ('product_categories',)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'date', 'truncated_content')
    list_filter = ('activity_type', 'date')
    search_fields = ('user__username', 'content')
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'

class SkateSpotAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'added_by', 'created_at')
    search_fields = ('name', 'location', 'description')

class MerchandiseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

# Register all models with custom admin
custom_admin.register(User, UserAdmin)
custom_admin.register(Profile, ProfileAdmin)
custom_admin.register(Event, EventAdmin)
custom_admin.register(Merchandise, MerchandiseAdmin)
custom_admin.register(SellerProfile, SellerProfileAdmin)
custom_admin.register(SkateSpot, SkateSpotAdmin)
custom_admin.register(Activity, ActivityAdmin)
custom_admin.register(MerchandiseCategory, MerchandiseCategoryAdmin)

# Optional: Register default admin models if needed
# custom_admin.register(Group)
# custom_admin.register(Permission)