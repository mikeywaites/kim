from django.db import models


class MyModel(models.Model):
    name = models.CharField(max_length=255)


class User(models.Model):
    name = models.CharField(max_length=255)
    signup_date = models.DateTimeField(max_length=255, null=True)
    contact_details = models.ForeignKey('ContactDetail', null=True)


class ContactDetail(models.Model):
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.ForeignKey('Address')


class Address(models.Model):
    address_1 = models.CharField(max_length=255, null=True)
    address_2 = models.CharField(max_length=255, null=True)
    postcode = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=False)
