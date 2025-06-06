from django.db import models


class OneModel(models.Model):

    testOne = models.CharField(max_length=30)

    class Meta:
        db_table = "one_model"


class TwoModel(models.Model):

    testTwo = models.CharField(max_length=30)
    testFor = models.ForeignKey(OneModel, related_name='two', on_delete=models.CASCADE)

    class Meta:
        db_table = "two_model"


class ThreeModel(models.Model):

    testThree = models.CharField(max_length=30)
    testMany = models.ManyToManyField(OneModel, related_name='three', blank=True, null=True)

    class Meta:
        db_table = "three_model"
