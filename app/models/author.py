from app.extensions import db

class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    nationality = db.Column(db.String(80))
    bio = db.Column(db.Text)

    books = db.relationship("Book", back_populates="author", lazy="select")