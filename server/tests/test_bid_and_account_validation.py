import os
import unittest
from datetime import datetime, timedelta
from smtplib import SMTPException
from time import sleep
from unittest.mock import patch

from mysql.connector.errors import IntegrityError as MySQLError
from sqlalchemy.exc import IntegrityError

with patch.dict(os.environ, {"FLASK_SECRET_KEY": "test-only", "DATABASE_URL": "sqlite://"}):
    from server import app, db
    from auth import User
    from bids import Bid, BidHistory
    from notifications import Notification
    from products import Product


class BidAndAccountValidationTests(unittest.TestCase):
    def setUp(self):
        config = patch.dict(app.config, TESTING=True)
        config.start()
        self.addCleanup(config.stop)
        with app.app_context():
            db.create_all()
            db.session.add_all([
                Product(id=1, name="Open", price=10, bid_price=0,
                        closing_date=datetime.now() + timedelta(days=1)),
                Product(id=2, name="Closed", price=10,
                        closing_date=datetime.now() - timedelta(days=1)),
                User(id=1, username="customer", email="customer@example.invalid",
                     password="unused-test-placeholder", account_type="personal", country="US"),
            ])
            db.session.commit()
        self.addCleanup(self.drop_tables)
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["user_id"] = 1
        self.header = {"X-CSRFToken": self.client.get("/api/csrf-token").json["csrf_token"]}

    def drop_tables(self):
        with app.app_context():
            db.drop_all()

    def bid(self, **changes):
        data = {"productId": "1", "bidAmount": "10", "autoBid": False, **changes}
        return self.client.post("/api/bid", json=data, headers=self.header)

    def test_opening_price_and_auto_start_below_current_price(self):
        self.assertEqual(self.bid().status_code, 201)
        self.assertEqual(self.bid(bidAmount=15).status_code, 201)
        with self.client.session_transaction() as session:
            session["user_id"] = 2
        self.assertEqual(self.bid(autoBid=True, maxLimit="20", increment="2").status_code, 201)
        with app.app_context():
            product = db.session.get(Product, 1)
            self.assertEqual((product.user_id, product.bid_price), (2, 16))

    def test_bad_bids_leave_bids_history_notifications_and_auction_unchanged(self):
        self.assertEqual(self.bid(bidAmount=15).status_code, 201)
        for changes, status in [
            ({"bidAmount": -1}, 400), ({"bidAmount": 0}, 400),
            ({"bidAmount": True}, 400), ({"bidAmount": "nan"}, 400),
            ({"bidAmount": "inf"}, 400), ({"bidAmount": 9}, 400),
            ({"bidAmount": 15}, 400), ({"productId": 2}, 400),
            ({"productId": 999}, 404),
            ({"autoBid": True, "increment": 2}, 400),
            ({"autoBid": True, "increment": 2, "maxLimit": "inf"}, 400),
            ({"autoBid": True, "increment": 2, "maxLimit": 9}, 400),
            ({"autoBid": True, "increment": 2, "maxLimit": 15}, 400),
        ]:
            with self.subTest(changes=changes):
                self.assertEqual(self.bid(**changes).status_code, status)
        with app.app_context():
            self.assertEqual(Bid.query.count(), 1)
            self.assertEqual(BidHistory.query.count(), 1)
            self.assertEqual(Notification.query.count(), 0)
            product = db.session.get(Product, 1)
            self.assertEqual((product.user_id, product.bid_price), (1, 15))
            self.assertIsNone(db.session.get(Product, 2).bid_price)

    def test_timestamp_defaults_are_evaluated_for_each_insert(self):
        for model in (Bid, BidHistory):
            with self.subTest(model=model), app.app_context():
                first = model(product_id=1, user_id=1, bid_amount=10)
                db.session.add(first)
                db.session.flush()
                sleep(0.01)
                second = model(product_id=1, user_id=1, bid_amount=11)
                db.session.add(second)
                db.session.flush()
                self.assertLess(first.created_at, second.created_at)
                db.session.rollback()

    def test_reset_response_is_identical_and_logs_no_smtp_details(self):
        with patch("auth.send_reset_email", side_effect=[None, SMTPException("sensitive diagnostic")]) as send:
            responses = []
            with self.assertLogs(app.logger, level="WARNING") as log:
                for email in ("unknown@example.invalid", "customer@example.invalid", "customer@example.invalid"):
                    response = self.client.post("/request-reset", json={"email": email}, headers=self.header)
                    responses.append((response.status_code, response.json))
            self.assertEqual(send.call_count, 2)
        self.assertEqual(responses[0][0], 200)
        self.assertEqual(responses, [responses[0]] * 3)
        self.assertIn("delivery failed", log.output[0])
        self.assertNotIn("sensitive diagnostic", log.output[0])

    def test_mysql_duplicate_code_returns_conflict_and_other_errors_are_generic(self):
        with self.client.session_transaction() as session:
            session["admin_id"] = 1
        with app.app_context():
            engine = db.engine
        for code, status in ((1062, 409), (1048, 500)):
            error = IntegrityError("INSERT", {}, MySQLError("private database details", errno=code))
            with self.subTest(code=code), patch.object(engine, "begin", side_effect=error):
                response = self.client.post("/admin/create-customer-rep", headers=self.header,
                                            json={"username": "rep", "password": "test-password"})
                self.assertEqual(response.status_code, status)
                self.assertNotIn("private database details", response.get_data(as_text=True))

    def test_auction_missing_bidder_is_displayed_as_na_by_the_api(self):
        with self.client.session_transaction() as session:
            session["rep_id"] = 1
        response = self.client.get("/api/customer-rep/get-auctions")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["auctions"])
        self.assertTrue(all(row["seller"] == "N/A" for row in response.json["auctions"]))
