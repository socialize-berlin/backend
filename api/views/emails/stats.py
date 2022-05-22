from rest_framework.decorators import api_view
from django.shortcuts import render
from api.models import Connection, User, Survey
from django.conf import settings
from django.http import Http404
import math
import geopandas as gpd
from shapely.geometry import Point

@api_view(['GET', ])
def EmailStatsView(request):
    berlin_neighbourhoods_df = gpd.read_file('api/helpers/neighbourhoods.geojson')
    users_locations = User.objects.filter(lat__isnull=False, lng__isnull=False)

    counts = {}

    for user in users_locations:
        location = Point(user.lng, user.lat)

        for index, row in berlin_neighbourhoods_df.iterrows():
            if location.within(row['geometry']):
                if row['neighbourhood_group'] in counts:
                    counts[row['neighbourhood_group']] += 1
                else:
                    counts[row['neighbourhood_group']] = 1

    # Get key with max count
    max_count = max(counts.values())
    max_count_key = max(counts, key=lambda k: counts[k])

    total_users = User.objects.all().count()
    total_connections = Connection.objects.all().count()
    accepted_connections = Connection.objects.filter(status='A').count()

    avg_response_rate = accepted_connections / total_connections * 100
    avg_response_rate = math.floor(avg_response_rate)

    # Get featured survey
    featured_survey = Survey.objects.filter(is_featured=True).first()

    context = {
        'total_users': total_users,
        'accepted_connections': accepted_connections,
        'avg_response_rate': avg_response_rate,
        'most_popular_neighbourhood': max_count_key,
        'most_popular_neighbourhood_count': max_count,
        'survey': featured_survey,
    }

    return render(request, 'api/stats_email.html', context)
