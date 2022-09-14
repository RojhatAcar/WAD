from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from PIL import Image
from upskill_photography.forms import PictureUploadForm, ProfilePictureForm
from upskill_photography.models import Category, Comment, Picture, User, UserProfile
from urllib.parse import urlencode, urlparse, parse_qs

## Private Method - Adds all current category objects to the given context dictionary ##
def get_categories(context_dict):
    try:
        context_dict['categories'] = list(Category.objects.all())
    except:
        pass


## Private Method - Retreives the query string from a GET request ##
def get_query_parameters(request):
    query_dict = {}
    if request.method == "GET":
        url_params = parse_qs(urlparse(request.build_absolute_uri()).query)
        for param in url_params:
            query_dict[param] = url_params[param][0]
    return query_dict


## Private Method - Orders a set of pictures in the given style and order ##
def picture_ordering(pictures, sort_style, sort_order):
    def upload_time(picture):
        return picture.timestamp
    def views(picture):
        return picture.views
    def likes(picture):
        return picture.likes
    def comments(picture):
        return len(Comment.objects.filter(picture=picture))

    pictures = list(pictures)
    reverse = True
    if sort_order == "asc":
        reverse = False
    func = upload_time
    if sort_style == "views":
        func = views
    elif sort_style == "likes":
        func = likes
    elif sort_style == "comments":
        func = comments
    pictures.sort(reverse=reverse, key=func)
    return pictures


def index(request):
    context_dict = {}
    get_categories(context_dict)
    try:
        # Retrieve the 10 most liked pictures to be displayed in the carousel.
        # There is a difference between the first picture and the others,
        # since the first picture needs to be selected to be displayed at the start.
        context_dict['first_picture'] = list(Picture.objects.order_by('-likes'))[0]
        context_dict['pictures'] = list(Picture.objects.order_by('-likes'))[1:10]
        context_dict['counter'] = list(range(1, len(context_dict['pictures']) + 1))
    except:
        pass
    return render(request, 'upskill_photography/index.html', context=context_dict)


def about(request):
    context_dict = {}
    get_categories(context_dict)
    return render(request, 'upskill_photography/about.html', context=context_dict)


def contact(request):
    context_dict = {}
    get_categories(context_dict)
    return render(request, 'upskill_photography/contact.html', context=context_dict)


def faq(request):
    context_dict = {}
    get_categories(context_dict)
    return render(request, 'upskill_photography/faq.html', context=context_dict)


def discovery(request):
    context_dict = {}
    if request.method == "POST":
        query_string = {}
        # Retrieve the sort style and order to pass as a query string
        # in the GET request to the same page
        sort_style = request.POST.get('sort_style', "")
        sort_order = request.POST.get('sort_order', "")
        if sort_style != "" and sort_order != "":
            query_string['sort'] = sort_style + "_" + sort_order
        if len(query_string) > 0:
            encoded_query_string = urlencode(query_string)
            return redirect(reverse('upskill_photography:discovery') + f"?{encoded_query_string}")
        else:
            return redirect(reverse('upskill_photography:discovery'))
    else:
        get_categories(context_dict)
        query_dict = get_query_parameters(request)
        # Order the pictures by newest by default
        pictures = Picture.objects.order_by('-timestamp')
        if pictures and 'sort' in query_dict:
            # If a different sort order is specified, re-order the pictures
            sort_style, sort_order = query_dict['sort'].split('_')
            pictures = picture_ordering(pictures, sort_style, sort_order)
            context_dict['sort_style'] = sort_style
            context_dict['sort_order'] = sort_order
        else:
            context_dict['sort_style'] = "new"
            context_dict['sort_order'] = "desc"

        context_dict['pictures'] = pictures
        return render(request, 'upskill_photography/discovery.html', context=context_dict)


def categories(request):
    context_dict = {}
    get_categories(context_dict)
    pictures = []
    for category in context_dict['categories']:
        # Get the Most liked picture of each category to be used as thumbnails
        pictures = pictures + list(Picture.objects.filter(category=Category.objects.get(name=category.name)).order_by('-likes'))[0:1]
    context_dict['pictures'] = pictures
    return render(request, 'upskill_photography/categories.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    if request.method == "POST":
        query_string = {}
        # Retrieve the sort style and order to pass as a query string
        # in the GET request to the same page
        sort_style = request.POST.get('sort_style', "")
        sort_order = request.POST.get('sort_order', "")
        if sort_style != "" and sort_order != "":
            query_string['sort'] = sort_style + "_" + sort_order
        if len(query_string) > 0:
            encoded_query_string = urlencode(query_string)
            return redirect(reverse('upskill_photography:show_category', kwargs={'category_name_slug': category_name_slug}) + f"?{encoded_query_string}")
        else:
            return redirect(reverse('upskill_photography:show_category', kwargs={'category_name_slug': category_name_slug}))
    else:
        get_categories(context_dict)
        query_dict = get_query_parameters(request)
        pictures = []
        try:
            # Attempt to get the category by its slug and retrieve all pictures of that category, newest first
            category = Category.objects.get(slug=category_name_slug)
            pictures = list(Picture.objects.filter(category=Category.objects.get(slug=category_name_slug)).order_by('-timestamp'))
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            pictures = None
        
        if pictures and 'sort' in query_dict:
            # If a different sort order is specified, re-order the pictures
            sort_style, sort_order = query_dict['sort'].split('_')
            pictures = picture_ordering(pictures, sort_style, sort_order)   
            context_dict['sort_style'] = sort_style
            context_dict['sort_order'] = sort_order
        else:
            context_dict['sort_style'] = "new"
            context_dict['sort_order'] = "desc"
        
        context_dict['pictures'] = pictures
        return render(request, 'upskill_photography/category.html', context=context_dict)


def search_result(request):
    context_dict = {}
    if request.method == "POST":
        query_string = {}
        # Retrieve the sort style and order to pass as a query string
        # in the GET request to the same page
        # Retrieve the search query and pass it to the query string
        query_text = request.POST.get('search_query', None)
        if query_text:
            query_string['query'] = query_text
        sort_style = request.POST.get('sort_style', "")
        sort_order = request.POST.get('sort_order', "")
        if sort_style != "" and sort_order != "":
            query_string['sort'] = sort_style + "_" + sort_order

        if len(query_string) > 0:
            encoded_query_string = urlencode(query_string)
            return redirect(reverse('upskill_photography:search_result') + f"?{encoded_query_string}")
        else:
            return redirect(reverse('upskill_photography:search_result'))
    else:
        get_categories(context_dict)
        query_dict = get_query_parameters(request)
        # Handle the search query passed in the query string
        query_text = ""
        if 'query' in query_dict:
            query_text = query_dict['query']
        results = search_function(query_text)

        context_dict['sort_style'] = "relevance"
        context_dict['sort_order'] = "relevance"
        if results and 'sort' in query_dict:
            # If a different sort order is specified, re-order the pictures
            sort_style, sort_order = query_dict['sort'].split('_')
            results = picture_ordering(results, sort_style, sort_order)
            context_dict['sort_style'] = sort_style
            context_dict['sort_order'] = sort_order

        context_dict['results'] = results
        context_dict['query'] = query_text
        return render(request, 'upskill_photography/search.html', context=context_dict)


## Private Method - Performs a basic search of the database through a search string ##
def search_function(query_text):
    results = []
    keywords = query_text.lower().split(' ')

    # Remove any unnecessary keywords from the keyword list
    obsolete_keywords = ['a', 'an', 'and', 'the', '&']
    for obsolete_keyword in obsolete_keywords:
        while obsolete_keyword in keywords:
            keywords.remove(obsolete_keyword)

    # First search for similarities with the whole query text
    results = results + list(Picture.objects.filter(title__icontains=query_text))

    # Then search for similarities with each keyword
    for keyword in keywords:
        results = results + list(Picture.objects.filter(title__icontains=keyword))

    if len(results) != 0:
        results = list(dict.fromkeys(results))  # To make the results unique
    else:
        results = None
    return results


def userprofile(request, userprofile_username):
    context_dict = {}
    if request.method == "POST":
        query_string = {}
        # Retrieve the sort style and order to pass as a query string
        # in the GET request to the same page
        sort_style = request.POST.get('sort_style', "")
        sort_order = request.POST.get('sort_order', "")
        if sort_style != "" and sort_order != "":
            query_string['sort'] = sort_style + "_" + sort_order
        if len(query_string) > 0:
            encoded_query_string = urlencode(query_string)
            return redirect(reverse('upskill_photography:userprofile', kwargs={'userprofile_username': userprofile_username}) + f"?{encoded_query_string}")
        else:
            return redirect(reverse('upskill_photography:userprofile', kwargs={'userprofile_username': userprofile_username}))
    else:
        get_categories(context_dict)
        query_dict = get_query_parameters(request)
        try:
            user = User.objects.get(username=userprofile_username)
            user_profile = UserProfile.objects.get(user=user)
            pictures = Picture.objects.filter(uploading_user=user_profile)
            if pictures and 'sort' in query_dict:
                # If a different sort order is specified, re-order the pictures
                sort_style, sort_order = query_dict['sort'].split('_')
                pictures = picture_ordering(pictures, sort_style, sort_order)   
                context_dict['sort_style'] = sort_style
                context_dict['sort_order'] = sort_order
            else:
                context_dict['sort_style'] = "new"
                context_dict['sort_order'] = "desc"
            context_dict['userprofile'] = user_profile
            context_dict['pictures'] = pictures
            views = 0
            likes = 0
            comments_received = 0
            # Count the likes, views, and comments of each picture uploaded by this user
            for picture in pictures:
                views = views + picture.views
                likes = likes + picture.likes
                for comment in Comment.objects.filter(picture=picture):
                    comments_received += 1
            context_dict['total_views'] = views
            context_dict['total_likes'] = likes
            context_dict['comments_received'] = comments_received
            comments_created = 0
            # Count the comments written by this user
            for comment in Comment.objects.filter(user=user_profile):
                comments_created += 1
            context_dict['comments_created'] = comments_created
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            pass
        return render(request, 'upskill_photography/user_profile.html', context=context_dict)


def picture_view(request, userprofile_username, picture_id):
    context_dict = {}
    get_categories(context_dict)
    if request.method == "POST":
        # Handle users posting comments on this picture
        # Create a new comment
        comment_username = request.POST.get('comment_username', None)
        comment_text = request.POST.get('comment_text', None)
        picture = None
        user = None
        try:
            picture = Picture.objects.get(picture_id=picture_id)
            user = UserProfile.objects.get(user=User.objects.get(username=comment_username))
        except Picture.DoesNotExist:
            pass
        except (UserProfile.DoesNotExist, User.DoesNotExist):
            pass
        if user and comment_text and picture:
            comment = Comment(picture=picture, user=user, text=comment_text)
            comment.save()
        return redirect(reverse('upskill_photography:picture_view', kwargs={'userprofile_username': userprofile_username, 'picture_id': picture_id}))
    else:
        try:
            picture = Picture.objects.get(picture_id=picture_id)
            comments = Comment.objects.filter(picture=picture).order_by('-timestamp')
            picture.views = picture.views + 1
            picture.save()
            more_pictures = list(Picture.objects.filter(uploading_user=picture.uploading_user).order_by('-likes'))[0:10]
            context_dict['picture'] = picture
            context_dict['comments'] = comments
            context_dict['more_pictures'] = more_pictures
        except Picture.DoesNotExist:
            context_dict['picture'] = None
        return render(request, 'upskill_photography/picture_view.html', context=context_dict)


@login_required
def account(request):
    context_dict = {}
    get_categories(context_dict)
    return render(request, 'upskill_photography/account.html', context=context_dict)


@login_required
def change_profile_picture(request):
    if request.method == "POST":
        # Change the profile picture ImageField
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.profile_picture = form.cleaned_data.get("profile_picture")
            user_profile.save()
        return redirect(reverse('upskill_photography:userprofile', kwargs={'userprofile_username': request.user.username}))
    else:            
        context_dict = {}
        get_categories(context_dict)
        context_dict['form'] = ProfilePictureForm()
        return render(request, 'upskill_photography/user_change_profile_picture.html', context=context_dict)


@login_required
def uploads(request):
    context_dict = {}
    get_categories(context_dict)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        context_dict['pictures'] = Picture.objects.filter(uploading_user=user_profile).order_by('-timestamp')
    except (UserProfile.DoesNotExist, Picture.DoesNotExist):
        pass
    return render(request, 'upskill_photography/uploads.html', context=context_dict)


@login_required
def upload(request):
    context_dict = {}
    if request.method == "POST":
        # Handle users uploading pictures
        # lng and lat coordinates are optional and can be left out
        form = PictureUploadForm(request.POST, request.FILES)
        if form.is_valid():
            allow_location = request.POST.get('use_location', None)
            uploading_user = UserProfile.objects.get(user=request.user)
            title = form.cleaned_data.get("title")
            image = form.cleaned_data.get("image")
            category = form.cleaned_data.get("category")
            lng = request.POST.get('longitude', None)
            lat = request.POST.get('latitude', None)
            if lng == "" or lat == "" or allow_location == None:
                lng = lat = None
            else:
                lng = float(lng)
                lat = float(lat)
            Picture.objects.create(uploading_user=uploading_user, title=title, image=image, category=category, longitude=lng, latitude=lat)
        return redirect(reverse('upskill_photography:discovery'))
    else:
        get_categories(context_dict)
        context_dict['form'] = PictureUploadForm()
        return render(request, 'upskill_photography/upload.html', context=context_dict)


# Handles AJAX requests for liking pictures
class LikePictureView(View):
    @method_decorator(login_required)
    def get(self, request):
        picture_id = request.GET['picture_id']
        picture = None
        try:
            picture = Picture.objects.get(picture_id=picture_id)
        except Picture.DoesNotExist:
            return HttpResponse(-1)
         
        picture.likes = picture.likes + 1
        picture.save()
        return HttpResponse(picture.likes)


# Handles AJAX requests for removing comments
class RemoveCommentView(View):
    @method_decorator(login_required)
    def get(self, request):
        comment_id = request.GET['comment_id']
        try:
            Comment.objects.get(id=comment_id).delete()
        except Comment.DoesNotExist:
            return HttpResponse(-1)
        return HttpResponse(0);


# Handles AJAX requests for removing pictures
class RemovePictureView(View):
    @method_decorator(login_required)
    def get(self, request):
        picture_id = request.GET['picture_id']
        try:
            Picture.objects.get(picture_id=picture_id).delete()
        except Picture.DoesNotExist:
            return HttpResponse(-1)
        return HttpResponse(0);