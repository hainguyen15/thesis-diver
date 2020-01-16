from rest_framework import serializers as sz
from api.apps.authentication.models import User
from api.apps.core.serializers import UserSerializer
from .models import Project

class ProjectSerializerForList(sz.ModelSerializer):
    status = sz.CharField(source='get_status_display')
    
    class Meta:
        model = Project
        fields = ('id', 'title', 'status')

class ProjectSerializerForCreate(sz.ModelSerializer):
    pass

class ProjectSerializerForDetail(sz.ModelSerializer):
    pass
