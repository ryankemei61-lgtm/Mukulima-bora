# Mukulima Bora - Agricultural Platform

Mukulima Bora is a comprehensive agricultural technology platform designed to empower farmers in East Africa with tools for marketplace management, financial services, weather insights, soil monitoring, and carbon offset tracking.

## Features

- **User Authentication** - Secure JWT-based authentication with password hashing
- **Wallet Management** - Financial transactions and balance tracking
- **Marketplace** - List and manage farm produce
- **Trade Listings** - Import/Export trade opportunities
- **Weather Integration** - Real-time weather data using OpenWeatherMap API
- **Soil Sensors** - Track soil moisture, pH, and temperature
- **Carbon Tracking** - Monitor environmental sustainability efforts
- **Analytics** - Farm performance metrics and insights

## Technology Stack

- **Backend**: Flask 3.0+
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **Security**: CORS, Rate Limiting, Input Validation
- **API Documentation**: RESTful API design

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. Clone the repository
```bash
git clone https://github.com/ryankemei61-lgtm/Mukulima-bora.git
cd Mukulima-bora
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application
```bash
python mukulima_bora_secure.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new farmer
- `POST /api/users/login` - Login and get JWT token

### Finance
- `GET /api/finance/balance` - Get wallet balance
- `POST /api/finance/pay` - Make payment from wallet
- `GET /api/finance/transactions` - View transaction history

### Marketplace
- `POST /api/marketplace/add` - Add produce listing
- `GET /api/marketplace/list` - View produce listings

### Trade
- `POST /api/trade/create` - Create trade listing
- `GET /api/trade/list` - View trade listings

### Weather
- `GET /api/weather/current?lat=<lat>&lon=<lon>` - Get weather forecast

### Sensors
- `POST /api/sensors/add` - Add soil sensor data
- `GET /api/sensors/list` - View sensor data history

### Carbon
- `POST /api/carbon/add` - Record carbon offset
- `GET /api/carbon/list` - View carbon records

### Analytics
- `GET /api/analytics/farm/<farmer_id>` - Get farm analytics

## Security Features

✅ **Implemented Security**
- Password hashing with werkzeug
- JWT authentication tokens
- Input validation for all endpoints
- Rate limiting on auth endpoints
- CORS configuration
- SQL injection prevention
- Null/reference checks
- Transaction safety with database locks
- Comprehensive error handling
- Request logging

## Environment Configuration

Create a `.env` file:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
WEATHER_API_KEY=your-openweather-key
DATABASE_URL=sqlite:///mukulima.db
ALLOWED_ORIGINS=http://localhost:3000
```

## Example API Usage

### Register
```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer1",
    "email": "farmer@example.com",
    "password": "SecurePass123",
    "location": "Nairobi",
    "farm_size": 2.5
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer1",
    "password": "SecurePass123"
  }'
```

### Add Produce
```bash
curl -X POST http://localhost:5000/api/marketplace/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Maize",
    "quantity": 100,
    "price": 50,
    "unit": "kg"
  }'
```

## Database Models

- **Farmer** - User profiles with farm information
- **Wallet** - Financial accounts for transactions
- **Transaction** - Payment and financial records
- **Produce** - Marketplace listings
- **TradeListing** - Import/Export opportunities
- **SoilData** - Sensor readings
- **CarbonRecord** - Environmental tracking

## Error Handling

All endpoints return standardized responses:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use PostgreSQL instead of SQLite
3. Update `SECRET_KEY` and `JWT_SECRET_KEY`
4. Configure CORS with specific origins
5. Use gunicorn:
```bash
gunicorn mukulima_bora_secure:app
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Issues & Improvements

Check the [GitHub Issues](https://github.com/ryankemei61-lgtm/Mukulima-bora/issues) page for:
- Bug reports
- Feature requests
- Known issues
- Improvements needed

## License

This project is licensed under MIT License.

## Contact

For questions or support, contact: ryankemei61@gmail.com

## Acknowledgments

- Flask and SQLAlchemy communities
- OpenWeatherMap for weather API
- Contributors and testers
