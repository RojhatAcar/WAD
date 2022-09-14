from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from io import BytesIO
import os
from PIL import Image
import uuid


## Private Method - Rename the UserProfile profile picture on creation ##
# Taken from https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
def rename_profile_picture(instance, filename):
    upload_to="profile_images"
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)


## Signal - Every time a new User is created, a corresponding UserProfile is created ##
@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:     
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    profile_picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            if not self.make_thumbnail():
                raise Exception('Could not create thumbnail - is the file type valid?')
        super(UserProfile, self).save(*args, **kwargs)
    
    ## Private Method - Scales down and crops the profile picture on upload ##
    # Taken from https://stackoverflow.com/questions/23922289/django-pil-save-thumbnail-version-right-when-image-is-uploaded
    def make_thumbnail(self):
        image = Image.open(self.profile_picture)
        width, height = image.size
        if width > height:
            new_width = height
            new_height = height
        else:
            new_width = width
            new_height = width
        # Crop the image to a centered square
        image = image.crop(box=((width - new_width)//2, (height - new_height)//2, (width + new_width)//2, (height + new_height)//2))
        image.thumbnail((480,480), Image.ANTIALIAS)
        thumb_name, thumb_extension = os.path.splitext(self.profile_picture.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = thumb_name + '_thumb' + thumb_extension
        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type
        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)
        # set save=False, otherwise it will run in an infinite loop
        self.profile_picture.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True
    
    def __str__(self):
        return f'{self.user.username}'


## Returns the hex representation of a uuid4 ##
def uuid4_hex():
    return uuid.uuid4().hex

## Private Method - Renames The image on upload ##
# Taken from https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
def rename_image(instance, filename):
    upload_to = "user_uploads"
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)

## Private Method - Renames The thumbnail on upload ##
# Taken from https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
def rename_thumbnail(instance, filename):
    upload_to="user_uploads_thumbnails"
    ext = filename.split('.')[-1]
    filename = '{}-thumb.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)

class Picture(models.Model):
    uploading_user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    picture_id = models.UUIDField(primary_key=True, default=uuid4_hex, editable=False)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to=rename_image)
    thumbnail = models.ImageField(upload_to=rename_thumbnail, blank=True, null=True, default=None, editable=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=None)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.likes < 0:
            self.likes = 0
        if self.views < 0:
            self.views = 0
        if self.latitude:
            if self.latitude < -90:
                self.latitude = -90
            if self.latitude > 90:
                self.latitude = 90
        if self.longitude:
            if self.longitude < -180:
                self.longitude = -180
            if self.longitude > 180:
                self.longitude = 180
        if not self.thumbnail:
            if self.image and not self.make_thumbnail():
                raise Exception('Could not create thumbnail - is the file type valid?')
        super(Picture, self).save(*args, **kwargs)
    
    ## Private Method - Creates the thumbnail from the uploaded image and adds padding to make it square ##
    # Taken from https://stackoverflow.com/questions/23922289/django-pil-save-thumbnail-version-right-when-image-is-uploaded
    def make_thumbnail(self):
        unpadded_image = Image.open(self.image)
        unpadded_image = unpadded_image.copy()
        unpadded_image.thumbnail((480,480), Image.ANTIALIAS)
        width, height = unpadded_image.size
        image = Image.new("RGB", (480, 480))
        image.paste(unpadded_image, box=((480-width)//2, (480-height)//2, (480-width)//2 + width, (480-height)//2 + height))
        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = thumb_name + '_thumb' + thumb_extension
        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type
        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)
        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True
    
    
    def __str__(self):
        return str(self.uploading_user.user.username) + " - " + str(self.title)

 

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ForeignKey('Picture', on_delete=models.CASCADE)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    
    def __str__(self):
        return str(self.id) + " - " + str(self.text)



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)

