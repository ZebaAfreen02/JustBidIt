from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from flask import Blueprint, current_app, request, jsonify, session
from PIL import Image, ImageOps
from auth import db

product_bp = Blueprint('product', __name__)
IMAGE_TYPES = {
    '.jpg': ('JPEG', 'image/jpeg'),
    '.jpeg': ('JPEG', 'image/jpeg'),
    '.png': ('PNG', 'image/png'),
    '.webp': ('WEBP', 'image/webp'),
}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float)  # 💵 price stored in USD
    brand = db.Column(db.String(255))
    storage = db.Column(db.String(255))
    ram = db.Column(db.String(255))
    color = db.Column(db.String(100))
    screen_size = db.Column(db.String(100))
    reserve_price = db.Column(db.Float)  # 💵 reserve price in USD
    closing_date = db.Column(db.DateTime)
    image_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default= datetime.now())
    user_id = db.Column(db.Float)
    bid_price = db.Column(db.Float)
    winner_notified = db.Column(db.Boolean, default=False)



def decode_product_image(upload):
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in IMAGE_TYPES:
        raise ValueError("Choose a JPEG, PNG, or WebP image")
    expected_format, _ = IMAGE_TYPES[suffix]
    payload = upload.stream.read(MAX_IMAGE_BYTES + 1)
    if len(payload) > MAX_IMAGE_BYTES:
        raise ValueError("Image must be at most 10 MB")
    try:
        with Image.open(BytesIO(payload), formats=[expected_format]) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image must be at most 16 megapixels")
            image.verify()
        with Image.open(BytesIO(payload), formats=[expected_format]) as image:
            image.load()
            clean_image = ImageOps.exif_transpose(image)
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError("Invalid image content") from error
    if expected_format == 'JPEG' and clean_image.mode not in ('RGB', 'L'):
        clean_image = clean_image.convert('RGB')
    # Retain PNG palette transparency while dropping metadata from stored files.
    transparency = clean_image.info.get('transparency')
    clean_image.info.clear()
    if expected_format == 'PNG' and transparency is not None:
        clean_image.info['transparency'] = transparency
    return clean_image, suffix, expected_format


@product_bp.route('/api/auctions', methods=['POST'])
def create_product():
    if "user_id" not in session:
        return jsonify(error="Unauthorized"), 401

    saved_image = None
    try:
        form = request.form
        upload = request.files.get('productImage')
        product = Product(
            name=form['name'],
            price=float(form['price']),  # 💵 price in USD
            brand=form['brand'],
            storage=form['storage'],
            ram=form['ram'],
            color=form['color'],
            screen_size=form['screenSize'],
            reserve_price = float(form['reservePrice']) if form.get('reservePrice') not in [None, '', 'null'] else None,

            closing_date=datetime.fromisoformat(form['closingDate']),
        )
        if upload:
            image, suffix, image_format = decode_product_image(upload)
            directory = Path(current_app.config['PRODUCT_UPLOAD_FOLDER'])
            directory.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=directory, suffix=suffix, delete=False) as destination:
                saved_image = Path(destination.name)
                with image:
                    image.save(destination, format=image_format)
            product.image_filename = saved_image.name

        db.session.add(product)
        db.session.commit()
        saved_image = None

        return jsonify({"message": "Product added successfully!"}), 201

    except (ValueError, KeyError) as error:
        return jsonify(error=str(error)), 400
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Could not save listing")
        return jsonify(error="Could not save listing"), 500
    finally:
        if saved_image is not None:
            saved_image.unlink(missing_ok=True)

# 🔵 Get All Products API
@product_bp.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        result = []

        for product in products:
            result.append({
                "id": product.id,
                "name": product.name,
                "price": round(product.price, 2),  # 💵 show two decimals
                "brand": product.brand,
                "storage": product.storage,
                "ram": product.ram,
                "color": product.color,
                "screen_size": product.screen_size,
                "reserve_price": round(product.reserve_price, 2) if product.reserve_price is not None else None,

                "closing_date": product.closing_date.strftime('%Y-%m-%d %H:%M:%S'),
                "image_url": f"http://localhost:8000/uploads/{product.image_filename}"
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔵 Get Specific Product by ID API
@product_bp.route('/api/product', methods=['GET'])
def get_product_by_id():
    try:
        product_id = request.args.get('id')
        if not product_id:
            return jsonify({"error": "Missing product ID"}), 400

        product = Product.query.get(product_id)

        if not product:
            return jsonify({"error": "Product not found"}), 404

        result = {
            "id": product.id,
            "name": product.name,
            "price": round(product.price, 2),  # 💵 two decimal formatting
            "brand": product.brand,
            "storage": product.storage,
            "ram": product.ram,
            "color": product.color,
            "screen_size": product.screen_size,
            "reserve_price": round(product.reserve_price, 2) if product.reserve_price is not None else None,

            "closing_date": product.closing_date.strftime('%Y-%m-%d %H:%M:%S'),
            "image_url": f"http://localhost:8000/uploads/{product.image_filename}"
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @product_bp.route('/api/winner', methods=['GET'])
# def get_auction_winner():
#     product_id = request.args.get('id')

#     product = Product.query.get(product_id)


#     if datetime.utcnow() < product.closing_date:
#         return

#     create_notification(
#         user_id=winner_user_id,
#         message=f"Congratulations! You have won the auction for product ID {product_id}.",
#         notif_type='winner'
#         )
        
#     if product.bid_price and product.user_id:
#         return jsonify({
#             "winner_user_id": int(product.user_id),
#             "winning_bid": round(product.bid_price, 2),
#             "product_id": product.id,
#             "product_name": product.name
#         }), 200
    
    

#     else:
#         return jsonify({"message": "No bids were placed for this product"}), 200



# @product_bp.route('/api/winner', methods=['GET'])
# def get_auction_winner():
#     product_id = request.args.get('id')

#     product = Product.query.get(product_id)


#     if datetime.utcnow() < product.closing_date:
#         return

#     create_notification(
#         user_id=winner_user_id,
#         message=f"Congratulations! You have won the auction for product ID {product_id}.",
#         notif_type='winner'
#         )
        
#     if product.bid_price and product.user_id:
#         return jsonify({
#             "winner_user_id": int(product.user_id),
#             "winning_bid": round(product.bid_price, 2),
#             "product_id": product.id,
#             "product_name": product.name
#         }), 200
    
    

#     else:
#         return jsonify({"message": "No bids were placed for this product"}), 200
