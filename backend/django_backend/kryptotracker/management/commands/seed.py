from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from kryptotracker.models import PortfolioType, Portfolio, Asset, Comment, TransactionType, Transaction
import random

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Erstellen Sie Dummy-User
        user = User.objects.create(username='Testuser', password='Test123', email='test@test.de')

        # Erstellen Sie PortfolioTypen
        portfolio_type_staking = PortfolioType.objects.create(type='Staking')
        portfolio_type_hodl = PortfolioType.objects.create(type='Spot')

        # Erstellen Sie Portfolios
        portfolio = Portfolio.objects.create(
            user=user,
            portfolio_type=portfolio_type_staking,
            name='Portfolio1',
            balance=random.uniform(1000.0, 5000.0)
        )

        portfolio2 = Portfolio.objects.create(
            user=user,
            portfolio_type=portfolio_type_hodl,
            name='Portfolio2',
            balance=random.uniform(1000.0, 5000.0)
        )

        # Erstellen Sie Assets
        asset1 = Asset.objects.create(
            portfolio=portfolio,
            fullname='Bitcoin',
            acronym='BTC',
            current_price=random.uniform(10.0, 100.0),
            mean_price=random.uniform(10.0, 100.0),
            win_loss=random.uniform(-10.0, 10.0)
        )

        asset2 = Asset.objects.create(
            portfolio=portfolio2,
            fullname='Ethereum',
            acronym='ETH',
            current_price=random.uniform(10.0, 100.0),
            mean_price=random.uniform(10.0, 100.0),
            win_loss=random.uniform(-10.0, 10.0)
        )

        assets = [asset1, asset2]

        # Erstellen Sie Kommentare
        comment = Comment.objects.create(text='Das ist ein Dummy-Kommentar.')

        # Erstellen Sie Transaktionstypen
        staking_type = TransactionType.objects.create(type='Staking-Reward')
        buy_type = TransactionType.objects.create(type='Einzahlung')
        sent_type = TransactionType.objects.create(type='Gesendet')
        trade_type = TransactionType.objects.create(type='Handel')
        t_types = [staking_type, buy_type, sent_type, trade_type]

        # Erstellen Sie Transaktionen
        for _ in range(10):  # Erstellen Sie 10 Dummy-Transaktionen
            Transaction.objects.create(
                user=user,
                asset=assets[random.randint(0, 1)],
                tx_type=t_types[random.randint(0, 3)],
                tx_comment=comment,
                tx_hash='hash{}'.format(random.randint(1, 100)),
                tx_sender_address='sender{}'.format(random.randint(1, 100)),
                tx_recipient_address='recipient{}'.format(random.randint(1, 100)),
                tx_amount=random.uniform(100.0, 1000.0),
                tx_value=random.uniform(100.0, 1000.0),
                tx_fee=random.uniform(1.0, 10.0),
                tx_date='2023-01-01T00:00:00Z'
            )

        self.stdout.write(self.style.SUCCESS('Data successfully created!'))
