import json
from datetime import datetime, timezone
from decimal import Decimal

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import FundingWalletTransaction, FundingWalletBalance

def home(request):
    def prices():
        try:
            url = 'https://epic-radar.com/api/coingecko/'
            response = requests.get(url=url)

            if response.status_code == 200:
                return response.json()['results'][0]
        except Exception as e:
            print(e)
            return

    def total_payments():
        return FundingWalletTransaction.objects.count()

    def received_in_percent(goal):
        return round(total_received_funds_in_usd() / float(goal) * 100, 1)

    def total_received_funds_in_usd():
        amount = balance_from_transactions() * Decimal(prices()[f'epic_vs_usd'])
        return int(amount)

    def transaction_history():
        return FundingWalletTransaction.objects.filter(amount__gt=0.9).order_by('-timestamp')

    def balance_from_transactions():
        txs = transaction_history()
        return Decimal(sum([tx.amount for tx in txs]))

    context = {
        'received_percent': received_in_percent(goal=5000),
        'milestone_goal': '5 000',
        'total_payments': total_payments(),
        'last_update': FundingWalletBalance.objects.last().timestamp,
        'history': transaction_history(),
        'total': total_received_funds_in_usd()  # rounded in USD
        }

    html_template = 'funding/home.html'
    return render(request, html_template, context)


def balance(request):
    if request.method == 'POST':
        data = {
            'timestamp': datetime.utcnow(),
            'balances': {'EPIC-002': json.loads(request.POST.get('EPIC-002'))},
            }

        # Create or update new FundingWalletBalance object
        update, created = FundingWalletBalance.objects.get_or_create(**data)
        if created:
            print(f"NEW RECORD: {update}")
        else:
            update.timestamp = datetime.now()
            update.save()

    elif request.method == 'GET':
        print(request.GET)

    return JsonResponse({})


def transactions(request):
    if request.method == 'POST':
        data = {
            'timestamp': datetime.fromtimestamp(int(request.POST.get('timestamp')), timezone.utc),
            'amount': Decimal(request.POST.get('amount')),
            'height': int(request.POST.get('height')),
            'token': request.POST.get('token'),
            'hash': request.POST.get('hash')
            }

        tx, created = FundingWalletTransaction.objects.get_or_create(**data)

        if created:
            print(f"NEW TRANSACTION: {tx}")
        else:
            print(f"TRANSACTION: ALREADY IN DB {tx}")

    elif request.method == 'GET':
        print(request.GET.get('data'))

    return JsonResponse({})
