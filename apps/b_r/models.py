from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
import datetime

pass_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}')
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def register_validator(self, post_data):
        errors = []

        if len(post_data['name']) < 1:
            errors.append("Name field cannot be empty")
        if not post_data['name'].isalpha:
            errors.append("Name must only include letters")
        if len(post_data['username']) < 1:
            errors.append("Username field cannot be empty")
        if len(User.objects.filter(username = post_data['username'])) > 0:
            errors.append("Username is not available. Please try another username.")
        if len(User.objects.filter(email = post_data['email'])) > 0:
            errors.append("Email address is currently registered. Please login.")
        if not email_regex.match(post_data['email']):
            errors.append("Email address format is not valid")
        if not pass_regex.match(post_data['pw']):
            errors.append("Password format is not valid")
        if not post_data['pw'] == post_data['pw_confirm']:
            errors.append("Passwords do not match")
        
        if not errors:
            hashed = bcrypt.hashpw(post_data['pw'].encode(), bcrypt.gensalt(5))
            user = User(
                name = post_data['name'],
                username = post_data['username'],
                email = post_data['email'],
                password = hashed
            )
            user.save()
            return user
        else:
            return errors

    def login_validator(self, post_data):
        errors = []

        if len(self.filter(username = post_data['username'])) > 0:
            user = self.filter(username = post_data['username'])[0]
            if not bcrypt.checkpw(post_data['pw'].encode(), user.password.encode()):
                errors.append("Password is not valid")
        else:
            errors.append("Username is not valid")

        if errors:
            return errors
        else:
            return user

class ReviewManager(models.Manager):
    def book_review_validator(self, post_data):
        errors = []
        print post_data
        if len(post_data['title']) < 1:
            errors.append("Title field cannot be empty")
        if len(post_data['author_new']) < 1 and not 'author_exist' in post_data:
            errors.append("Must select an existing author or add a new author")
        if len(post_data['author_new']) > 0 and len(Author.objects.filter(name = post_data['author_new'])) > 0:
            errors.append("Author already exists in the database. Select from Existing Authors.")
        if len(post_data['review']) < 1:
            errors.append("Review field cannot be empty")
        
        if not errors:
            if len(post_data['author_new']) > 0:
                author = Author(
                    name = post_data['author_new']
                )
                author.save()
            else:
                author = Author.objects.filter(name = post_data['author_exist'])[0]
            
            if len(Book.objects.filter(title = post_data['title'])) > 0:
                book = Book.objects.filter(title = post_data['title'])[0]
            else:
                book = Book(
                    title = post_data['title'],
                    author = author
                )
                book.save()

            user = User.objects.get(id=post_data['user_id'])
            review = Review(
                review = post_data['review'],
                rating = post_data['rating'],
                reviewed_by = user,
                book = book
            )
            review.save()
            return book
        else:
            return errors
    
    def review_validator(self, post_data):
        errors = []

        if len(post_data['review']) < 1:
            errors.append("Review field cannot be empty")
            return errors
        else:
            book = Book.objects.get(id=post_data['book_id'])
            user = User.objects.get(id=post_data['user_id'])
            review = Review(
                review = post_data['review'],
                rating = post_data['rating'],
                reviewed_by = user,
                book = book
            )
            review.save()
        
    def recent_and_not(self):
        reviews = (self.all().order_by('-created_at')[:3], self.all().order_by('-created_at')[3:])
        return reviews

class User(models.Model):
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):     
        return "%s" % (self.username)

class Author(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):     
        return "%s" % (self.name)

class Book(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, related_name="books")

    def __str__(self):     
        return "%s %s %s" % (self.title, self.author.name, self.uploaded_by.username)

class Review(models.Model):
    review = models.TextField()
    rating = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, related_name="user_reviews")
    book = models.ForeignKey(Book, related_name="book_reviews")
    objects = ReviewManager()

    def __str__(self):     
        return "%s %s %s" % (self.reviewed_by.username, self.book.title, self.review)