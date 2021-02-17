from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm, QuizForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
import pymongo
import todo.config as config

username = config.username
password = config.password


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        # create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], request.POST['password1'], request.POST['password2'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Username already taken'})

        else:
            # tell teh user the passwords didn't match
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error':'Passwords did not match'})

@login_required()
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(),
                                                           'error': 'username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required()
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos':todos})

@login_required()
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required()
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form,
                                                          'error': 'Bad Info'})
# 6383

@login_required()
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit = False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Bad data passed in. Try again.'})

@login_required()
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect('currenttodos')


def quiz(request):
    with open('todo/templates/todo/data/keywords_translated.json') as f:
        keywords = json.load(f)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            keywords_selected = form.cleaned_data['keywords_selected']
            print("keywords_selected: ", keywords_selected)
    form = QuizForm()
    return render(request, 'todo/quiz2.html', {'form': form, 'keywords': keywords})


def quiz2(request):
    form = QuizForm
    return render(request, 'todo/quiz2.html', {'form': form})


def querydict_to_dict(query_dict):
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data


def get_top_products(products, selected_words):
    # for each product we need to create the total scores on selected_words
    for product in products:
        total = 0
        for word in selected_words:
            total += product['d']['attributs'][word]['perceived_benefit']
        product['total'] = total
    return sorted(products, key = lambda i: i['total'])[5:]
    

def getmatch(request):
    if request.method == 'POST':
        print(request)
        if request.method == 'POST':
            selected_words = querydict_to_dict(request.POST)['keywords[]']
            print("result: ", selected_words)
            client = pymongo.MongoClient(
                f"mongodb+srv://{username}:{password}@cluster0.n2hnd.mongodb.net/ifresearch?retryWrites=true&w=majority")
            collection = client.test.sephora_backup3
            cursor = collection.find({})
            products = [x for x in cursor]
            # on veut celui qui maximise la somme des attributs dans results
            top_products = get_top_products(products, selected_words)

            print(top_products[0])
            return render(request, 'todo/result.html', {'products': top_products[:5]})


def similar(request):
    return render(request, 'todo/similar.html')
