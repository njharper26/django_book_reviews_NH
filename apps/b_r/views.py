from django.shortcuts import render, redirect
from models import *
from django.contrib import messages

def index(request):
    return render(request, 'b_r/index.html')

def process_register(request):
    result = User.objects.register_validator(request.POST)
    if type(result) == list:
        for error in result:
            messages.error(request, error)
        return redirect('/')
    else:
        messages.success(request, "Congrats, you have successfully registered!")
        request.session['id'] = result.id
        return redirect('/books')

def process_login(request):
    result = User.objects.login_validator(request.POST)
    if type(result) == list:
        for error in result:
            messages.error(request, error)
        return redirect('/')
    else:
        messages.success(request, "You have successfully logged in.")
        request.session['id'] = result.id
        return redirect('/books')

def logout(request):
    for key in request.session.keys():
        del request.session[key]
    return redirect('/')

def show(request):
    context = {
        'user': User.objects.get(id=request.session['id']),
        'recent_reviews': Review.objects.recent_and_not()[0],
        'old_reviews': Review.objects.recent_and_not()[1]
    }
    return render(request, 'b_r/show.html', context)

def add(request):
    context = {
        'authors': Author.objects.all()
    }
    return render(request, 'b_r/add.html', context)

def process_add_book_review(request):
    result = Review.objects.book_review_validator(request.POST)
    if type(result) == list:
        for error in result:
            messages.error(request, error)
        return redirect('/books/add')
    else:
        messages.success(request, "You successfully added a review!")
        id = result.id
        return redirect('/books/' + str(id))

def process_review(request, id):
    result = Review.objects.review_validator(request.POST)
    if type(result) == list:
        for error in result:
            messages.error(request, error)
        return redirect('/books/' + str(id))
    else:
        messages.success(request, "You successfully added a review!")
        return redirect('/books/' + str(id))

def book(request, id):
    context = {
        'book': Book.objects.get(id=id),
        'reviews': Book.objects.get(id=id).book_reviews.all().order_by('-created_at')
    }
    return render(request, 'b_r/book.html', context)

def user(request, id):
    user = User.objects.get(id=id)
    context = {
        'user': user,
        'reviews': user.user_reviews.all().order_by('-created_at'),
        'count': user.user_reviews.count()
    }
    return render(request, 'b_r/user.html', context)