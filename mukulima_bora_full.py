from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import requests

# ------------------- Config -------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mukulima.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "jwtsecretkey"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# ------------------- Models -------------------
class Farmer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    farm_size = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    amount = db.Column(db.Float)
    type = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Produce(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Float)
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradeListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    trade_type = db.Column(db.String(10))  # IMPORT / EXPORT
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Float)
    price_per_unit = db.Column(db.Float)
    destination_country = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Pending")

class SoilData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    soil_moisture = db.Column(db.Float)
    soil_ph = db.Column(db.Float)
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CarbonRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'), nullable=False)
    trees_planted = db.Column(db.Integer)
    estimated_co2_offset = db.Column(db.Float)

# ------------------- Routes -------------------
# Users
@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    if Farmer.query.filter_by(username=data['username']).first():
        return jsonify({"msg":"Username exists"}), 400
    if Farmer.query.filter_by(email=data['email']).first():
        return jsonify({"msg":"Email exists"}), 400
    farmer = Farmer(
        username=data['username'],
        email=data['email'],
        phone=data.get('phone',''),
        location=data.get('location',''),
        farm_size=float(data.get('farm_size',0.0))
    )
    farmer.set_password(data['password'])
    db.session.add(farmer)
    db.session.commit()
    wallet = Wallet(farmer_id=farmer.id, balance=0.0)
    db.session.add(wallet)
    db.session.commit()
    return jsonify({"msg":"Farmer registered successfully"}), 201

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    farmer = Farmer.query.filter_by(username=data['username']).first()
    if not farmer or not farmer.check_password(data['password']):
        return jsonify({"msg":"Bad username or password"}), 401
    access_token = create_access_token(identity=farmer.id, expires_delta=timedelta(days=1))
    return jsonify({"access_token": access_token})

# Wallet
@app.route('/api/finance/balance', methods=['GET'])
@jwt_required()
def wallet_balance():
    farmer_id = get_jwt_identity()
    wallet = Wallet.query.filter_by(farmer_id=farmer_id).first()
    return jsonify({"balance": wallet.balance})

@app.route('/api/finance/pay', methods=['POST'])
@jwt_required()
def pay():
    data = request.get_json()
    amount = float(data.get('amount',0))
    farmer_id = get_jwt_identity()
    wallet = Wallet.query.filter_by(farmer_id=farmer_id).first()
    if wallet.balance >= amount:
        wallet.balance -= amount
        transaction = Transaction(farmer_id=farmer_id, amount=amount, type="Wallet Payment")
        db.session.add(wallet)
        db.session.add(transaction)
        db.session.commit()
        return jsonify({"msg":"Paid from wallet"})
    else:
        return jsonify({"msg":"Insufficient funds"}), 402

# Marketplace
@app.route('/api/marketplace/add', methods=['POST'])
@jwt_required()
def add_produce():
    farmer_id = get_jwt_identity()
    data = request.get_json()
    produce = Produce(
        farmer_id=farmer_id,
        name=data['name'],
        quantity=float(data['quantity']),
        price=float(data['price'])
    )
    db.session.add(produce)
    db.session.commit()
    return jsonify({"msg":"Produce added"})

@app.route('/api/marketplace/list', methods=['GET'])
@jwt_required()
def list_produce():
    farmer_id = get_jwt_identity()
    produce_list = Produce.query.filter_by(farmer_id=farmer_id).all()
    return jsonify([{"id":p.id,"name":p.name,"quantity":p.quantity,"price":p.price} for p in produce_list])

# Trade
@app.route('/api/trade/create', methods=['POST'])
@jwt_required()
def create_trade():
    farmer_id = get_jwt_identity()
    data = request.get_json()
    trade = TradeListing(
        farmer_id=farmer_id,
        trade_type=data['trade_type'],
        product_name=data['product_name'],
        quantity=float(data['quantity']),
        price_per_unit=float(data['price_per_unit']),
        destination_country=data.get('destination_country','')
    )
    db.session.add(trade)
    db.session.commit()
    return jsonify({"msg":"Trade created"})

@app.route('/api/trade/list', methods=['GET'])
@jwt_required()
def list_trade():
    farmer_id = get_jwt_identity()
    trades = TradeListing.query.filter_by(farmer_id=farmer_id).all()
    return jsonify([{"id":t.id,
        "trade_type":t.trade_type,
        "product_name":t.product_name,
        "quantity":t.quantity,
        "price_per_unit":t.price_per_unit,
        "destination_country":t.destination_country,
        "status":t.status
    } for t in trades])

# Weather
WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
@app.route('/api/weather/current', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"msg":"Provide lat & lon"}),400
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={{lat}}&lon={{lon}}&appid={{WEATHER_API_KEY}}&units=metric"
    try:
        data = requests.get(url).json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"msg":"Error fetching weather","error":str(e)}),500

# Soil Sensors
@app.route('/api/sensors/add', methods=['POST'])
@jwt_required()
def add_sensor_data():
    farmer_id = get_jwt_identity()
    data = request.get_json()
    soil = SoilData(
        farmer_id=farmer_id,
        soil_moisture=float(data.get('soil_moisture',0)),
        soil_ph=float(data.get('soil_ph',7)),
        temperature=float(data.get('temperature',25))
    )
    db.session.add(soil)
    db.session.commit()
    return jsonify({"msg":"Sensor data added"})

@app.route('/api/sensors/list', methods=['GET'])
@jwt_required()
def list_sensor_data():
    farmer_id = get_jwt_identity()
    records = SoilData.query.filter_by(farmer_id=farmer_id).all()
    return jsonify([{"soil_moisture":r.soil_moisture,"soil_ph":r.soil_ph,"temperature":r.temperature,"timestamp":r.timestamp} for r in records])

# Carbon
@app.route('/api/carbon/add', methods=['POST'])
@jwt_required()
def add_carbon():
    farmer_id = get_jwt_identity()
    data = request.get_json()
    carbon = CarbonRecord(
        farmer_id=farmer_id,
        trees_planted=int(data.get('trees_planted',0)),
        estimated_co2_offset=float(data.get('estimated_co2_offset',0.0))
    )
    db.session.add(carbon)
    db.session.commit()
    return jsonify({"msg":"Carbon record added"})

@app.route('/api/carbon/list', methods=['GET'])
@jwt_required()
def list_carbon():
    farmer_id = get_jwt_identity()
    records = CarbonRecord.query.filter_by(farmer_id=farmer_id).all()
    return jsonify([{"trees_planted":r.trees_planted,"estimated_co2_offset":r.estimated_co2_offset} for r in records])

# AI Advice
@app.route('/api/ai/advice', methods=['POST'])
@jwt_required()
def ai_advice():
    data = request.get_json()
    question = data.get('question','')
    reply = f"AI advice placeholder for: {{question}}"
    return jsonify({"reply": reply})

# Analytics
@app.route('/api/analytics/farm/<int:farmer_id>', methods=['GET'])
def farm_analytics(farmer_id):
    produce = Produce.query.filter_by(farmer_id=farmer_id).all()
    total_value = sum([p.quantity * p.price for p in produce])
    return jsonify({
        "total_products": len(produce),
        "total_value": total_value,
        "products":[{"name":p.name,"quantity":p.quantity,"price":p.price} for p in produce]
    })

# ------------------- Run App -------------------
if __name__ == '__main__':
    app.run(debug=True)