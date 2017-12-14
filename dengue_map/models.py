from django.db import models


class BaseTable(models.Model):
    """
    Base abstract table to be inherited by all other tables
    """
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Model(BaseTable):
    """
    Defines the structure of the model table
    """
    # the columns for the tables
    model_name = models.CharField(max_length=100)

    class Meta:
        db_table = '__models'

    def publish(self):
        self.save()


class Provinces(BaseTable):
    # define the dictionary structure
    name1 = models.CharField(max_length=100)
    name2 = models.CharField(max_length=100)
    varname = models.CharField(max_length=100)
    engtype = models.CharField(max_length=100)
    prov_id = models.IntegerField(unique=True)
    provtype = models.CharField(max_length=50)
    isocode = models.CharField(max_length=20)
    geometry = models.TextField()

    class Meta:
        db_table = 'provinces'

    def publish(self):
        self.save()

    def get_id(self):
        return self.id
