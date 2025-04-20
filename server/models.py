from sqlalchemy_serializer import SerializerMixin
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import re

def get_utc_now():
    return datetime.now(timezone.utc)

# Mixin for automatic timestamps
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)


# =====================
# Models
# =====================

# Article Model 
class Article(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)

    # Relationships
    submitted_by = db.relationship('User', back_populates='submitted_articles')
    comments = db.relationship('Comment', back_populates='article', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='article', cascade='all, delete-orphan')

    serialize_rules = ('-user.articles', '-comments.article', '-fact_checks.article')


# User Model
class User(db.Model, SerializerMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    submitted_articles = db.relationship('Article', back_populates='submitted_by')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    fact_checks = db.relationship('FactCheck', back_populates='user', passive_deletes=True)

    serialize_rules = ('-_password_hash', '-articles.user', '-comments.user', '-fact_checks.user')

    # Password Handling
    @hybrid_property
    def password_hash(self):
        raise Exception("Password hashes can't be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        # Check if the password is empty or only contains whitespace
        if not password or not password.strip():
            raise ValueError("Password can't be blank")

        # Password length rule
        if len(password.strip()) < 6:
            raise ValueError("Password has to be at least 6 characters long")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must have at least one lowercase letter")

        # At least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must have at least one uppercase letter")

        # At least one digit
        if not re.search(r'\d', password):
            raise ValueError("Password must have at least one number")

        # No spaces allowed in the password
        if ' ' in password:
            raise ValueError("Password cannot have spaces")

        # If all checks pass, hash the password
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))


# Comment Model
class Comment(db.Model, SerializerMixin, TimestampMixin):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='comments')
    article = db.relationship('Article', back_populates='comments')

    serialize_rules = ('-user.comments', '-article.comments')


# FactCheck Model
class FactCheck(db.Model, SerializerMixin):
    __tablename__ = "fact_check"

    id = db.Column(db.Integer, primary_key=True)
    verified_status = db.Column(db.Boolean, nullable=False)
    content = db.Column(db.String(2000), nullable=True)
    source = db.Column(db.String(150), nullable=False)
    fact_check_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete='CASCADE'), nullable=False)
    # Relationships
    user = db.relationship('User', back_populates='fact_checks')
    article = db.relationship('Article', back_populates='fact_checks')

    serialize_rules = ('-user.fact_checks', '-article.fact_checks')


# Uncomment these when ready to use categories
# class Category(db.Model, SerializerMixin):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)

# class ArticleCategory(db.Model, SerializerMixin):
#     __tablename__ = "article_category"
#     # Join table between Article and Category
#     pass
