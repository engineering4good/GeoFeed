from __future__ import unicode_literals

from django.db import models


class Feed(models.Model):
    """Feed containing Messages"""
    feed_secret = models.CharField(max_length=64, default='', primary_key=True)
    title = models.CharField(default='', max_length=64)
    description = models.CharField(default='', max_length=1024)
    # TODO change default
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    location_scale = models.IntegerField(default=16)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['latitude', 'longitude'], name='unique_location')
        ]
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.title

    def __unicode__(self):
        return u'Feed title: %s' % self.title


class Message(models.Model):
    """single Message"""
    feed = models.ForeignKey(Feed, related_name='messages', on_delete=models.CASCADE)
    author_ip = models.GenericIPAddressField(default="unknown")
    publication_date = models.FloatField(default=0)
    text = models.CharField(default="", max_length=1024)

    def __str__(self):
        return self.text

    def __unicode__(self):
        return u'Message text: %s' % self.text
