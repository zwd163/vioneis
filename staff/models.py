from django.db import models

class ListModel(models.Model):
    staff_name = models.CharField(max_length=255, unique=True, verbose_name="Staff Name/Username") # Make username unique
    # TODO: Consider making staff_name unique=True if it serves as the username
    real_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Real Name") # Optional
    staff_type = models.CharField(max_length=255, verbose_name="Staff Type")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="Email") # Optional but unique
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number") # Optional for now
    # password field removed as it's not used for authentication
    openid = models.CharField(max_length=255, verbose_name="Openid", null=True, blank=True) # Keep for now, make optional
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")


    is_lock = models.BooleanField(default=False,verbose_name='Whether the lock')
    class Meta:
        db_table = 'staff'
        verbose_name = 'Staff'
        verbose_name_plural = "Staff"
        ordering = ['staff_name']

class TypeListModel(models.Model):
    staff_type = models.CharField(max_length=255, verbose_name="Staff Type")
    openid = models.CharField(max_length=255, verbose_name="Openid", null=True, blank=True) # Keep for now, make optional
    creater = models.CharField(max_length=255, verbose_name="Creater")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        db_table = 'stafftype'
        verbose_name = 'Staff Type'
        verbose_name_plural = "Staff Type"
        ordering = ['staff_type']
