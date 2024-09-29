import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    
    p = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    
    liked_posts = set()  

    if request.user.is_authenticated:
        currentUser = get_object_or_404(User, username=request.user.username)
        for post in posts:
            if currentUser.username in post.likeUser.split(','):
                liked_posts.add(post.id)
    else:
        currentUser = None
        
    return render(request, "network/index.html",{
        "page_obj": page_obj,
        "currentUser": currentUser,
        "liked_posts": liked_posts, 
        "posts": posts
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def newPost (request):
    if request.method == "POST":
        # Get content of body
        data = json.loads(request.body)
        body = data.get("body", "")
        
        # Save content to model
        post = Post(
            user = request.user,
            body=body,
        )
        post.save()
        
        return JsonResponse({"message": "Post made successfully."}, status=201)

def profileView(request, user):
    posts = Post.objects.filter(user__username = user).order_by("-timestamp").all()
    
    try:
        currentUser = get_object_or_404(User, username=request.user)
        # Get following list for current user
        followingList = currentUser.following.split(",")
    except:
        currentUser = "Guest"
        followingList = "None"
        
    p = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    user = get_object_or_404(User, username=user)
    
    return render(request, "network/profile.html",{
        "page_obj": page_obj,
        "Profileuser": user,
        "currentUser": currentUser,
        "followingList": followingList
    })

def followView(request, profileUsername, currentUsername):
    
    currentUser = get_object_or_404(User, username=currentUsername)
    
    # Check to see if user is already following someone
    if currentUser.following:
        followingList = currentUser.following.split(',')
    else:
        followingList = []
        
    # Follow / unfollow function
    if profileUsername in followingList:
        followingList.remove(profileUsername)  
    else: 
        followingList.append(profileUsername)
    
    currentUser.following = ','.join(followingList)
    currentUser.save()
    
    return HttpResponseRedirect(reverse("index"))

def followPage(request):
    currentUser = get_object_or_404(User, username=request.user.username)
    currentFollowing = currentUser.following
    
    #Put all followers post into a list 
    posts = []
    
    for f in currentFollowing:
        follow = Post.objects.filter(user__username = f)
        posts.extend(follow)
    
    # Sort all posts in descending order
    posts = sorted(posts, key=lambda post: post.timestamp, reverse=True)
    
    p = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    
    return render(request, "network/following.html",{
        "page_obj": page_obj
    })
    
@csrf_exempt
@login_required
def editView(request):
    if request.method == "POST":
        # Get data
        data = json.loads(request.body)
        body = data.get("body", "")
        postID = data.get("postID", "")
        
        # Fetch the post
        currentPost = get_object_or_404(Post, id=postID)
        currentPost.body = body
        currentPost.edited = True
        currentPost.save()

        return JsonResponse({"message": "Edit made successfully."}, status=201)
    
@csrf_exempt
@login_required
def like(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        postID = data.get("postID", "")

        currentPost = get_object_or_404(Post, id=postID)
        user = request.user.username

        if currentPost.likeUser:
            likeList = currentPost.likeUser.split(',')
        else:
            likeList = []

        if user in likeList:
            likeList.remove(user)
            if currentPost.likeCount > 0:
                currentPost.likeCount -= 1
            text = "Like"
        else:
            likeList.append(user)
            currentPost.likeCount += 1
            text = "Unlike"

        currentPost.likeUser = ','.join(likeList)
        currentPost.save()
    
    return JsonResponse({"likeCount": currentPost.likeCount, "text": text}, status=201)