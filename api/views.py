from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate
# Create your views here.
import json
from .models import *
import base64

@csrf_exempt
def user_management(request):
    username = request.POST.get("username" , None)
    password = request.POST.get("password" , None)
    sign_in = request.GET.get("sign_in" , False)
    final = {}
    if request.method == 'GET':
        final['success'] = False
        final['msg'] = "method not allowed"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 405)
    if username and password:
        if not sign_in:
            user , created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                final['success'] = True
                final['msg'] = "User created"
                return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 200)
            else:
                final['success'] = False
                final['msg'] = "User already registered with this username , please sign-in with correct creds"
                return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 400)
        else:
            auth_user = authenticate(username=username, password=password)
            if not auth_user:
                final['success'] = False
                final['msg'] = "Credentials didnt match!!"
                return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 400)
            final['success'] = True
            final['msg'] = ""
            return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 200)
    final['success'] = False
    final['msg'] = "Please provide username and password"
    return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 400)

    
def basic_authentication(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split(" ")
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode("utf8").split(':', 1)
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    return user
    return None

SORT_BY = ['latest' , 'oldest']

FILTER_BY = ['image' , 'text']

def sort_by_function(posts , sort_by):
    if sort_by == 'latest':
        posts = posts.order_by('-date_created')
    elif sort_by == 'oldest':
        posts = posts.order_by('date_created')
    return posts


def user_post_list(request):
    user = basic_authentication(request)
    final = {}
    if not user:
        final['success'] = False
        final['msg'] = "Please provide valid credentials!! NOTE:- Api works on Basic authentication"
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    sort_by = request.GET.get('sort' , None)
    search = request.GET.get('search' , None)
    posts = UserPost.objects.filter(user=user)
    if sort_by in SORT_BY:
        posts = sort_by_function(posts , sort_by)
    if search:
        posts = posts.filter(text__contains = search)
    data = []
    for post in posts:
        data.append(post.serialize)
    final['success'] = True
    final['data'] = data
    final['msg'] = ""
    return HttpResponse(json.dumps(final) , content_type = 'application/json', status = 200)

ALLOWED_FILES_TYPES = ['image/png' , 'image/jpeg' , "image/jpg"]

@csrf_exempt
def user_post_create(request):
    final = {}
    if request.method == 'GET':
        final['success'] = False
        final['msg'] = "method not allowed"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 405)
    user = basic_authentication(request)
    final = {}
    if not user:
        final['success'] = False
        final['msg'] = "Please provide valid credentials!! NOTE:- Api works on Basic authentication"
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    text = request.POST.get("text" , "")
    file = request.FILES.get('file' , None)
    if text or (file and file.content_type in ALLOWED_FILES_TYPES):
        UserPost.objects.create(user=user , text=text , image = file)
        final['success'] = True
        final['msg'] = "Sucessfully created!"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 200)
    final['success'] = False
    final['msg'] = "Please provide some data , image or text"
    return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)


@csrf_exempt
def user_comment(request,post_id):
    final = {}
    if request.method == 'GET':
        final['success'] = False
        final['msg'] = "method not allowed"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 405)
    user = basic_authentication(request)
    final = {}

    if not user:
        final['success'] = False
        final['msg'] = "Please provide valid credentials!! NOTE:- Api works on Basic authentication"
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    
    text = request.POST.get("text" , "")
    if text:
        try:
            up = UserPost.objects.get(id = post_id)
        except UserPost.DoesNotExist:
            final['success'] = False
            final['msg'] = "Post with id %s not found"%post_id
            return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)

        Comment.objects.create(post= up , user= user , text=text)
        final['success'] = True
        final['msg'] = "Sucessfully created!"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 200)

    final['success'] = False
    final['msg'] = "Please provide some comment!!"
    return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    

@csrf_exempt
def post_like_unlike(request,post_id):
    final = {}
    if request.method == 'GET':
        final['success'] = False
        final['msg'] = "method not allowed"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 405)
    user = basic_authentication(request)
    final = {}

    if not user:
        final['success'] = False
        final['msg'] = "Please provide valid credentials!! NOTE:- Api works on Basic authentication"
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    if request.body is None:
        final['success'] = False
        final['msg'] = "request cannot be completed as no desired body found!!"
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    
    try:
        like_or_unlike = json.loads(request.body)['like_or_unlike']
    except Exception as e:
        final['success'] = False
        final['msg'] = str(e)
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    try:
        up = UserPost.objects.get(id = post_id)
    except UserPost.DoesNotExist:
        final['success'] = False
        final['msg'] = "Post with id %s not found"%post_id
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)
    try:
        obj , created = LikeUnlike.objects.get_or_create(post=up , user=user)
        obj.like_unlike = like_or_unlike
        obj.save()
        final['success'] = True
        final['msg'] = "Sucessfully saved!"
        return HttpResponse(json.dumps(final) , content_type = 'application/json' ,status = 200)
    except Exception as e:
        final['success'] = False
        final['msg'] = str(e)
        return HttpResponse(json.dumps(final) , content_type = "application/json" , status = 400)




