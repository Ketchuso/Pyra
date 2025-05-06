#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Article, Comment, FactCheck, Vote
from datetime import datetime

fake = Faker()

# Create sample users
def create_users():
    users = []
    for i in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.email()
        )
        user.password_hash = f"Password{i}"  # Uses the secure setter
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return users

# Create sample articles
def create_articles(users):
    articles = [
        Article(
            title="Bystander Becomes ‘Lifesaver’ Leaping into Ocean When Bull Shark Bites Swimmer Off Deserted Beach",
            url="https://www.goodnewsnetwork.org/bystander-becomes-lifesaver-leaping-into-ocean-when-bull-shark-bites-swimmer-off-deserted-beach/",
            image_url="https://www.goodnewsnetwork.org/wp-content/uploads/2025/05/A-bull-shark-in-the-Bahamas-public-domain-696x385.jpg",
            submitted_by_id=rc(users).id
        ),
        Article(
            title="Perpetually-Smiling Endangered Amphibian Now Thrives in Artificial Wetlands in Mexico City",
            url="https://www.goodnewsnetwork.org/perpetually-smiling-endangered-amphibian-now-thrives-in-artificial-wetlands-in-mexico-city/",
            image_url="https://www.goodnewsnetwork.org/wp-content/uploads/2025/05/A-captive-bred-leucistic-Axolotl-credit-LaDame-Bucolique-via-Pixabay-e1746429396644-696x416.jpg",
            submitted_by_id=rc(users).id
        ),
        Article(
            title="Woman Hires Private Detective and Finds 2 Long-Lost Sisters After 44 Years and the Death of Adoptive Parents",
            url="https://www.goodnewsnetwork.org/woman-hires-private-detective-and-found-2-long-lost-sisters-after-44-years-and-death-of-adoptive-parents/",
            image_url="https://www.goodnewsnetwork.org/wp-content/uploads/2025/05/Magda-Berg-with-her-two-sisters-Beata-and-Daria-via-SWNS--696x374.jpg",
            submitted_by_id=rc(users).id
        ),
        Article(
            title="Pollen Replacement Food for Honey Bees Brings New Hope for Struggling Colonies and the Crops They Support",
            url="https://www.goodnewsnetwork.org/pollen-replacement-food-for-honey-bees-brings-new-hope-for-struggling-colonies-and-the-crops-they-support/",
            image_url="https://www.goodnewsnetwork.org/wp-content/uploads/2025/05/Honey-beekeeper-inspects-colony-Photo-credit-College-of-Agricultural-Human-and-Natural-Resource-Sciences%E2%80%93WSU--696x375.jpg",
            submitted_by_id=rc(users).id
        ),
    ]
    
    # Add more articles if needed
    for article in articles:
        add_votes_for_articles(article)


    
    db.session.add_all(articles)
    db.session.commit()
    return articles

# Create sample comments
def create_comments(users, articles):
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    comments = []
    
    if len(articles) > 1:  # Ensure we have more than one article
        for _ in range(30):
            comment = Comment(
                content=lorem_text,
                user_id=rc(users).id,
                article_id=rc(articles[:-1]).id  # Exclude the last article
            )
            comments.append(comment)

        db.session.add_all(comments)
        db.session.commit()

# Create sample fact checks
def create_fact_checks(users, articles):
    lorem_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )
    fact_levels = [1, 2, 3, 4, 5]
    fact_checks = []

    for article in articles[:-1]:  # Exclude the last article
        for _ in range(7):
            fact_check = FactCheck(
                fact_check_level=rc(fact_levels),
                content=lorem_text,
                fact_check_url=fake.url(),
                user_id=rc(users).id,
                article_id=article.id
            )
            fact_checks.append(fact_check)

            # Add random upvotes/downvotes for each fact check
            add_votes_for_fact_check(fact_check)

    db.session.add_all(fact_checks)
    db.session.commit()

def add_votes_for_fact_check(fact_check):
    # Ensure fact_check is added to the session before using its ID
    db.session.add(fact_check)
    db.session.flush()  # This will flush the fact_check object to the database and assign it an ID

    # Random number of upvotes and downvotes
    num_upvotes = randint(5, 15)  # Upvotes between 5 and 15
    num_downvotes = randint(0, 5)  # Downvotes between 0 and 5
    
    # Create upvotes
    for _ in range(num_upvotes):
        vote = Vote(
            votable_id=fact_check.id, 
            votable_type='FactCheck', 
            value=1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    # Create downvotes
    for _ in range(num_downvotes):
        vote = Vote(
            votable_id=fact_check.id, 
            votable_type='FactCheck', 
            value=-1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    db.session.commit()  # Commit all the votes

def add_votes_for_articles(article):
    # Ensure fact_check is added to the session before using its ID
    db.session.add(article)
    db.session.flush()  # This will flush the fact_check object to the database and assign it an ID

    # Random number of upvotes and downvotes
    num_upvotes = randint(5, 15)  # Upvotes between 5 and 15
    num_downvotes = randint(0, 5)  # Downvotes between 0 and 5
    
    # Create upvotes
    for _ in range(num_upvotes):
        vote = Vote(
            votable_id=article.id, 
            votable_type='Article', 
            value=1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    # Create downvotes
    for _ in range(num_downvotes):
        vote = Vote(
            votable_id=article.id, 
            votable_type='Article', 
            value=-1, 
            user_id=rc([user.id for user in User.query.all()])
        )
        db.session.add(vote)

    db.session.commit()  # Commit all the votes

# Main function to run the seed script
def run_seed():
    with app.app_context():
        print("Seeding database...")

        # Drop all tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Populate with data
        users = create_users()
        articles = create_articles(users)
        create_comments(users, articles)
        create_fact_checks(users, articles)

        print("Database seeded successfully!")

# Run the seed function
if __name__ == "__main__":
    run_seed()
