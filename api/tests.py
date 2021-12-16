import json
from django.test import TestCase, Client
from django.urls import reverse
import random
import string
from .models import *
from .serializers import *

# Create your tests here.


class ApiTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.app = App.objects.create(
            app_id=self.generate_random_str(128),
            app_name=self.generate_random_str(128),
            app_summary=self.generate_random_str(256),
            min_installs=random.randint(0, 10000000),
            avg_rating=random.random() * 5,
            ratings_count=random.randint(0, 10000000),
            reviews_count=random.randint(0, 10000000),
            free=random.random() >= 0.5,
            icon_link=self.generate_random_str(16),
        )
        self.app.similar_apps.add(self.app)
        self.query = Query.objects.create(query=self.generate_random_str(256))
        self.query_choice = QueryChoice.objects.create(query=self.query, choice=5)
        self.genre = Genre.objects.create(genre=self.generate_random_str(128))
        self.genre.apps.add(self.app)
        self.genre.queries.add(self.query)
        self.password = self.generate_random_str(16)
        self.user = User.objects.create_user(
            self.generate_random_str(8),
            self.generate_random_str(8) + "@mail.com",
            self.password,
        )
        self.review = Review.objects.create(
            app=self.app,
            user=self.user,
            content=self.generate_random_str(256),
            rating=random.randint(1, 5),
            state=self.generate_random_str(128),
            city=self.generate_random_str(128),
        )
        self.review.query_choices.add(self.query_choice)

    def assert_needs_login(self, path: str) -> None:
        res = self.client.post(path)
        self.assertEqual(res.status_code, 401)
        self.assertTrue(
            self.client.login(username=self.user.username, password=self.password)
        )

    def generate_random_str(self, n: int) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.whitespace, k=n))

    def test_best_apps_get(self) -> None:
        res = self.client.get(reverse("api_best_apps"))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset(
            AppSerializer(self.app).data, res.json()[self.genre.genre][0]
        )

    def test_top_users_get(self) -> None:
        res = self.client.get(reverse("api_top_users"))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset({self.user.username: 0}, res.json())

    def test_counter_get(self) -> None:
        res = self.client.get(reverse("api_counter"))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset(
            {"apps": 1, "users": 1, "reviews": 1, "views": 1}, res.json()
        )

    def test_similar_apps_get(self) -> None:
        res = self.client.get(
            reverse("api_similar_apps", args=[self.generate_random_str(128)])
        )
        self.assertEqual(res.status_code, 404)
        res = self.client.get(reverse("api_similar_apps", args=[self.app.app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset(AppSerializer(self.app).data, res.json()[0])

    def test_app_review_get(self) -> None:
        res = self.client.get(
            reverse("api_app_reviews", args=[self.generate_random_str(128)])
        )
        self.assertEqual(res.status_code, 404)
        res = self.client.get(reverse("api_app_reviews", args=[self.app.app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset(ReviewSerializer(self.review).data, res.json()[0])

    def test_app_review_post(self) -> None:
        path = reverse("api_app_reviews", args=[self.app.app_id])
        self.assert_needs_login(path)
        city = self.generate_random_str(128)
        res = self.client.post(
            path,
            {
                "app_id": self.app.app_id,
                "content": self.generate_random_str(256),
                "rating": random.randint(1, 5),
                "query_choices": json.dumps(
                    [
                        {"query": self.query.query, "choice": random.randint(1, 5)},
                    ]
                ),
                "state": self.generate_random_str(128),
                "city": city,
            },
        )
        self.assertEqual(res.status_code, 200)
        review = Review.objects.get(pk=self.review.pk + 1)
        self.assertDictContainsSubset(ReviewSerializer(review).data, res.json())

    def test_delete_review_post(self) -> None:
        path = reverse("api_delete_review", args=[self.review.pk])
        self.client.force_login(
            User.objects.create(username=self.generate_random_str(8))
        )
        res = self.client.post(path)
        self.assertEqual(res.status_code, 401)
        self.assert_needs_login(path)
        res = self.client.post(path)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_api_app_get(self) -> None:
        res = self.client.get(reverse("api_app", args=[self.app.app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset(AppSerializer(self.app).data, res.json())

    def test_all_genres_get(self) -> None:
        res = self.client.get(reverse("api_all_genres"))
        self.assertEqual(res.status_code, 200)
        self.assertListEqual(res.json(), [self.genre.genre])

    def test_app_review_queries_get(self) -> None:
        res = self.client.get(reverse("api_app_review_queries", args=[self.app.app_id]))
        self.assertEqual(res.status_code, 200)
        self.assertListEqual(res.json(), [self.query.query])

    def test_up_vote_review_post(self) -> None:
        res = self.client.post(reverse("api_up_vote_review", args=[self.review.pk + 1]))
        self.assertEqual(res.status_code, 404)
        path = reverse("api_up_vote_review", args=[self.review.pk])
        self.assert_needs_login(path)
        res = self.client.post(path)
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset({"up_votes": 1, "down_votes": 0}, res.json())
        res = self.client.post(reverse("api_up_vote_review", args=[self.review.pk]))
        self.assertEqual(res.status_code, 409)
        res = self.client.post(reverse("api_down_vote_review", args=[self.review.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset({"up_votes": 0, "down_votes": 1}, res.json())

    def test_down_vote_review_post(self) -> None:
        res = self.client.post(
            reverse("api_down_vote_review", args=[self.review.pk + 1])
        )
        self.assertEqual(res.status_code, 404)
        path = reverse("api_down_vote_review", args=[self.review.pk])
        self.assert_needs_login(path)
        res = self.client.post(path)
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset({"up_votes": 0, "down_votes": 1}, res.json())
        res = self.client.post(reverse("api_down_vote_review", args=[self.review.pk]))
        self.assertEqual(res.status_code, 409)
        res = self.client.post(reverse("api_up_vote_review", args=[self.review.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertDictContainsSubset({"up_votes": 1, "down_votes": 0}, res.json())

    def test_user_details_get(self) -> None:
        res = self.client.get(
            reverse("api_user_details", args=[self.generate_random_str(8)])
        )
        self.assertEqual(res.status_code, 404)
        res = self.client.get(reverse("api_user_details", args=[self.user.username]))
        self.assertDictContainsSubset(
            {"reviews": ReviewSerializer([self.review], many=True).data}, res.json()
        )
