# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals
from django.contrib.auth.models import UserManager, AbstractBaseUser, BaseUserManager

from django.db import models


class Actor(models.Model):
    aid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Actor'


class Director(models.Model):
    did = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Director'


class Movie(models.Model):
    mid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)
    critic_rating = models.IntegerField(blank=True, null=True)
    audience_rating = models.IntegerField(blank=True, null=True)
    runtime = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie'


class MovieActor(models.Model):
    mid = models.ForeignKey(Movie, db_column='mid', primary_key=True)
    aid = models.ForeignKey(Actor, db_column='aid', primary_key=True)

    class Meta:
        managed = False
        db_table = 'Movie_Actor'
        unique_together = (('mid', 'aid'),)


class MovieDirector(models.Model):
    mid = models.ForeignKey(Movie, db_column='mid', primary_key=True)
    did = models.ForeignKey(Director, db_column='did', primary_key=True)

    class Meta:
        managed = False
        db_table = 'Movie_Director'
        unique_together = (('mid', 'did'),)


class RecRating(models.Model):
    uid = models.IntegerField(primary_key=True)
    mid = models.ForeignKey('Movie', db_column='mid')
    rating = models.FloatField()

    class Meta:
        managed = True
        db_table = 'RecRating'
        unique_together = (('uid', 'mid'),)

class UserRating(models.Model):
    uid = models.ForeignKey('AuthUser', db_column='id', primary_key=True)
    mid = models.ForeignKey('Movie', db_column='mid')
    rating = models.FloatField()

    class Meta:
        managed = True
        db_table = 'UserRating'
        unique_together = (('uid', 'mid'),)

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class Query(models.Model):
    qid = models.IntegerField(primary_key=True)
    uid = models.ForeignKey('AuthUser', db_column='id', primary_key=True)
    text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Query'
        unique_together = (('qid', 'uid'),)

class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
