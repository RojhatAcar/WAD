from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from upskill_photography.models import Category, Comment, Picture, User, UserProfile
from uuid import uuid4

def uuid4_hex():
    return uuid4().hex

def add_UserProfile(name=None, pw=None):
    if name:
        username = name
    else:
        username = uuid4_hex()
    if pw:
        password = pw
    else:
        password = uuid4_hex()
    user = User(username=username)
    user.set_password(password)
    user.save()
    return UserProfile.objects.get(user=user)

def add_Category(name=None):
    if name:
        category_name = name
    else:
        category_name = uuid4_hex()
    category = Category(name=category_name)
    category.save()
    return category

def add_Picture(title=None, uploading_user=None, category=None, lng=None, lat=None, views=0, likes=0):
    small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
    if title:
        image_title = title
    else:
        image_title = uuid4_hex()
    if uploading_user:
        user_profile = uploading_user
    else:
        user_profile = add_UserProfile()
    if category:
        image_category = category
    else:
        image_category = add_Category()
    image = SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')
    picture = Picture(title=image_title, longitude=lng, latitude=lat, views=views, likes=likes)
    picture.uploading_user = user_profile
    picture.image = image
    picture.category = image_category
    picture.save()
    return picture

def add_Comment(picture=None, user_profile=None, text=""):
    if picture:
        comment_picture = picture
    else:
        comment_picture = add_Picture()
    if user_profile:
        user = user_profile
    else:
        user = add_UserProfile
    comment = Comment(picture=comment_picture, user=user, text=text)
    comment.save()
    return comment


class CategoryMethodTests(TestCase):
    def test_slug_line_creation(self):
        """
        Checks to make sure that when a category is created, an
        appropriate slug is created.
        Example: "Random Category String" should be "random-category-string".
        """
        category = Category(name='Random Category String')
        category.save()
        self.assertEqual(category.slug, 'random-category-string')


class PictureMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        Ensures the number of views received for a Picture are non-negative.
        """
        picture = add_Picture(views=-1)
        self.assertEqual((picture.views >= 0), True)
    
    def test_ensure_likes_are_positive(self):
        """
        Ensures the number of likes received for a Picture are non-negative.
        """
        picture = add_Picture(likes=-1)
        self.assertEqual((picture.likes >= 0), True)
    
    def test_ensure_latitude_not_too_negative(self):
        """
        Ensures that the latitude can't be smaller than -90
        """
        picture = add_Picture(lat=-91)
        self.assertEqual((picture.latitude >= -90 and picture.latitude <= 90), True)
    
    def test_ensure_latitude_not_too_positive(self):
        """
        Ensures that the latitude can't be larger than 90
        """
        picture = add_Picture(lat=91)
        self.assertEqual((picture.latitude >= -90 and picture.latitude <= 90), True)
    
    def test_ensure_longitude_not_too_negative(self):
        """
        Ensures that the longitude can't be smaller than -180
        """
        picture = add_Picture(lng=-181)
        self.assertEqual((picture.longitude >= -180 and picture.longitude <= 180), True)
    
    def test_ensure_longitude_not_too_positive(self):
        """
        Ensures that the longitude can't be larger than 180
        """
        picture = add_Picture(lng=181)
        self.assertEqual((picture.longitude >= -180 and picture.longitude <= 180), True)


class IndexViewTests(TestCase):
    def test_index_view_with_no_pictures(self):
        """
        Ensures that the index view can handle having no picture to display
        """
        response = self.client.get(reverse('upskill_photography:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OOPS')
    
    def test_index_view_with_one_picture(self):
        """
        Ensures that the index view can display a single picture if that is the only
        picture in the database.
        """
        picture_1 = add_Picture()
        response = self.client.get(reverse('upskill_photography:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['first_picture']), str(picture_1))
    
    def test_index_view_with_two_pictures(self):
        """
        Ensures that the index view works when there are only two pictures in the databse.
        """
        picture_1 = add_Picture()
        picture_2 = add_Picture()
        response = self.client.get(reverse('upskill_photography:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['first_picture']), str(picture_1))
        self.assertEqual(len(response.context['pictures']), 1)
        self.assertEqual(str(response.context['pictures'][0]), str(picture_2))


class DiscoveryViewTests(TestCase):
    def test_ensure_discovery_view_default_sort_newest(self):
        """
        Ensures that the pictures are displayed by newest in descending order.
        """
        picture_1 = add_Picture()
        picture_2 = add_Picture()
        response = self.client.get(reverse('upskill_photography:discovery'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pictures']), 2)
        self.assertEqual(str(response.context['pictures'][0]), str(picture_2))

    def test_ensure_alternative_sort_styles_work(self):
        """
        Ensures that alternative ways to sort the pictures work as well.
        """
        picture_1 = add_Picture(likes=99)
        picture_2 = add_Picture()
        response = self.client.get(reverse('upskill_photography:discovery') + "?sort=likes_desc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pictures']), 2)
        self.assertEqual(str(response.context['pictures'][0]), str(picture_1))


class SearchViewTests(TestCase):
    def test_ensure_search_function_yields_results(self):
        """
        Ensures that the search function actually does some decent filtering.
        """
        picture_1 = add_Picture(title="Strawberry")
        picture_2 = add_Picture(title="Sail Boat")
        picture_3 = add_Picture(title="Lovely Portrait")
        response = self.client.get(reverse('upskill_photography:search_result') + "?query=boat")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)
        self.assertEqual(str(response.context['results'][0]), str(picture_2))


class UserProfileViewTests(TestCase):
    def test_ensure_only_pictures_of_user(self):
        """
        Ensures that all pictures of the user are displayed and not any other.
        """
        user_profile = add_UserProfile()
        picture_1 = add_Picture()
        picture_2 = add_Picture(uploading_user=user_profile)
        picture_3 = add_Picture(uploading_user=user_profile)
        picture_4 = add_Picture()
        picture_5 = add_Picture(uploading_user=user_profile)
        user_pictures = [str(picture_5), str(picture_3), str(picture_2)]
        response = self.client.get(reverse('upskill_photography:userprofile', kwargs={'userprofile_username': user_profile.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pictures']), 3)
        self.assertEqual(str(response.context['pictures'][0]) in user_pictures, True)
        self.assertEqual(str(response.context['pictures'][1]) in user_pictures, True)
        self.assertEqual(str(response.context['pictures'][2]) in user_pictures, True)



class AccountViewTests(TestCase):
    def test_ensure_account_can_not_be_viewed_when_not_logged_in(self):
        user_profile = add_UserProfile(name='Test')
        response = self.client.get(reverse('upskill_photography:account'))
        self.assertEqual(response.status_code, 302)
    
    def test_ensure_account_can_be_viewed_when_logged_in(self):
        user_profile = add_UserProfile(name='test_user', pw='12345')
        login = self.client.login(username='test_user', password='12345')
        response = self.client.get(reverse('upskill_photography:account'))
        self.assertEqual(response.status_code, 200)
