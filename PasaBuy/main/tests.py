import json
from datetime import time

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from .models import FoodOrder, FoodOrderItem, UserProfile


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


class FoodOrderTests(TestCase):
	def create_profiled_user(self, username, first_name, student_id):
		user = User.objects.create_user(
			username=username,
			first_name=first_name,
			last_name="User",
			password="StrongTestPass!42",
		)
		UserProfile.objects.create(
			user=user,
			role=UserProfile.ROLE_STUDENT,
			institutional_id=student_id,
			graduation_term="2027",
			id_front=SimpleUploadedFile(f"{username}-front.txt", b"front"),
			id_back=SimpleUploadedFile(f"{username}-back.txt", b"back"),
		)
		return user

	def test_authenticated_user_can_post_food_order(self):
		user = User.objects.create_user(
			username="RUNNER-1001",
			first_name="Food",
			last_name="Poster",
			password="StrongTestPass!42",
		)
		UserProfile.objects.create(
			user=user,
			role=UserProfile.ROLE_STUDENT,
			institutional_id="RUNNER-1001",
			graduation_term="2027",
			id_front=SimpleUploadedFile("front.txt", b"front"),
			id_back=SimpleUploadedFile("back.txt", b"back"),
		)
		self.client.force_login(user)

		response = self.client.post(
			"/order/",
			data=json.dumps({
				"posterName": "Food Poster",
				"posterSid": "RUNNER-1001",
				"target": "Campus Cafe",
				"deliver": "Science Building 304",
				"dueInput": "13:30",
				"desc": "One lunch order",
				"tip": "150",
				"items": [{"name": "Chicken meal", "qty": 2}],
			}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 201)
		order = FoodOrder.objects.get()
		self.assertEqual(order.poster, user)
		self.assertEqual(order.poster_name, "Food Poster")
		self.assertEqual(order.student_id, "RUNNER-1001")
		self.assertEqual(order.items.get().quantity, 2)
		self.assertEqual(FoodOrderItem.objects.count(), 1)

	def test_browser_excludes_current_users_active_orders(self):
		current_user = self.create_profiled_user("CURRENT-1001", "Current", "CURRENT-1001")
		other_user = self.create_profiled_user("OTHER-1001", "Other", "OTHER-1001")
		FoodOrder.objects.create(
			poster=current_user,
			poster_name="Current User",
			student_id="CURRENT-1001",
			target_store="Own Cafe",
			delivery_location="Own Building",
			due_time=time(13, 30),
		)
		FoodOrder.objects.create(
			poster=other_user,
			poster_name="Other User",
			student_id="OTHER-1001",
			target_store="Other Cafe",
			delivery_location="Other Building",
			due_time=time(13, 30),
		)
		self.client.force_login(current_user)

		response = self.client.get("/browser/")

		self.assertContains(response, "Other Cafe")
		self.assertNotContains(response, "Own Cafe")
