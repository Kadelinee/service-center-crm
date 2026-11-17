# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'


class Clients(models.Model):
    client_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clients'


class OrderServices(models.Model):
    order_service_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    service = models.ForeignKey('Services', models.DO_NOTHING)
    quantity = models.IntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'order_services'
        unique_together = (('order', 'service'),)


class OrderStatusHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    changed_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='changed_by', blank=True, null=True)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status_history'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Clients, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'orders'


class Services(models.Model):
    service_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Categories, models.DO_NOTHING)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'services'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
