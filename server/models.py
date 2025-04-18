from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime, timezone
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

def get_utc_now():
    return datetime.now(timezone.utc)

# Models go here!
class Article (db.Model, SerializerMixin):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable = False)


    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    #relationships
    user = db.relationship('user', back_populates='article')
    comment = db.relationship('comment', back_populates='article', cascade='all, delete-orphan')
    fact_check = db.relationship('fact_check', back_populates='article', cascade='all, delete-orphan')

class User (db.Model, SerializerMixin, UserMixin):
    __tablename__ = "user" 

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False, unique=True)
    email = db.Column(db.String, nullable = False, unique = True)
    _password_hash = db.Column(db.String, nullable = False)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    # edit for google auth later
    
    #relationships
    article = db.relationship('article', back_populates = 'user')
    comment = db.relationship('comment', back_populates = 'user', cascade='all, delete-orphan')
    fact_check = db.relationship('fact_check', back_populates = 'user')

    @hybrid_property
    def password_hash(self):
        raise Exception("Password hashes can't be viewed.")
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode("utf-8")
    
    def check_password(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )

class Comment (db.Model, SerializerMixin):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String, nullable = False)

    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    #comment relationships
    user = db.relationship('user', back_populates = 'comment')
    article = db.relationship('article', back_populates = 'comment')

class FactCheck (db.Model, SerializerMixin):
    __tablename__ = "fact_check"
    id = db.Column(db.Integer, primary_key = True)
    verified_status = db.Column(db.Boolean, nullable = False)
    source = db.Column(db.String, nullable = False)
    fact_check_url = db.Column(db.String)
    
    #add relationship for article and user
    user = db.relationship('user', back_populates = 'fact_check')
    article = db.relationship('article', back_populates = 'article')

# class Category (db.Model, SerializerMixin):
#     __tablename__ = "category"
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String, nullable = False)

# class ArticleCategory (db.Model, SerializerMixin):
#     __tablename__ = "article_category"
#     #join table between Article and Category
#     pass


