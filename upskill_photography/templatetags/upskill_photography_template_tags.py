from django import template
from upskill_photography.models import Picture

register = template.Library()

@register.inclusion_tag('upskill_photography/picture_thumbnail.html')
def get_picture_thumbnail(picture=None):
    return {'picture': picture}