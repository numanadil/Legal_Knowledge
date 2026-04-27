from rest_framework import serializers
from .models import (
    FileModel, VectorDBInformation, BareActsAgentConfiguration,
    WebsearchAgentConfiguration, ReflexionAgentConfiguration,
    Extension_Data, Extension_Data_BSA, Extension_Data_BNS,
    Extension_Data_IT, Extension_Data_Web_Search, Extension_Data_DPDP,
    Githhub_Model_API
)

class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = '__all__'

class VectorDBInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorDBInformation
        fields = '__all__'

class BareActsAgentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BareActsAgentConfiguration
        fields = '__all__'

class WebsearchAgentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsearchAgentConfiguration
        fields = '__all__'

class ReflexionAgentConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReflexionAgentConfiguration
        fields = '__all__'

class ExtensionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data
        fields = '__all__'

class ExtensionDataBSASerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data_BSA
        fields = '__all__'

class ExtensionDataDPDPSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data_DPDP
        fields = '__all__'

class ExtensionDataBNSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data_BNS
        fields = '__all__'

class ExtensionDataITSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data_IT
        fields = '__all__'

class ExtensionDataWebSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension_Data_Web_Search
        fields = '__all__'

class Githhub_Model_APISerializer(serializers.ModelSerializer):
    class Meta:
        model = Githhub_Model_API
        fields = '__all__'


