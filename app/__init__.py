from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, ma, cors, swagger, limiter

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    swagger.init_app(app)
    limiter.init_app(app)

    from app.models.author import Author
    from app.models.book import Book
    from app.models.user import User
    from app.models.loan import Loan

    from app.routes.book_routes import book_bp
    from app.routes.author_routes import author_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.loan_routes import loan_bp

    app.register_blueprint(book_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(loan_bp)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "not_found", "message": "Ressource introuvable"}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {"error": "internal_error", "message": "Erreur interne du serveur"}, 500

    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "error"

        status_code = 200 if db_status == "ok" else 503
        return {"status": "ok" if db_status == "ok" else "degraded", "database": db_status}, status_code

    return app