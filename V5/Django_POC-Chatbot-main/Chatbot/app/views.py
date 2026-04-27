import json
import datetime
from .models import *
from .serializers import *
from openpyxl import Workbook
from .Langserve_streamer import *
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

MODEL_MAP = {
    "Extension_Data": Extension_Data,
    "Extension_Data_BSA": Extension_Data_BSA,
    "Extension_Data_BNS": Extension_Data_BNS,
    "Extension_Data_DPDP": Extension_Data_DPDP,
    "Extension_Data_IT": Extension_Data_IT,
    "Extension_Data_Web_Search": Extension_Data_Web_Search
}

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


class ExportExcelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        table_name = request.GET.get("table")
        if not table_name:
            return Response({"error": "Missing 'table' parameter"}, status=400)

        filters = request.GET.dict()
        filters.pop("table", None)

        request._full_data = {
            "table": table_name,
            "filters": filters
        }
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            try:
                raw = request.body.decode("utf-8").strip()
                if raw:
                    body = json.loads(raw)
                else:
                    body = request._full_data   
            except:
                body = request._full_data        

            if not body:
                return Response({"error": "No input data provided"}, status=400)

            table_name = body.get("table")
            filters = body.get("filters", {})

            if table_name not in MODEL_MAP:
                return Response({"error": f"Invalid table: {table_name}"}, status=400)

            Model = MODEL_MAP[table_name]
            queryset = Model.objects.filter(**filters)

            wb = Workbook()
            ws = wb.active
            ws.title = table_name

            fields = [field.name for field in Model._meta.fields]
            ws.append(fields)

            for row_index, obj in enumerate(queryset, start=2):
                row_data = []

                for field in fields:
                    value = getattr(obj, field)

                    if isinstance(value, (datetime.datetime, datetime.time)):
                        if is_aware(value):
                            value = value.replace(tzinfo=None)

                    if isinstance(value, str):
                        value = value.replace("\\n", "\n")

                    row_data.append(value)

                ws.append(row_data)

                for col_idx in range(1, len(fields)+1):
                    ws.cell(row=row_index, column=col_idx).alignment = Alignment(wrap_text=True)

            for column_cells in ws.columns:
                length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
                ws.column_dimensions[column_cells[0].column_letter].width = min(length + 5, 60)

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{table_name}_export.xlsx"'

            wb.save(response)
            return response

        except Exception as e:
            return HttpResponse(str(e), status=500)


"""
http://127.0.0.1:8001/VLANC-LegalAI/export-excel/?table=Extension_Data_BNS
{
    "table": "Extension_Data",
    "filters": {
        "Thread_Id": "123456"
    }
}
"""