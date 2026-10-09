import json
from datetime import time, timedelta

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone

from .models import FoodOrder, FoodOrderItem, FoodOrderReview, UserProfile


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
		profile = UserProfile.objects.get(user=user)
		self.assertFalse(profile.is_approved)
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
			is_approved=True,
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
			is_approved=True,
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
			due_at=timezone.now() + timedelta(hours=1),
		)
		FoodOrder.objects.create(
			poster=other_user,
			poster_name="Other User",
			student_id="OTHER-1001",
			target_store="Other Cafe",
			delivery_location="Other Building",
			due_time=time(13, 30),
			due_at=timezone.now() + timedelta(hours=1),
		)
		self.client.force_login(current_user)

		response = self.client.get("/browser/")

		self.assertContains(response, "Other Cafe")
		self.assertNotContains(response, "Own Cafe")

	def test_only_order_owner_can_cancel_active_order(self):
		owner = self.create_profiled_user("OWNER-1001", "Owner", "OWNER-1001")
		other_user = self.create_profiled_user("OTHER-2001", "Other", "OTHER-2001")
		order = FoodOrder.objects.create(
			poster=owner,
			poster_name="Owner User",
			student_id="OWNER-1001",
			target_store="Campus Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
		)

		self.client.force_login(other_user)
		forbidden_response = self.client.post(f"/order/{order.id}/cancel/")
		self.assertEqual(forbidden_response.status_code, 404)
		order.refresh_from_db()
		self.assertEqual(order.status, FoodOrder.STATUS_POSTED)

		self.client.force_login(owner)
		cancel_response = self.client.post(f"/order/{order.id}/cancel/")
		self.assertEqual(cancel_response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.status, FoodOrder.STATUS_CANCELLED)

	def test_runner_acceptance_and_completion_update_order_status(self):
		owner = self.create_profiled_user("OWNER-3001", "Owner", "OWNER-3001")
		runner = self.create_profiled_user("RUNNER-3001", "Runner", "RUNNER-3001")
		order = FoodOrder.objects.create(
			poster=owner,
			poster_name="Owner User",
			student_id="OWNER-3001",
			target_store="Campus Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
			due_at=timezone.now() + timedelta(hours=1),
		)

		self.client.force_login(runner)
		accept_response = self.client.post(f"/order/{order.id}/accept/")
		self.assertEqual(accept_response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.status, FoodOrder.STATUS_CLAIMED)
		self.assertEqual(order.claimed_by, runner)

		self.assertEqual(
			self.client.post(
				f"/order/{order.id}/complete/",
				data=json.dumps({"rating": 5}),
				content_type="application/json",
			).status_code,
			404,
		)
		self.client.force_login(owner)
		self.assertEqual(
			self.client.post(
				f"/order/{order.id}/complete/",
				data=json.dumps({}),
				content_type="application/json",
			).status_code,
			400,
		)
		complete_response = self.client.post(
			f"/order/{order.id}/complete/",
			data=json.dumps({"rating": 5, "review": "Fast and careful delivery."}),
			content_type="application/json",
		)
		self.assertEqual(complete_response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.status, FoodOrder.STATUS_COMPLETED)
		review = FoodOrderReview.objects.get(order=order)
		self.assertEqual(review.runner, runner)
		self.assertEqual(review.reviewer, owner)
		self.assertEqual(review.rating, 5)
		self.assertEqual(review.review, "Fast and careful delivery.")

	def test_due_posted_order_is_cancelled_when_my_orders_loads(self):
		owner = self.create_profiled_user("OWNER-4001", "Owner", "OWNER-4001")
		order = FoodOrder.objects.create(
			poster=owner,
			poster_name="Owner User",
			student_id="OWNER-4001",
			target_store="Expired Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
			due_at=timezone.now() - timedelta(minutes=1),
		)
		self.client.force_login(owner)

		response = self.client.get("/my-orders/")

		self.assertEqual(response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.status, FoodOrder.STATUS_CANCELLED)

	def test_order_detail_assigns_owner_or_accept_permission(self):
		owner = self.create_profiled_user("OWNER-5001", "Owner", "OWNER-5001")
		other_user = self.create_profiled_user("OTHER-5001", "Other", "OTHER-5001")
		order = FoodOrder.objects.create(
			poster=owner,
			poster_name="Owner User",
			student_id="OWNER-5001",
			target_store="Detail Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
			due_at=timezone.now() + timedelta(hours=1),
		)

		self.client.force_login(owner)
		owner_response = self.client.get(f"/order/{order.id}/")
		self.assertContains(owner_response, '"canCancel": true')
		self.assertNotContains(owner_response, '"canAccept": true')

		self.client.force_login(other_user)
		other_response = self.client.get(f"/order/{order.id}/")
		self.assertContains(other_response, '"canAccept": true')
		self.assertNotContains(other_response, '"canCancel": true')

	def test_unapproved_user_can_browse_but_cannot_post_or_accept(self):
		pending_user = self.create_profiled_user("PENDING-1001", "Pending", "PENDING-1001")
		pending_user.userprofile.is_approved = False
		pending_user.userprofile.save(update_fields=["is_approved"])
		approved_user = self.create_profiled_user("APPROVED-1001", "Approved", "APPROVED-1001")
		order = FoodOrder.objects.create(
			poster=approved_user,
			poster_name="Approved User",
			student_id="APPROVED-1001",
			target_store="Campus Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
			due_at=timezone.now() + timedelta(hours=1),
		)
		self.client.force_login(pending_user)

		self.assertEqual(self.client.get("/hero/").status_code, 200)
		hero_response = self.client.get("/hero/")
		self.assertContains(hero_response, "awaiting manual KYC approval")
		self.assertContains(hero_response, "Post")
		post_response = self.client.post(
			"/order/",
			data=json.dumps({
				"posterName": "Pending User",
				"posterSid": "PENDING-1001",
				"target": "Campus Cafe",
				"deliver": "Science Building",
				"dueInput": "13:30",
				"items": [{"name": "Lunch", "qty": 1}],
			}),
			content_type="application/json",
		)
		self.assertEqual(post_response.status_code, 403)
		self.assertEqual(self.client.post(f"/order/{order.id}/accept/").status_code, 403)

	def test_only_order_owner_can_edit_description(self):
		owner = self.create_profiled_user("OWNER-6001", "Owner", "OWNER-6001")
		other_user = self.create_profiled_user("OTHER-6001", "Other", "OTHER-6001")
		order = FoodOrder.objects.create(
			poster=owner,
			poster_name="Owner User",
			student_id="OWNER-6001",
			target_store="Campus Cafe",
			delivery_location="Science Building",
			due_time=time(13, 30),
			description="Original description",
			due_at=timezone.now() + timedelta(hours=1),
		)

		self.client.force_login(other_user)
		forbidden_response = self.client.post(
			f"/order/{order.id}/description/",
			data=json.dumps({"description": "Changed by someone else"}),
			content_type="application/json",
		)
		self.assertEqual(forbidden_response.status_code, 404)

		self.client.force_login(owner)
		update_response = self.client.post(
			f"/order/{order.id}/description/",
			data=json.dumps({"description": "Updated by owner"}),
			content_type="application/json",
		)
		self.assertEqual(update_response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.description, "Updated by owner")
