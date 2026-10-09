from django.contrib import admin
from .models import UserProfile, FoodOrder, FoodOrderItem, FoodOrderReview


class FoodOrderItemInline(admin.TabularInline):
    model = FoodOrderItem
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "institutional_id", "is_approved", "created_at")
    list_editable = ("is_approved",)
    list_filter = ("is_approved", "role")
    search_fields = ("user__username", "user__first_name", "user__last_name", "institutional_id")


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target_store",
        "poster_name",
        "delivery_location",
        "status",
        "tip",
        "due_time",
        "claimed_by",
        "posted_at",
    )
    list_filter = ("status", "posted_at", "target_store")
    search_fields = ("poster_name", "student_id", "target_store", "delivery_location")
    inlines = [FoodOrderItemInline]


@admin.register(FoodOrderReview)
class FoodOrderReviewAdmin(admin.ModelAdmin):
    list_display = ("order", "reviewer", "runner", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("reviewer__username", "runner__username", "review")