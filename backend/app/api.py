from flask import Blueprint, request, jsonify
import importlib
import logging

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def _load_product_model():
    candidates = []
    if __package__:
        candidates.append(f"{__package__}.models")
    candidates += ["models", "backend.app.models", "app.models"]
    for name in candidates:
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "Product"):
                return getattr(mod, "Product")
        except Exception as e:
            logger.debug("model import failed: %s (%s)", name, e)
            continue
    raise ImportError(f"Product model not found. Tried: {', '.join(candidates)}")

@api.route('/api/products/search')
def product_search():
    """
    Primary search endpoint. If a Product model is available it will query the DB.
    If not found, return demo/sample data so frontend can still function.
    """
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Try to load real model; fallback to demo data on failure
    try:
        Product = _load_product_model()
    except ImportError:
        return product_search_demo()

    try:
        query = Product.query
        if q:
            # assume Product.name exists
            query = query.filter(Product.name.ilike(f'%{q}%'))
        if category and hasattr(Product, 'category'):
            query = query.filter(getattr(Product, 'category') == category)
        if min_price is not None and hasattr(Product, 'price'):
            query = query.filter(getattr(Product, 'price') >= min_price)
        if max_price is not None and hasattr(Product, 'price'):
            query = query.filter(getattr(Product, 'price') <= max_price)

        results = query.limit(10).all()
        return jsonify([{
            'id': p.id,
            'name': getattr(p, 'name', ''),
            'price': getattr(p, 'price', None),
            'image_url': getattr(p, 'image_url', None)
        } for p in results])
    except Exception as e:
        logger.exception("Error querying Product model")
        return jsonify({'error': 'Search failed', 'detail': str(e)}), 500

@api.route('/api/products/demo')
def product_search_demo():
    sample = [
        {"id": 1, "name": "Kamera Mirrorless", "price": "Rp 5.000.000", "image_url": ""},
        {"id": 2, "name": "Kemeja Pria", "price": "Rp 150.000", "image_url": ""},
        {"id": 3, "name": "Headphone Wireless", "price": "Rp 750.000", "image_url": ""},
        {"id": 4, "name": "Kamera Digital", "price": "Rp 2.000.000", "image_url": ""},
        {"id": 5, "name": "Kaos Polos", "price": "Rp 50.000", "image_url": ""}
    ]
    q = request.args.get('q', '').strip().lower()
    if not q:
        return jsonify(sample[:10])
    filtered = [p for p in sample if q in p['name'].lower()]
    return jsonify(filtered[:10])