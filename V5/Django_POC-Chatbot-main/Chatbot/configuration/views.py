from django.shortcuts import render
import json
import datetime
from .models import *
from .serializers import *
from openpyxl import Workbook
from rest_framework import status
from django.utils import timezone
from collections import defaultdict
from django.http import HttpResponse
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils.timezone import is_aware
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles import Alignment



# @method_decorator(csrf_exempt, name='dispatch')
class Get_Configuration(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = {}
            if VectorDBInformation.objects.exists():
                grouped_data = defaultdict(list)
                all_vectors = VectorDBInformation.objects.all().order_by('-Checked_on')
                serialized_vectors = VectorDBInformationSerializer(all_vectors, many=True).data
                for entry in serialized_vectors:
                    act_name = entry.get("DB_name", "Unknown_Act")
                    grouped_data[act_name].append(entry)

                data['vector_db'] = grouped_data

            if BareActsAgentConfiguration.objects.exists():
                data['bare_acts_agent'] = BareActsAgentConfigurationSerializer(
                                            BareActsAgentConfiguration.objects.last()
                                            ).data

            if WebsearchAgentConfiguration.objects.exists():
                data['websearch_agent'] = WebsearchAgentConfigurationSerializer(
                                            WebsearchAgentConfiguration.objects.last()
                                            ).data

            if ReflexionAgentConfiguration.objects.exists():
                data['reflexion_agent'] = ReflexionAgentConfigurationSerializer(
                                            ReflexionAgentConfiguration.objects.last()
                                            ).data
            
            if Githhub_Model_API.objects.exists():
                 data['GithubModel_Api'] = Githhub_Model_APISerializer(
                                            Githhub_Model_API.objects.last()
                                            ).data



            return Response({
                            "status": "success",
                            "message": "Latest configuration fetched successfully.",
                            "data": data
                            }, 
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                            "status": "error",
                            "message": f"Error fetching configuration: {str(e)}"
                            }, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
