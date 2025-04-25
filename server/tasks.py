from celery import Celery
import time
from server.models import db, Article, User, Comment, FactCheck, Vote
from server.app import create_app

# Initialize Celery
celery = Celery(
    "tasks",
    broker="valkey://localhost:6379/0",   # Changed from redis:// to valkey://
    backend="valkey://localhost:6379/0"   # Changed from redis:// to valkey://
)

# Optional Flask context, useful if you're touching the DB inside tasks
flask_app = create_app()

@celery.task
def update_score(post_id):
    with flask_app.app_context():  # Ensures we are in the Flask app context
        time.sleep(5)  # Delay to allow for batching votes
        post = Post.query.get(post_id)
        if post:
            post.score = post.calculate_score()  # Your model's method for calculating score
            db.session.commit()
            print(f"Score updated for post {post_id}: {post.score}")
