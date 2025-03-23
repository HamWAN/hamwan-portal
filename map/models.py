# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models


CLIENT_TYPES = (
    ('CLIENT', 'Client'),
    ('UPLINK', 'Uplink'),
    ('SURVEY', 'Survey'),
)


class Site(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID') # Field name made lowercase.
    name = models.CharField(max_length=30L, db_column='NAME', blank=True) # Field name made lowercase.
    latitude = models.CharField(max_length=20L, db_column='LATITUDE', blank=True) # Field name made lowercase.
    longitude = models.CharField(max_length=20L, db_column='LONGITUDE', blank=True) # Field name made lowercase.
    status = models.CharField(max_length=20L, db_column='STATUS', blank=True) # Field name made lowercase.
    comment = models.CharField(max_length=255L, db_column='COMMENT', blank=True) # Field name made lowercase.
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'map_sites'

class Client(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID') # Field name made lowercase.
    site = models.ForeignKey(Site, null=True, db_column='SITE_ID', blank=True) # Field name made lowercase.
    name = models.CharField(max_length=30L, db_column='NAME', blank=True) # Field name made lowercase.
    latitude = models.CharField(max_length=20L, db_column='LATITUDE', blank=True) # Field name made lowercase.
    longitude = models.CharField(max_length=20L, db_column='LONGITUDE', blank=True) # Field name made lowercase.
    comment = models.CharField(max_length=255L, db_column='COMMENT', blank=True) # Field name made lowercase.
    strength_rrd = models.CharField(max_length=255L, db_column='STRENGTH_RRD', blank=True) # Field name made lowercase.
    strength_rrd_value = models.CharField(max_length=255L, db_column='STRENGTH_RRD_VALUE', blank=True) # Field name made lowercase.
    speed_rrd = models.CharField(max_length=255L, db_column='SPEED_RRD', blank=True) # Field name made lowercase.
    speed_rrd_value = models.CharField(max_length=255L, db_column='SPEED_RRD_VALUE', blank=True) # Field name made lowercase.
    type = models.CharField(max_length=255L, db_column='TYPE', blank=True, choices=CLIENT_TYPES) # Field name made lowercase.
    survey_data = models.CharField(max_length=255L, db_column='SURVEY_DATA', blank=True) # Field name made lowercase.
    public = models.BooleanField(db_column='PUBLIC') # Field name made lowercase.
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'map_clients'

class Link(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID') # Field name made lowercase.
    name = models.CharField(max_length=30L, db_column='NAME', blank=True) # Field name made lowercase.
    site1 = models.ForeignKey(Site, null=True, db_column='SITE1_ID', blank=True, related_name='links_out') # Field name made lowercase.
    site2 = models.ForeignKey(Site, null=True, db_column='SITE2_ID', blank=True, related_name='links_in') # Field name made lowercase.
    comment = models.CharField(max_length=255L, db_column='COMMENT', blank=True) # Field name made lowercase.
    strength_rrd = models.CharField(max_length=255L, db_column='STRENGTH_RRD', blank=True) # Field name made lowercase.
    strength_rrd_value = models.CharField(max_length=255L, db_column='STRENGTH_RRD_VALUE', blank=True) # Field name made lowercase.
    speed_rrd = models.CharField(max_length=255L, db_column='SPEED_RRD', blank=True) # Field name made lowercase.
    speed_rrd_value = models.CharField(max_length=255L, db_column='SPEED_RRD_VALUE', blank=True) # Field name made lowercase.
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'map_links'
