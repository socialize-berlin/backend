from rest_framework.decorators import api_view
from django.shortcuts import render
from api.models import Connection
from django.conf import settings
from django.http import Http404

@api_view(['GET', ])
def EmailConnectNotificationView(request):
    if not settings.DEBUG:
        raise Http404("Not found")

    connection = Connection.objects.filter(status='P').first()

    context = {
        'connection': connection,
    }

    return render(request, 'api/connect_notification.html', context)

@api_view(['GET', ])
def EmailConnectNotificationStatusView(request):
    if not settings.DEBUG:
        raise Http404("Not found")

    connection = Connection.objects.filter(status='P').first()

    context = {
        'connection': connection,
    }

    return render(request, 'api/connect_notification.html', context)
