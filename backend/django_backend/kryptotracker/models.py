# Author: Roberto Piazza
# Date: 25.03.2023

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class PortfolioType(models.Model):
    type = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.type


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    portfolio_type = models.ForeignKey(PortfolioType, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=50, null=False)
    balance = models.FloatField(default=0.0, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name


class AssetInfo(models.Model):
    history = HistoricalRecords()

    fullname = models.CharField(max_length=255, null=False)
    api_id_name = models.CharField(max_length=255, null=False)
    acronym = models.CharField(max_length=100, null=False)
    current_price = models.FloatField(default=0.0, null=True)
    image = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullname} Price at {self.updated_at}"


class AssetOwned(models.Model):
    history = HistoricalRecords()

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=False)
    asset = models.ForeignKey(AssetInfo, on_delete=models.CASCADE, null=False)
    quantity_owned = models.FloatField(default=0.0, null=False)
    quantity_price = models.FloatField(default=0.0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset.fullname


class Comment(models.Model):
    text = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)


class TransactionType(models.Model):
    type = models.CharField(max_length=50, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.type


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    asset = models.ForeignKey(AssetOwned, on_delete=models.CASCADE, null=False)
    tx_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, null=False)
    tx_comment = models.OneToOneField(Comment, on_delete=models.CASCADE, null=True, blank=True)
    tx_hash = models.CharField(max_length=255, null=True, blank=True)
    tx_sender_address = models.CharField(max_length=255, null=True, blank=True)
    tx_recipient_address = models.CharField(max_length=255, null=True, blank=True)
    tx_amount = models.FloatField(null=False)
    tx_value = models.FloatField(null=False)
    tx_fee = models.FloatField(default=0.0, null=True, blank=True)
    tx_date = models.DateTimeField(null=False)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)


class TaxReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    report_pdf = models.BinaryField(null=False)
    income_trading = models.FloatField(default=0.0, null=False)
    income_staking = models.FloatField(default=0.0, null=False)
    year = models.IntegerField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)


class ExchangeAPIs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    api_key = models.CharField(max_length=255, null=False)
    api_sec = models.CharField(max_length=255, null=True)
    exchange_name = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
