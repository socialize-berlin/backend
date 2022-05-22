from django.urls import path
from django.conf.urls import url, include
from api.views.emails import EmailConnectNotificationView, EmailStatsView
from api.views.survey import SurveyVoteView

urlpatterns = [
    path('email/connect-notification/', EmailConnectNotificationView),
    path('email/stats/', EmailStatsView),
    path('survey/<uuid:survey_id>/vote/<uuid:option_id>/', SurveyVoteView),
]
