from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm, QuizForm
from .models import Todo, Perfume
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
import pymongo
from todo import config
from django.views.generic import ListView
from django.http import JsonResponse
import pandas as pd
import requests
from bson.objectid import ObjectId

username = config.username
password = config.password

client = pymongo.MongoClient(
    f"mongodb+srv://{username}:{password}@cluster0.n2hnd.mongodb.net/ifresearch?retryWrites=true&w=majority")
collection = client.test.sephora_backup3


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        # create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],
                                                request.POST['password1'],
                                                request.POST['password2'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Username already taken'})

        else:
            # tell teh user the passwords didn't match
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Passwords did not match'})


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
            print("request.method: ", request.method)
            print("user: ", user)
            login(request, user)
            return redirect('recommend')


@login_required()
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': todos})


@login_required()
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos': todos})


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
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html',
                          {'form': TodoForm(), 'error': 'Bad data passed in. Try again.'})


@login_required()
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


def collaborative_recommendation(users, k):
    # je veux tous les items que l'utilisateur a liké
    users = ["Jackobear"]
    perfumes_commented = list(collection.aggregate([
        {"$match": {"q2.Results.UserNickname": {"$in": users}}},
        {"$unwind": "$q2.Results"},
        {"$match": {"q2.Results.UserNickname": {"$in": users}}},
        {"$project": {"d": 1}}
    ]))
    all_perfumes = list(collection.aggregate([
        {"$match": {"q2.Results.UserNickname": {"$nin": users}}},
        {"$unwind": "$q2.Results"},
        {"$match": {"q2.Results.UserNickname": {"$nin": users}}},
        {"$project": {"d": 1}}
    ]))
    # je crée un vecteur de goût
    for attribute in perfumes_commented[0]['d']['attributs'].items():
        print("attribute[1]: ", attribute[1])
        up_dict = {attribute[0]: sum(attribute[1].values())}
        perfumes_commented[0]['d']['attributs'].update(up_dict)
    target_preferences = pd.DataFrame(perfumes_commented[0]['d']['attributs'], index=[str(perfumes_commented[0]['_id'])])

    rows_list = []
    # je crée un vecteur de tous les autres parfums
    for perfume in all_perfumes:
        for attribute in perfume['d']['attributs'].items():
            print("attribute[1]: ", attribute[1])
            up_dict = {attribute[0]: sum(attribute[1].values())}
            perfume['d']['attributs'].update(up_dict)
        rows_list.append(perfume['d']['attributs'])
    perfumes = pd.DataFrame(rows_list)
    # et je fais le produit entre le vecteur de préférence et la matrice de tous les autres produits
    scores = target_preferences.dot(perfumes)
    # je récupère les k parfumns qui ont les meilleurs scores
    s = scores.sum().sort(ascending=False, inplace=False)
    scores = scores.ix[:, s.index]
    best_perfumes = scores[s.index[:k]].columns
    return best_perfumes


@login_required()
def recommend(request):
    if request.method == 'GET':
        userid = request.user
        # On récupère le modèle
        recs = collaborative_recommendation(users=[str(userid)], k=5)
        if recs:
            perfume_id = [str(i) for i in recs['perfume_id']]
            rec_perfumes = list(collection.find({'perfume_id': {'$in': perfume_id}},
                                                {'item_name': 1, 'brand': 1, 'gender': 1,
                                                 'note': 1, 'tags': 1, 'theme': 1, '_id': 0}))
        return render(request, 'todo/table.html', {'liked': None, 'recommendations': None})


def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.delete()
        return redirect('currenttodos')


def quiz(request):
    with open('todo/templates/todo/data/keywords.json') as f:
        keywords = json.load(f)
    with open('todo/templates/todo/data/notes.json') as f:
        notes = json.load(f)
    with open('todo/templates/todo/data/themes.json') as f:
        themes = json.load(f)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            keywords_selected = form.cleaned_data['keywords_selected']
            print("keywords_selected: ", keywords_selected)
    form = QuizForm()
    return render(request, 'todo/quiz2.html', {'form': form, 'keywords': keywords, 'notes': notes, 'themes': themes})


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

def get_top_products(selected_words):
    """
    :param selected_words: the words selected by the user to describe the perfume wanted
    :return: the list of top 5 perfume corresponding to the o
    """
    selected_words = selected_words.lower()
    query = {'features': selected_words}
    r = requests.get('https://perfumerecommender-api.herokuapp.com/perfume', params=query)
    products = r.json()
    return products


def getmatch(request):
    if request.method == 'POST':
        selected_words = querydict_to_dict(request.POST)['keywords[]']
        client = pymongo.MongoClient(
            f"mongodb+srv://{username}:{password}@cluster0.n2hnd.mongodb.net/ifresearch?retryWrites=true&w=majority")
        top_products = get_top_products(selected_words)

        collection = client.test.sephora_backup3
        top_products = [ObjectId(x) for x in top_products['perfumes']]
        print(top_products)
        products = collection.find({'_id': {"$in": top_products}})
        print("products[0]: ", products[0])
        return render(request, 'todo/result.html', {'products': products})


def similar(request):
    return render(request, 'todo/search_similar.html')


class SearchResultsView(ListView):
    model = Perfume
    template_name = 'todo/search_similar_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get('q')
        object_list = list(collection.aggregate([
            {
                '$search': {
                    'index': 'default',
                    'compound': {
                        'must': {
                            'text': {
                                'query': str(query),
                                'path': 'name',
                                'fuzzy': {
                                    'maxEdits': 2
                                }
                            }
                        }
                    }
                }
            }
        ]
        ))
        return [x for x in object_list]


def search(request):
    # params = request.GET
    # query = params.get('q', '')
    query = request.GET.get('query')
    pipeline = [
        {
            '$search': {
                'index': 'default',
                'compound': {
                    'must': {
                        'text': {
                            'query': str(query),
                            'path': 'name',
                            'fuzzy': {
                                'maxEdits': 2
                            }
                        }
                    }
                }
            }
        },
        {
            "$limit": 10
        },
        {
            "$project": {
                "_id": 0,
                "name": 1
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    data = {'data': result}
    return JsonResponse(data)
