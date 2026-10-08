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
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.get_full_name() or self.user.username
