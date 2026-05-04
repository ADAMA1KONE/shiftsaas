from flask import Flask, jsonify
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

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(personnel_bp, url_prefix='/api/personnel')
    app.register_blueprint(shift_bp, url_prefix='/api/shifts')
    app.register_blueprint(checkin_bp, url_prefix='/api/checkin')

    @app.route('/')
    def index():
        return '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShiftSaaS - Vardiya Yonetim Sistemi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; color: #333; }
        .header {
            background: linear-gradient(135deg, #1a3c6e, #2563eb);
            color: white; padding: 40px 20px; text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .badge {
            display: inline-block; background: #22c55e;
            color: white; padding: 6px 16px; border-radius: 20px;
            font-size: 0.9em; margin-top: 12px;
        }
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .card {
            background: white; border-radius: 12px;
            padding: 24px; margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .card h2 { color: #1a3c6e; margin-bottom: 16px; font-size: 1.3em; }
        .endpoint {
            display: flex; align-items: center;
            padding: 10px 0; border-bottom: 1px solid #f0f0f0;
        }
        .endpoint:last-child { border-bottom: none; }
        .method {
            font-weight: bold; padding: 3px 10px; border-radius: 4px;
            font-size: 0.8em; min-width: 60px; text-align: center; margin-right: 12px;
        }
        .get { background: #dbeafe; color: #1d4ed8; }
        .post { background: #dcfce7; color: #166534; }
        .put { background: #fef9c3; color: #854d0e; }
        .delete { background: #fee2e2; color: #991b1b; }
        .url { font-family: monospace; font-size: 0.95em; color: #374151; }
        .desc { color: #6b7280; font-size: 0.85em; margin-left: auto; }
        .team-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px; margin-top: 8px;
        }
        .member {
            background: #f8fafc; border-radius: 8px; padding: 12px;
            text-align: center; border: 1px solid #e2e8f0;
        }
        .member .name { font-weight: bold; font-size: 0.9em; color: #1a3c6e; }
        .member .role { font-size: 0.8em; color: #64748b; margin-top: 4px; }
        .info-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }
        .info-item { background: #f8fafc; border-radius: 8px; padding: 14px; border-left: 4px solid #2563eb; }
        .info-item .label { font-size: 0.8em; color: #64748b; text-transform: uppercase; }
        .info-item .value { font-weight: bold; color: #1a3c6e; margin-top: 4px; }
        .footer { text-align: center; color: #9ca3af; font-size: 0.85em; padding: 30px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 ShiftSaaS</h1>
        <p>Bulut Tabanli Vardiya ve Personel Yonetim Sistemi</p>
        <div class="badge">✅ CANLI - DEPLOYED</div>
    </div>

    <div class="container">

        <div class="card">
            <h2>📊 Sistem Bilgisi</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="label">Durum</div>
                    <div class="value">🟢 Calisıyor</div>
                </div>
                <div class="info-item">
                    <div class="label">Versiyon</div>
                    <div class="value">v1.0.0</div>
                </div>
                <div class="info-item">
                    <div class="label">Platform</div>
                    <div class="value">Render Cloud</div>
                </div>
                <div class="info-item">
                    <div class="label">Mimari</div>
                    <div class="value">REST API / MVC</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔗 API Uc Noktalari</h2>

            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/auth/register</span>
                <span class="desc">Yeni personel kaydi</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/auth/login</span>
                <span class="desc">Kullanici girisi</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/personnel/</span>
                <span class="desc">Tum personeli listele</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/personnel/</span>
                <span class="desc">Personel olustur</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <span class="url">/api/personnel/{id}</span>
                <span class="desc">Personeli guncelle</span>
            </div>
            <div class="endpoint">
                <span class="method delete">DELETE</span>
                <span class="url">/api/personnel/{id}</span>
                <span class="desc">Personeli devre disi birak</span>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="url">/api/shifts/</span>
                <span class="desc">Vardiylari listele</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/shifts/</span>
                <span class="desc">Vardiya olustur (cakisma kontrolu)</span>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="url">/api/checkin/checkin</span>
                <span class="desc">GPS dogrulamali giris</span>
            </div>
            <div class="endpoint">
                <span class="method put">PUT</span>
                <span class="url">/api/checkin/checkout</span>
                <span class="desc">Cikis kaydi</span>
            </div>
        </div>

        <div class="card">
            <h2>👥 Proje Ekibi</h2>
            <div class="team-grid">
                <div class="member">
                    <div class="name">Ahmad Yasin</div>
                    <div class="role">Takim Lideri</div>
                </div>
                <div class="member">
                    <div class="name">Mehtap Gultepe</div>
                    <div class="role">Gelistirici</div>
                </div>
                <div class="member">
                    <div class="name">Adama Kone</div>
                    <div class="role">Gelistirici</div>
                </div>
                <div class="member">
                    <div class="name">Gulcin Civelek</div>
                    <div class="role">Gelistirici</div>
                </div>
                <div class="member">
                    <div class="name">Mukhidin Yussupov</div>
                    <div class="role">Test Uzmani</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🏫 Universite Bilgisi</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="label">Universite</div>
                    <div class="value">Istanbul Arel Universitesi</div>
                </div>
                <div class="info-item">
                    <div class="label">Odev</div>
                    <div class="value">HW5 - First SaaS Prototype</div>
                </div>
                <div class="info-item">
                    <div class="label">Bolum</div>
                    <div class="value">Bilgisayar Muhendisligi</div>
                </div>
                <div class="info-item">
                    <div class="label">Son Teslim</div>
                    <div class="value">5 Mayis 2026</div>
                </div>
            </div>
        </div>

    </div>
    <div class="footer">
        ShiftSaaS &copy; 2026 — Istanbul Arel Universitesi
    </div>
</body>
</html>
        '''

    @app.route('/health')
    def health():
        return jsonify({"status": "saglikli", "service": "ShiftSaaS"})

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
