from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# GET all bakeries
@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = Bakery.query.all()
    bakery_list = [bakery.to_dict() for bakery in bakeries]
    return make_response(jsonify(bakery_list), 200)

# GET single bakery by ID
@app.route('/bakeries/<int:id>', methods=['GET'])
def get_bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if bakery:
        return make_response(jsonify(bakery.to_dict()), 200)
    return make_response(jsonify({"error": "Bakery not found"}), 404)

# GET all baked goods ordered by price descending
@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    result = [bg.to_dict() for bg in baked_goods]
    return make_response(jsonify(result), 200)

# GET most expensive baked good
@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    bg = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(jsonify(bg.to_dict()), 200)

# POST a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    if not name or not price or not bakery_id:
        return make_response(jsonify({"error": "Missing data"}), 400)

    try:
        baked_good = BakedGood(name=name, price=float(price), bakery_id=int(bakery_id))
        db.session.add(baked_good)
        db.session.commit()
        return make_response(jsonify(baked_good.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

# PATCH a bakery name
@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    name = request.form.get('name')
    if name:
        bakery.name = name
        db.session.commit()

    return make_response(jsonify(bakery.to_dict()), 200)

# DELETE a baked good by ID
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response(jsonify({"error": "Baked good not found"}), 404)

    db.session.delete(baked_good)
    db.session.commit()

    return make_response(jsonify({"message": "Baked good successfully deleted"}), 200)

# Home route
@app.route('/')
def home():
    return '<h1>Bakery API</h1>'

if __name__ == '__main__':
    app.run(port=5000, debug=True)
