from rest_framework.decorators import api_view
from api.models import SurveyOption
from django.shortcuts import redirect
from ratelimit.decorators import ratelimit


@api_view(['GET', ])
@ratelimit(key='ip', rate='1/d', block=True)
def SurveyVoteView(request, survey_id, option_id):
  try:
    option = SurveyOption.objects.get(uuid=option_id, survey__pk=survey_id)
  except SurveyOption.DoesNotExist:
    raise Http404("Survey option does not exist")

  option.votes = option.votes + 1
  option.save()

  return redirect("http://socialize.berlin/#thank-you-for-voting")
