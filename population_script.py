import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WAD_Team4D.settings')

import django
django.setup()

from upskill_photography.models import Picture, Category, User, UserProfile, Comment
import shutil
import uuid
from PIL import Image, ImageChops
from pathlib import Path

"""
Since it is difficult to find duplicates of Pictures and Comments in the current model,
it is advised to use the population script only once when the database is empty.
Otherwise, copies of Pictures and Comments can occur several times.
"""
def populate():
    if not os.path.exists('media'):
        os.makedirs('media')
    if not os.path.exists('media/user_uploads'):
        os.makedirs('media/user_uploads')

    pictures = [
        {'image_file_name' : 'bee.jpg',
            'uploading_user': add_UserProfile("James"),
            'category': add_cat("Nature"),
            'title': 'Buzzing Bee',
            'views': 10,
            'likes': 2,
            'lat': 48.79835820197272,
            'lng': 9.205502344760113,
            'comments': [
                            {'user': add_UserProfile("Oliver"),
                            'text': "Impressive that you could get a picture so close to the Bee!",
                            },
                            {'user': add_UserProfile("Annie"),
                            'text': "That's a really sweet Bee.",
                            },
                            ],
            },
        {'image_file_name' : 'blurry_lights.jpg',
            'uploading_user': add_UserProfile("Oliver"),
            'category': add_cat("Architecture"),
            'title': 'Night Lights Without Glasses',
            'views': 15,
            'likes': 4,
            'lat': None,
            'lng': None,
            'comments': [
                            {'user': add_UserProfile("Rojhat"),
                            'text': "A really nice effect. You could have used a diffuser though I think.",
                            },
                            ],
            },
        {'image_file_name' : 'ferris_wheel.jpg',
            'uploading_user': add_UserProfile("Rojhat"),
            'category': add_cat("Architecture"),
            'title': 'Now that is a festival',
            'views': 20,
            'likes': 1,
            'lat': None,
            'lng': None,
            },
        {'image_file_name' : 'lizard.jpg',
            'uploading_user': add_UserProfile("Annie"),
            'category': add_cat("Nature"),
            'title': 'Sunbathing',
            'views': 15,
            'likes': 10,
            'lat': None,
            'lng': None,
            },
        {'image_file_name' : 'milkshake.jpg',
            'uploading_user': add_UserProfile("James"),
            'category': add_cat("Misc"),
            'title': 'Sweet',
            'views': 10,
            'likes': 2,
            'lat': None,
            'lng': None,
            'comments': [
                            {'user': add_UserProfile("Oliver"),
                            'text': "The portrait format definitely makes this picture unique. It's like the milkshake is put on a pedestal.",
                            },
                            {'user': add_UserProfile("Rojhat"),
                            'text': "I find the colours a bit over-saturated. Besides that through you have a really nice composition.",
                            },
                            ],
            },
        {'image_file_name' : 'miniature_trains.jpg',
            'uploading_user': add_UserProfile("Oliver"),
            'category': add_cat("Miniature"),
            'title': 'Choo Choo Mini Trains',
            'views': 5,
            'likes': 2,
            'lat': None,
            'lng': None,
            },
        {'image_file_name' : 'moon.jpg',
            'uploading_user': add_UserProfile("Rojhat"),
            'category': add_cat("Astronomy"),
            'title': 'The Big White Disk',
            'views': 11,
            'likes': 6,
            'lat': None,
            'lng': None,
            'comments': [
                            {'user': add_UserProfile("Oliver"),
                            'text': "What lens did you use for this picture? I always struggle with the resolution of my images.",
                            },
                            {'user': add_UserProfile("James"),
                            'text': "The negative space gives this image a really ominous feeling.",
                            },
                            {'user': add_UserProfile("Annie"),
                            'text': "A good picture. It would have come out better if you could also see the surrounding stars through.",
                            },
                            ],
            },
        {'image_file_name' : 'park_pond.jpg',
            'uploading_user': add_UserProfile("Annie"),
            'category': add_cat("Nature"),
            'title': 'Autumn Times',
            'views': 25,
            'likes': 7,
            'lat': 48.80599162294229,
            'lng': 9.172123589667487,
            },
        {'image_file_name' : 'porsche.jpg',
            'uploading_user': add_UserProfile("James"),
            'category': add_cat("Cars"),
            'title': 'Speedy Boi',
            'views': 14,
            'likes': 4,
            'lat': 48.83432337355542,
            'lng': 9.152500854741813,
            },
        {'image_file_name' : 'racecar.jpg',
            'uploading_user': add_UserProfile("Oliver"),
            'category': add_cat("Cars"),
            'title': 'Super Speedy Boi',
            'views': 13,
            'likes': 2,
            'lat': 48.83432337355542,
            'lng': 9.152500854741813,
            'comments': [
                            {'user': add_UserProfile("Oliver"),
                            'text': "A very fast looking racecar",
                            },
                            {'user': add_UserProfile("Annie"),
                            'text': "Interesting choice of lighting - it looks a bit menacing",
                            },
                            ],
            },
        {'image_file_name' : 'spring_flowers.jpg',
            'uploading_user': add_UserProfile("Rojhat"),
            'category': add_cat("Nature"),
            'title': 'Spring Flowers',
            'views': 23,
            'likes': 13,
            'lat': None,
            'lng': None,
            },
        {'image_file_name' : 'swans.jpg',
            'uploading_user': add_UserProfile("Annie"),
            'category': add_cat("Nature"),
            'title': 'Young and Old',
            'views': 16,
            'likes': 10,
            'lat': None,
            'lng': None,
            },
        {'image_file_name' : 'violet_flowers.jpg',
            'uploading_user': add_UserProfile("James"),
            'category': add_cat("Nature"),
            'title': 'Violets?',
            'views': 8,
            'likes': 3,
            'lat': 48.79835820197272,
            'lng': 9.205502344760113,
            },
            ]
        
    for picture in pictures:
        file = picture['image_file_name']
        ext = file.split('.')[-1]
        new_name = uuid.uuid4().hex + "." +  ext
        shutil.copy("population_script_files/" + file, "media/user_uploads")
        os.rename("media/user_uploads/" + file, "media/user_uploads/" + new_name)
        user = picture['uploading_user']
        cat = picture['category']
        title = picture['title']
        views = picture['views']
        likes = picture['likes']
        lat = picture['lat']
        lng = picture['lng']
        image = add_picture(cat, title, "user_uploads/" + new_name, user, views=views, likes=likes, lat=lat, lng=lng)
        for comment in picture.get('comments', []):
            add_comment(image, comment['user'], comment['text'])


def add_UserProfile(name):
    user, created = User.objects.get_or_create(username=name)
    user.save()
    user_profile = UserProfile.objects.get(user=user)
    if created:
        print(f"User: {user_profile}")
    return user_profile


def add_cat(name):
    cat, created = Category.objects.get_or_create(name=name)
    cat.name = name
    cat.save()
    if created:
        print(f"Category: {cat}")
    return cat


def add_picture(cat, title, image, uploading_user, views=0, likes=0, lat=None, lng=None):
    already_exists = False
    duplicate_picture = None
    this_im_path = Path("media/" + image).absolute()
    this_im = Image.open(this_im_path)
    this_width, this_height = this_im.size
    this_im.thumbnail((512,512), Image.ANTIALIAS)
    parent_path = Path(this_im_path).parent.absolute()
    cwd = os.getcwd()
    for picture_object in Picture.objects.filter(uploading_user=uploading_user):
        comp_im = Image.open(Path(cwd + picture_object.image.url).absolute())
        comp_width, comp_height = comp_im.size
        if this_width == comp_width and this_height == comp_height:
            comp_im.thumbnail((512,512), Image.ANTIALIAS)
            pixels = list(ImageChops.difference(this_im, comp_im).getdata())
            diff = 0
            for tup in pixels:
                diff += sum(tup)
            if diff == 0:
                already_exists = True
                duplicate_picture = picture_object
            break
    if not already_exists:
        p, created = Picture.objects.get_or_create(uploading_user=uploading_user, title=title, image=image, category=cat)
        p.views = views
        p.likes = likes
        p.latitude = lat
        p.longitude = lng
        p.save()
        if created:
            print(f"Picture: {p}")
    else:
        p = duplicate_picture
    return p

def add_comment(picture, user, text):
    c, created = Comment.objects.get_or_create(picture=picture, user=user, text=text)
    c.save()
    if created:
        print(f"Comment: {c}")
    return c


if __name__ == '__main__':
    print('Starting upskillphotography population script...')
    populate()
