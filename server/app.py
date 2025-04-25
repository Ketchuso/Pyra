#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, session, make_response, jsonify
from flask_restful import Resource
from datetime import timedelta
# from server.tasks import update_score

# Local imports
from config import app, db, api
# Add your model imports
from models import Article, User, Comment, FactCheck, Vote

import traceback

# Views go here!

class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        password_confirmation = data.get("password_confirmation", "").strip()

        if not all([username, email, password, password_confirmation]):
            return {"error": "All fields are required."}, 400

        if password != password_confirmation:
            return {"error": "Passwords do not match."}, 400

        try:
            user = User(username=username, email=email)
            user.password_hash = password  # This should trigger any validation logic
            db.session.add(user)
            db.session.commit()
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except Exception as e:
            db.session.rollback()
            print("Server Error:", e)  # Make sure this prints!
            traceback.print_exc()
            return {"error": "Something went wrong on the server."}, 500

        # Set up session
        stay_signed_in = data.get("stay_signed_in", False)
        session.permanent = stay_signed_in
        if stay_signed_in:
            app.permanent_session_lifetime = timedelta(days=30)
        session["user_id"] = user.id

        return user.to_dict(), 201



class CheckSession(Resource):
    def get(self):
        user = db.session.get(User, session.get('user_id'))
        if user:
            return make_response(user.to_dict(), 200)
        else:
            return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password', '')
        stay_signed_in = data.get('stay_signed_in', False)

        query = db.select(User).where(User.username == username)
        user = db.session.execute(query).scalar_one_or_none()

        if user and user.check_password(password):
            session.permanent = stay_signed_in
            if stay_signed_in:
                app.permanent_session_lifetime = timedelta(days=30)
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id', None)
            return make_response('', 204)
        else:
            return {"error": "Not logged in"}, 401
        
class Articles(Resource):
    def get(self):
        try:
            articles = db.session.query(Article).all()
            return jsonify([article.to_dict() for article in articles])
        except Exception as e:
            print("Articles route error:", e)
            return {"error": str(e)}, 500

class ArticleById(Resource):
    def get(self, id):
        try:
            # Fetch article by id
            article = db.session.get(Article, id)
            
            if not article:
                return jsonify({"error": "Article not found"}), 404
            
            # Return article data in JSON format
            return jsonify(article.to_dict())
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

class UserById(Resource):
    def get(self, id):
        try:
            user = db.session.get(User, id)

            if not user:
                return jsonify({"error": "User was not found"}), 404
            
            return jsonify(user.to_dict())
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

class Votes(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        votable_type = data.get("votable_type")  # 'Article', 'Comment', 'FactCheck'
        votable_id = data.get("votable_id")

        try:
            value = int(data.get("value")) 
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing vote value"}), 400

        # Validate votable_type
        valid_types = {"Article", "Comment", "FactCheck"}
        if votable_type not in valid_types:
            return jsonify({"error": f"Invalid votable_type. Must be one of {valid_types}"}), 400

        if value not in (-1, 0, 1):
            return jsonify({"error": "Vote value must be +1, 0, or -1"}), 400


        # Try to find existing vote
        vote = db.session.query(Vote).filter_by(
            user_id=user_id,
            votable_type=votable_type,
            votable_id=votable_id
        ).first()

        if vote:
            if value == 0:
                db.session.delete(vote)
            else:
                vote.value = value
        else:
            if value != 0:
                vote = Vote(
                    user_id=user_id,
                    votable_type=votable_type,
                    votable_id=votable_id,
                    value=value
                )
                db.session.add(vote)

        db.session.commit()

        like_count = db.session.query(Vote).filter_by(
            votable_type=votable_type,
            votable_id=votable_id,
            value=1
        ).count()

        dislike_count = db.session.query(Vote).filter_by(
            votable_type=votable_type,
            votable_id=votable_id,
            value=-1
        ).count()

        return jsonify({
            "result": "vote recorded",
            "votable_type": votable_type,
            "votable_id": votable_id,
            "value": value,
            "likes": like_count,
            "dislikes": dislike_count
        })
    
    def get(self, votable_type, votable_id):
        try:
            like_count = db.session.query(Vote).filter_by(
                votable_type=votable_type,
                votable_id=votable_id,
                value=1
            ).count()

            dislike_count = db.session.query(Vote).filter_by(
                votable_type=votable_type,
                votable_id=votable_id,
                value=-1
            ).count()

            return jsonify({
                "likes": like_count,
                "dislikes": dislike_count
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Add to API
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Articles, '/articles')
api.add_resource(ArticleById, '/article/<int:id>')
api.add_resource(UserById, '/user/<int:id>')
api.add_resource(Votes, '/votes', '/votes/<string:votable_type>/<int:votable_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
