from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # Programmatically create database tables
        db.create_all()
        
        # Seed default admin user if it doesn't exist
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin_user = User(
                email='admin@trekking.com',
                password_hash=generate_password_hash('admin123'),
                full_name='Super Admin',
                role='admin',
                status='approved'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin@trekking.com / admin123")

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Import and register blueprints
    from routes_auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from routes_admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from routes_staff import staff_bp
    app.register_blueprint(staff_bp)

    from routes_user import user_bp
    app.register_blueprint(user_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
