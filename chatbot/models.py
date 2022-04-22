from django.db import models
from django.urls import reverse, reverse_lazy

def _(x):
    return x

# Create your models here.
class Search(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField( blank=True, null=True)
    people = models.IntegerField( blank=True, null=True)
    child_in_group = models.BooleanField(null=True, blank=True)
    elder_in_group = models.BooleanField(null=True, blank=True)
    startdate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    enddate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    state = models.CharField(max_length=150, blank=True, null=True)
    current_city = models.CharField(max_length=150, blank=True, null=True)
    
    
    

    class Meta:
        verbose_name = _("Search")
        verbose_name_plural = _("Searchs")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Search_detail", kwargs={"pk": self.pk})
