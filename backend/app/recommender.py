import os
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app import db
from app.model.transaction import Transaction
from app.model.product import Product

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'recommender')
os.makedirs(MODEL_PATH, exist_ok=True)
SIM_PATH = os.path.join(MODEL_PATH, 'similarity_df.pkl')
UI_PATH = os.path.join(MODEL_PATH, 'user_item.pkl')


def build_and_save(min_transactions=1):
    # load transactions from DB
    q = db.session.query(Transaction.customer_id, Transaction.product_id, db.func.sum(Transaction.quantity).label('qty'))\
        .filter(Transaction.status == 'completed')\
        .group_by(Transaction.customer_id, Transaction.product_id)
    rows = [{'customer_id': r.customer_id, 'product_id': r.product_id, 'quantity': int(r.qty)} for r in q]

    if not rows:
        q_all = db.session.query(Transaction.customer_id, Transaction.product_id, db.func.sum(Transaction.quantity).label('qty'))\
            .group_by(Transaction.customer_id, Transaction.product_id)
        rows = [{'customer_id': r.customer_id, 'product_id': r.product_id, 'quantity': int(r.qty)} for r in q_all]
        if rows:
            print('Warning: building recommender from all transactions (no completed transactions found)')
        else:
            return False

    df = pd.DataFrame(rows)
    user_item = df.pivot_table(index='customer_id', columns='product_id', values='quantity', aggfunc='sum').fillna(0)

    # compute similarity
    sim = cosine_similarity(user_item)
    sim_df = pd.DataFrame(sim, index=user_item.index, columns=user_item.index)

    with open(SIM_PATH, 'wb') as f:
        pickle.dump(sim_df, f)
    with open(UI_PATH, 'wb') as f:
        pickle.dump(user_item, f)

    return True


def load_model():
    if not os.path.exists(SIM_PATH) or not os.path.exists(UI_PATH):
        try:
            built = build_and_save()
        except Exception as e:
            print(f'Could not build recommender model: {e}')
            return None, None
        if not built:
            return None, None
    with open(SIM_PATH, 'rb') as f:
        sim_df = pickle.load(f)
    with open(UI_PATH, 'rb') as f:
        user_item = pickle.load(f)
    return sim_df, user_item


def recommend_for_customer(customer_id, top_n=10, similar_user_count=5):
    sim_df, user_item = load_model()
    if sim_df is None or user_item is None:
        return []
    if customer_id not in sim_df.index:
        return []

    similar = sim_df[customer_id].sort_values(ascending=False).drop(customer_id).head(similar_user_count)
    scores = {}
    for other_id, weight in similar.items():
        other_row = user_item.loc[other_id]
        for pid, qty in other_row.items():
            if user_item.loc[customer_id, pid] == 0 and qty > 0:
                scores[pid] = scores.get(pid, 0) + qty * weight

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    product_ids = [int(pid) for pid, _ in ranked]
    if not product_ids:
        return []
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    prod_map = {p.id: p for p in products}
    ordered = [prod_map.get(pid) for pid in product_ids if pid in prod_map]
    return ordered
