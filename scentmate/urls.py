from django.contrib import admin
from django.urls import path
from todo import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('signup/', views.signupuser, name="signupuser"),
    path('logout/', views.logoutuser, name="logoutuser"),
    path('login/', views.loginuser, name="loginuser"),

    # Todos
    path('', views.home, name="home"),
    path('current/', views.currenttodos, name="currenttodos"),
    path('completed/', views.completedtodos, name="completedtodos"),
    path('todo/<int:todo_pk>', views.viewtodo, name="viewtodo"),
    path('todo/<int:todo_pk>/complete', views.completetodo, name="completetodo"),
    path('todo/<int:todo_pk>/delete', views.deletetodo, name="deletetodo"),
    path('create/', views.createtodo, name="createtodo"),

    # quiz
    path('quiz/', views.quiz, name="quiz"),
    path('quiz/getmatch/', views.getmatch, name="getmatch"),

    # similar
    path('similar/', views.similar, name='similar'),
    path('similar/similar_results/', views.SearchResultsView.as_view(), name='similar_results'),

    # api
    path('api/perfumes/', views.search, name='api'),

]
