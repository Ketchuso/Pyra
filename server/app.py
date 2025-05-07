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
        sort_type = request.args.get('sort', 'hot')
        try:
            if sort_type == 'new':
                articles = db.session.query(Article).order_by(Article.created_at.desc()).all()
            elif sort_type == 'hot':
                articles = db.session.query(Article).all()
                articles = sorted(articles, key=lambda a: a.hotness(), reverse=True)
            else:
                return {"error": "unsupported sorting type"}, 400

            return jsonify([article.to_dict() for article in articles])

        except Exception as e:
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
    
    def patch(self, id):
        try:
            # Fetch article by id
            article = db.session.get(Article, id)
            data = request.get_json()

            def is_valid_str(value):
                return isinstance(value, str) and value.strip()

            if not article:
                return jsonify({"error": "Article not found"}, 404)
            
            if "image_url" in data:
                if is_valid_str(data['image_url']):
                    article.image_url = data["image_url"]
                else:
                    return jsonify({"error": "Invalid image url"}, 400)
            
            if "title" in data:
                if is_valid_str(data['title']):
                    article.title = data["title"]
                else:
                    return jsonify({"error": "Invalid title"}, 400)

            if "url" in data:
                if is_valid_str(data['url']):
                    article.url = data["url"]
                else:
                    return jsonify({"error": "Invalid url"}, 400)
            
            db.session.commit()
            return make_response(article.to_dict(), 200)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def delete(self, id):
        article = db.session.get(Article, id)
        if not article:
            return make_response({"error": "Article not found"}, 400)
        
        db.session.delete(article)
        db.session.commit()
        return make_response("", 204)
    
class CreateArticle(Resource):
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['image_url', 'title', 'url']
            for field in required_fields:
                if field not in data or not isinstance(data[field], str) or not data[field].strip():
                    return jsonify({"error": f"Invalid or missing field: {field}"}), 400
            
            if 'submitted_by_id' not in data or not isinstance(data['submitted_by_id'], int):
                return jsonify({"error": "Invalid or missing field: submitted_by_id"}), 400

            new_article = Article(image_url = data['image_url'], title = data['title'], url = data['url'], submitted_by_id = data['submitted_by_id'])
            db.session.add(new_article)
            db.session.commit()
            return make_response(new_article.to_dict(), 201)
        
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
        
    def patch(self, id):
        try:
            user = db.session.get(User, id)

            if not user: 
                return {"error": "User was not found"}, 404
            
            data = request.get_json()

            if "username" in data:
                existing_user = db.session.query(User).filter(User.username == data["username"]).first()
                if existing_user and existing_user.id != user.id:
                    return {"error": "Username already taken!"}, 400
                elif existing_user and existing_user.id == user.id:
                    return {"error": "That is your current username, silly goose!"}, 400
                
                user.username = data['username']
            
            if "email" in data:
                existing_email = db.session.query(User).filter(User.email == data['email']).first()
                if existing_email and existing_email.id != user.id:
                    return {"error": "Email already in use"}, 400
                elif existing_email and existing_email.id == user.id:
                    return {"error": "That is your current email silly goose!"}, 400

                user.email = data['email']
                
            if "password" in data:
                if user.check_password(data["password"]):
                    return {"error": "That is your current password, silly goose!"}, 400
                
                user.password_hash = data['password']

            db.session.commit()
            return user.to_dict(), 200

        except Exception as e:
            return {"error": str(e)}, 500
        
    # def delete(self, id):
    #     user = db.session.get(User, id)
    #     if not user:
    #         return make_response({"error": "User not found"}, 400)
        
    #     db.session.delete(user)
    #     db.session.commit()
    #     return make_response("", 204)



class Votes(Resource):
    def post(self, votable_type, votable_id):
        data = request.get_json()
        user_id = data.get("user_id")

        try:
            value = int(data.get("value")) 
        except (ValueError, TypeError):
            return {"error": "Invalid or missing vote value"}, 400

        # Validate votable_type
        valid_types = {"Article", "Comment", "FactCheck"}
        if votable_type not in valid_types:
            return {"error": f"Invalid votable_type. Must be one of {valid_types}"}, 400

        if value not in (-1, 0, 1):
            return {"error": "Vote value must be +1, 0, or -1"}, 400


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

        return {
            "result": "vote recorded",
            "votable_type": votable_type,
            "votable_id": votable_id,
            "value": value,
            "likes": like_count,
            "dislikes": dislike_count
        }, 200
    
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

class CreateFactCheck(Resource):
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['content']
            for field in required_fields:
                if field not in data or not isinstance(data[field], str) or not data[field].strip():
                    return {"error": f"Invalid or missing field: {field}"}, 400
            
            if 'fact_check_level' not in data or not isinstance(data['fact_check_level'], int):
                return {"error": "Invalid or missing field: fact_check_level"}, 400
            
            if 'article_id' not in data or not isinstance(data['article_id'], int):
                return {"error" : "Article_id must not be null or invalid"}
            
            new_fact_check = FactCheck(
                content=data['content'],
                fact_check_level=data['fact_check_level'],
                article_id=data['article_id'],
                fact_check_url=data.get('fact_check_url'),
                user_id = data.get('user_id')
            )

            db.session.add(new_fact_check)
            db.session.commit()
            return make_response(new_fact_check.to_dict(), 201)
        
        except Exception as e:
            return {"error": str(e)}, 500

class FactCheckById(Resource):
    def patch(self, id):
        try:
            fact_check = db.session.get(FactCheck, id)

            if not fact_check: 
                return {"error": "FactCheck not found"}, 404
            
            data = request.get_json()

            if "fact_check_level" in data:
                if not isinstance(data['fact_check_level'], int):
                    return {"error": "fact_check_level must be an integer"}, 400
                if not (0 <= data["fact_check_level"] <= 4):
                    return {"error": "fact_check_level must be between 0 and 4"}, 400

                fact_check.fact_check_level = data["fact_check_level"]
            
            if "content" in data:
                if not isinstance(data['content'], str):
                    return {"error": "Content must be a string"}, 400
                if not (0 < len(data['content']) <= 2000):  # Content length should be between 1 and 2000
                    return {"error": "fact check content must be between 1 and 2000 characters"}, 400
                
                fact_check.content = data['content']
            
            if "fact_check_url" in data:
                if not isinstance(data['fact_check_url'], str):
                    return {"error": "fact_check_url must be a string"}, 400
                if not (0 < len(data['fact_check_url']) <= 255):
                    return {"error": "fact_check_url must be between 1 and 255 characters"}
                
                fact_check.fact_check_url = data['fact_check_url']

            db.session.commit()
            return fact_check.to_dict(), 200

        except Exception as e:
            return {"error": str(e)}, 500
    
    def delete(self, id):
        fact_check = db.session.get(FactCheck, id)
        if not fact_check:
            return make_response({"error": "FactCheck not found"}, 400)
        
        db.session.delete(fact_check)
        db.session.commit()
        return make_response("", 204)

        
class CreateComment(Resource):
    def post(self):
        try:
            data = request.get_json()
            required_fields = ['content']
            for field in required_fields:
                if field not in data or not isinstance(data[field], str) or not data[field].strip():
                    return {"error": f"Invalid or missing field: {field}"}, 400
            
            if 'user_id' not in data or not isinstance(data['user_id'], int):
                return {"error": "Invalid or missing field: user_id"}, 400
            
            if 'article_id' not in data or not isinstance(data['article_id'], int):
                return {"error" : f"Article_id must not be null or invalid"}, 400
            
            new_comment = Comment(
                content=data['content'],
                user_id=data['user_id'],
                article_id=data['article_id']
            )

            db.session.add(new_comment)
            db.session.commit()
            return make_response(new_comment.to_dict(), 201)
        
        except Exception as e:
            return {"error": str(e)}, 500
        
class CommentById(Resource):
    def patch(self, id):
        try:
            comment = db.session.get(Comment, id)

            if not comment: 
                return {"error": "Comment not found"}, 404
            
            data = request.get_json()
            
            if "content" in data:
                if not isinstance(data['content'], str):
                    return {"error": "Content must be a string"}, 400
                if not (0 < len(data['content']) <= 1000):  # Content length should be between 1 and 2000
                    return {"error": "comment content must be between 1 and 2000 characters"}, 400
                
                comment.content = data['content']

            db.session.commit()
            return comment.to_dict(), 200

        except Exception as e:
            return {"error": str(e)}, 500
    
    def delete(self, id):
        comment = db.session.get(Comment, id)
        if not comment:
            return make_response({"error": "Comment not found"}, 400)
        
        db.session.delete(comment)
        db.session.commit()
        return make_response("", 204)
        
# Add to API
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Articles, '/articles')
api.add_resource(ArticleById, '/article/<int:id>')
api.add_resource(CreateArticle, '/create_article')
api.add_resource(UserById, '/user/<int:id>')
api.add_resource(Votes, '/votes/<string:votable_type>/<int:votable_id>')
api.add_resource(CreateFactCheck, '/create_fact_check')
api.add_resource(CreateComment, '/create_comment')
api.add_resource(FactCheckById, '/fact_check/<int:id>')
api.add_resource(CommentById, '/comment/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
