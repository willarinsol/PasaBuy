from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    ROLE_STUDENT = "Student"
    ROLE_EMPLOYEE = "Employee"
    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_EMPLOYEE, "Employee"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    institutional_id = models.CharField(max_length=50, unique=True)
    graduation_term = models.CharField(max_length=50, blank=True)
    id_front = models.FileField(upload_to="institutional_ids/")
    id_back = models.FileField(upload_to="institutional_ids/")
    is_approved = models.BooleanField(default=False, verbose_name="KYC approved")
    
    # New Contact fields
    phone = models.CharField(max_length=20, blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class FoodOrder(models.Model):
	STATUS_POSTED = "posted"
	STATUS_CLAIMED = "claimed"
	STATUS_COMPLETED = "completed"
	STATUS_CANCELLED = "cancelled"
	STATUS_CHOICES = [
		(STATUS_POSTED, "Posted"),
		(STATUS_CLAIMED, "Claimed"),
		(STATUS_COMPLETED, "Completed"),
		(STATUS_CANCELLED, "Cancelled"),
	]

	poster = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="food_orders",
	)
	claimed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="claimed_food_orders",
	)
	poster_name = models.CharField(max_length=150)
	student_id = models.CharField(max_length=50)
	target_store = models.CharField(max_length=200)
	delivery_location = models.CharField(max_length=200)
	due_time = models.TimeField()
	due_at = models.DateTimeField(null=True, blank=True)
	description = models.TextField(blank=True)
	tip = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_POSTED,
	)
	posted_at = models.DateTimeField(auto_now_add=True)
	claimed_at = models.DateTimeField(null=True, blank=True)
	completed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"{self.target_store} for {self.poster_name}"


class FoodOrderItem(models.Model):
	order = models.ForeignKey(
		FoodOrder,
		on_delete=models.CASCADE,
		related_name="items",
	)
	name = models.CharField(max_length=255)
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.quantity}x {self.name}"


class FoodOrderReview(models.Model):
	order = models.OneToOneField(
		FoodOrder,
		on_delete=models.CASCADE,
		related_name="review",
	)
	reviewer = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="food_order_reviews",
	)
	runner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="runner_reviews",
	)
	rating = models.PositiveSmallIntegerField()
	review = models.TextField(blank=True, max_length=1000)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.rating}/5 review for order {self.order_id}"
