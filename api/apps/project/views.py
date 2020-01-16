from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Project
from .renderers import ProjectJSONRenderer
from .serializers import ProjectSerializerForList

class ProjectRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Project.objects.filter('user')
    renderer_classes = (ProjectJSONRenderer,)
    
