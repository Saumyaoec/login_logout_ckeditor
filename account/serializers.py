from rest_framework import serializers
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'task', 'description', 'date_created']


class UserSerializer(serializers.ModelSerializer):

    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comments.objects.all())
    # comments_set = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name']