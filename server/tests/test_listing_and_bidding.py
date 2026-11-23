import os
import unittest
from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image

with patch.dict(os.environ, {"FLASK_SECRET_KEY": "test-only", "DATABASE_URL": "sqlite://"}):
    from server import app, db
    from bids import Bid
    from products import Product


class ListingAndBiddingTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.upload_dir = Path(scratch.name)
        config = patch.dict(app.config, TESTING=True, PRODUCT_UPLOAD_FOLDER=self.upload_dir)
        config.start()
        self.addCleanup(config.stop)
        with app.app_context():
            db.create_all()
        self.addCleanup(self.drop_tables)
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["user_id"] = 1
        self.header = {"X-CSRFToken": self.client.get("/api/csrf-token").json["csrf_token"]}

    def drop_tables(self):
        with app.app_context():
            db.drop_all()

    def post_listing(self, payload, filename):
        return self.client.post("/api/auctions", headers=self.header, data={
            "name": "Demo phone", "price": "10", "brand": "Demo",
            "storage": "64 GB", "ram": "4 GB", "color": "Blue",
            "screenSize": "6", "closingDate": "2030-01-01T12:00",
            "productImage": (BytesIO(payload), filename),
        })

    def test_upload_names_do_not_collide_and_content_is_reencoded(self):
        sentinel = b"trailing-content-marker"
        image = BytesIO()
        with Image.new("RGB", (2, 2), "blue") as pixels:
            pixels.save(image, "PNG")
        payload = image.getvalue() + sentinel
        legacy_path = self.upload_dir / "phone.png"
        legacy_path.write_bytes(image.getvalue())
        for _ in range(2):
            response = self.post_listing(payload, "phone.png")
            self.assertEqual(response.status_code, 201, response.json)
        with app.app_context():
            names = [product.image_filename for product in Product.query.all()]
        self.assertEqual(len(set(names + ["phone.png"])), 3)
        self.assertEqual(legacy_path.read_bytes(), image.getvalue())
        for name in names + ["phone.png"]:
            with self.client.get(f"/uploads/{name}") as response:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "image/png")
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
                self.assertNotIn(sentinel, response.data)
                with Image.open(BytesIO(response.data)) as stored:
                    self.assertEqual(stored.size, (2, 2))

    def test_rejects_active_disguised_and_mismatched_uploads(self):
        image = BytesIO()
        with Image.new("RGB", (2, 2)) as pixels:
            pixels.save(image, "PNG")
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        for payload, filename in ((svg, "bad.svg"), (svg, "bad.png"), (image.getvalue(), "bad.jpg")):
            with self.subTest(filename=filename):
                self.assertEqual(self.post_listing(payload, filename).status_code, 400)
        self.assertEqual(list(self.upload_dir.iterdir()), [])
        with app.app_context():
            self.assertEqual(Product.query.count(), 0)
        (self.upload_dir / "old.svg").write_bytes(svg)
        self.assertEqual(self.client.get("/uploads/old.svg").status_code, 404)

    def test_rejects_invalid_auto_increments_before_inserting_a_bid(self):
        with app.app_context():
            db.session.add(Product(name="Demo phone", price=10, closing_date=datetime(2030, 1, 1)))
            db.session.commit()
        bid = {"productId": 1, "bidAmount": "10", "autoBid": True, "maxLimit": "20"}
        for increment in (None, "", True, 0, -1, "nan", "inf", "-inf", "invalid"):
            with self.subTest(increment=increment):
                response = self.client.post("/api/bid", json={**bid, "increment": increment}, headers=self.header)
                self.assertEqual(response.status_code, 400)
        with app.app_context():
            self.assertEqual(Bid.query.count(), 0)
        response = self.client.post("/api/bid", json={**bid, "increment": "2"}, headers=self.header)
        self.assertEqual(response.status_code, 201, response.json)
        with app.app_context():
            self.assertEqual(Bid.query.one().increment, 2)
