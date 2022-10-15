# It is function. it take request as an argument and it will return dictionary of data as context


from .models import *


def menu_links(request):
    links = Categories.objects.all()
    return dict(links=links)