from django.contrib import admin
from .models import (
                      GithhubModelAPI,
                      BareActFileModel,
                      VectorDBInformation,
                      LanggraphDeployedAPI,
                      BareActsAgentConfiguration,
                      WebsearchAgentConfiguration,
                      ReflexionAgentConfiguration                       
                    )

admin.site.register(GithhubModelAPI)
admin.site.register(BareActFileModel)
admin.site.register(VectorDBInformation)
admin.site.register(LanggraphDeployedAPI)
admin.site.register(BareActsAgentConfiguration)
admin.site.register(WebsearchAgentConfiguration)
admin.site.register(ReflexionAgentConfiguration )