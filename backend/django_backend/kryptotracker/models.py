from django.db import models
from django.contrib.auth.models import User


class PortfolioType(models.Model):
    type = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.type


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio_type = models.ForeignKey(PortfolioType, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=50, null=False)
    balance = models.FloatField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name
