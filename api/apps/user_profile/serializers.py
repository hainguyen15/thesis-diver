from rest_framework import serializers
from apps.core.constants import STC_DEFAUL_PROFILE_IMG
from apps.authentication.models import User
from .models import Profile

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    username    = serializers.CharField(source='user.username')
    # user    = ProfileUserSerializer(read_only=True)
    bio     = serializers.CharField(allow_blank=True, required=False)
    image   = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        # fields = '__all__'
        fields = ('username', 'bio', 'image',)
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image
        
        return STC_DEFAUL_PROFILE_IMG
