from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .models import UserProfile


class AuthenticationFlowTests(TestCase):
	def test_signup_creates_profile_and_login_works(self):
		signup_details = {
			"role": "Student",
			"first_name": "Test",
			"last_name": "Runner",
			"idnumber": "STUDENT-1001",
			"graduation": "2027",
			"password": "StrongTestPass!42",
			"password_confirmation": "StrongTestPass!42",
		}

		details_response = self.client.post("/signup/details/", signup_details)
		self.assertEqual(details_response.status_code, 200)
		self.assertEqual(
			self.client.session["signup_details"]["institutional_id"],
			"STUDENT-1001",
		)

		complete_response = self.client.post(
			"/signup/complete/",
			{
				"affirmation": "yes",
				"id_front": SimpleUploadedFile("front.txt", b"front"),
				"id_back": SimpleUploadedFile("back.txt", b"back"),
		})

		self.assertRedirects(complete_response, "/hero/")
		user = User.objects.get(username="STUDENT-1001")
		self.assertTrue(UserProfile.objects.filter(user=user).exists())

		self.client.get("/logout/")
		login_response = self.client.post(
			"/",
			{"username": "STUDENT-1001", "password": "StrongTestPass!42"},
		)
		self.assertRedirects(login_response, "/hero/")
