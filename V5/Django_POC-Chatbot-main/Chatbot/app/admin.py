from django.contrib import admin

from .models import (
                     FileModel,
                     Extension_Data,
                     Githhub_Model_API,
                     Extension_Data_IT,
                     Visual_explanation,
                     Extension_Data_BNS,
                     Extension_Data_BSA,
                     Extension_Data_DPDP,
                     VectorDBInformation,
                     Langgraph_Deployed_API,
                     Extension_Data_Web_Search,
                     BareActsAgentConfiguration,
                     WebsearchAgentConfiguration,
                     ReflexionAgentConfiguration,
                     Langgraph_Deployed_Agent_Name
                    )



admin.site.register(FileModel)
admin.site.register(Extension_Data)
admin.site.register(Extension_Data_IT)
admin.site.register(Visual_explanation)
admin.site.register(Githhub_Model_API)
admin.site.register(Extension_Data_BNS)
admin.site.register(Extension_Data_BSA)
admin.site.register(Extension_Data_DPDP)
admin.site.register(VectorDBInformation)
admin.site.register(Langgraph_Deployed_API)
admin.site.register(Extension_Data_Web_Search)
admin.site.register(BareActsAgentConfiguration)
admin.site.register(WebsearchAgentConfiguration)
admin.site.register(ReflexionAgentConfiguration)
admin.site.register(Langgraph_Deployed_Agent_Name)