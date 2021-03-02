import re
from django import template
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import loader
from django.utils import timezone
from django.urls import reverse
# from django.contrib.gis.geoip2 import GeoIP2
# from ipware.ip import get_ip
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from .models import Feed
from .models import Message

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


def feed(request, feed_secret):
    # defaults
    default_location = settings_value('MAP_CONFIG')['DEFAULT_LOCATION']
    feed_lat = default_location[0]
    feed_lng = default_location[1]
    feed_location_scale = settings_value('MAP_CONFIG')['DEFAULT_ZOOM']
    feed_title = 'new feed'
    latest_messages = None

    try:
        # private view
        feed_object = Feed.objects.get(feed_secret=feed_secret)
        feed_title = feed_object.title
        feed_lat = feed_object.latitude
        feed_lng = feed_object.longitude
        feed_location_scale = feed_object.location_scale
        latest_messages = feed_object.messages.order_by('-id')[:5]
        messages_number = len(latest_messages)
    except ObjectDoesNotExist:
        messages_number = 0

    # TODO get user ip
    user_ip = None
    have_ip = False

    feed_template = loader.get_template('feed.html')
    context = {
        'latest_messages_list': latest_messages,
        'messages_number': messages_number,
        'feed_title': feed_title,
        'feed_secret': feed_secret,
        'feed_lat': feed_lat,
        'feed_lng': feed_lng,
        'feed_location_scale': feed_location_scale,
        'user_have_ip': have_ip,
        'user_ip': user_ip,
    }
    return HttpResponse(feed_template.render(context, request))


def feed_public(request, latitude, longitude):
    try:
        feed_lat, feed_lng = float(latitude), float(longitude)
        feed_object = Feed.objects.get(latitude=feed_lat,
                                       longitude=feed_lng)
        messages_number = -1
        feed_template = loader.get_template('feed.html')
        # TODO clean unnecessary parameters
        context = {
            'latest_messages_list': None,
            'messages_number': messages_number,
            'feed_title': feed_object.title,
            'feed_secret': None,
            'feed_lat': feed_object.latitude,
            'feed_lng': feed_object.longitude,
            'feed_location_scale': feed_object.location_scale,
            'user_have_ip': False,
            'user_ip': None,
        }
        return HttpResponse(feed_template.render(context, request))
    except ValueError:
        return HttpResponseNotFound('<h1>Coordinates format error.</h1>')
    except ObjectDoesNotExist:
        return HttpResponseNotFound('<h1>Feed not found. Create new feed.</h1>')


def post(request):
    feed_secret = request.POST["new_message_feed_secret"].strip('/')
    message_text = request.POST["new_message_text"]
    # text = re.sub('[^A-Za-z0-9!"#$%&\\\\\'*()+,-./:;=>?@[\]^_`{|}~ \n]+', '', text)
    # message_text = re.sub('[<]+', '', message_text)
    # feed_secret = re.sub('[^A-Za-z0-9.,]+', '', feed_secret)

    if feed_secret == '':
        return HttpResponseNotFound('<h1>Feed not found</h1>')

    if message_text != '':
        try:
            feed_obj = Feed.objects.get(feed_secret=feed_secret)
        except Feed.DoesNotExist as e:
            feed_title = request.POST["new_message_feed_title"]
            # feed_title = re.sub('[<]+', '', feed_title)
            if feed_title == '':
                return HttpResponseNotFound('<h1>Specify title</h1>')
            feed_lat = request.POST["new_message_feed_lat"]
            feed_lng = request.POST["new_message_feed_lng"]
            location_scale = request.POST["new_message_feed_scale"]
            # TODO add feed description
            try:
                feed_obj = Feed(feed_secret=feed_secret,
                                title=feed_title,
                                latitude=float(feed_lat),
                                longitude=float(feed_lng),
                                location_scale=int(location_scale))
                feed_obj.save()
            except ValueError:
                return HttpResponseNotFound('<h1>Wrong format</h1>')
            except IntegrityError:
                return HttpResponseNotFound('<h1>Location is occupied</h1>')
        nm = Message(
            feed=feed_obj,
            author_ip="192.168.1.1",  # TODO
            publication_date=timezone.now().timestamp(),
            text=message_text,
        )
        nm.save()

    return HttpResponseRedirect(reverse('feed:feed', args=(feed_secret,)))


def index(request):
    latest_feeds = Feed.objects.all()
    index_template = loader.get_template('index.html')
    context = {
        'latest_feeds_list': latest_feeds,
        'default_location': settings_value('MAP_CONFIG')['DEFAULT_LOCATION'],
        'default_location_scale': settings_value('MAP_CONFIG')['DEFAULT_ZOOM'],
    }
    return HttpResponse(index_template.render(context, request))


def vue_app(request):
    app_template = loader.get_template('vue.html')
    context = {
        'default_location': settings_value('MAP_CONFIG')['DEFAULT_LOCATION'],
        'default_location_scale': settings_value('MAP_CONFIG')['DEFAULT_ZOOM'],
        'locale': settings_value('LANGUAGE_CODE').replace('-', '_'),
    }
    return HttpResponse(app_template.render(context, request))
