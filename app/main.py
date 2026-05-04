"""
ShiftSaaS - Vardiya ve Personel Yönetim Sistemi
Cloud-based Shift Management SaaS Application
Built with Flask + SQLite (3-tier MVC architecture)
"""

from flask import Flask
from app.database import init_db
from app.routes.auth_routes import auth_bp
from app.routes.personnel_routes import personnel_bp
from app.routes.shift_routes import shift_bp
from app.routes.checkin_routes import checkin_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'shiftsaas-secret-key-2026'
    app.config['DATABASE'] = 'shiftsaas.db'

    init_db()

    # Register blueprints (Controller layer)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(personnel_bp, url_prefix='/api/personnel')
    app.register_blueprint(shift_bp, url_prefix='/api/shifts')
    app.register_blueprint(checkin_bp, url_prefix='/api/checkin')

    @app.route('/')
    def index():
        return {
            "message": "ShiftSaaS API is running",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "personnel": "/api/personnel",
                "shifts": "/api/shifts",
                "checkin": "/api/checkin"
            }
        }

    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "ShiftSaaS"}

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
