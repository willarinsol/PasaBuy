from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "institutional_id", "is_approved", "created_at")
	list_editable = ("is_approved",)
	list_filter = ("is_approved", "role")
	search_fields = ("user__username", "user__first_name", "user__last_name", "institutional_id")
