from ..model.test import *
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=OneModel)
def create_one_two(sender, instance, created, **kwargs):
    print(f"sender:{sender}, instance:{instance}, created:{created}")


@receiver(post_save, sender=ThreeModel)
def create_one_two(sender, instance, created, **kwargs):
    print(f"sender:{sender}, instance:{instance}, created:{created}")