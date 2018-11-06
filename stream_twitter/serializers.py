from django.contrib.auth.models import User
from .models import Tweet
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "groups", "user_permissions"]


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Tweet
        fields = "__all__"


# TODO: move this to stream-django
class ActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    foreign_id = serializers.CharField()
    verb = serializers.CharField()
    time = serializers.DateTimeField()

    def __init__(self, *args, **kwargs):
        object_serializer = kwargs.pop("object_serializer", None)
        actor_serializer = kwargs.pop("actor_serializer", None)
        super().__init__(self, *args, **kwargs)
        if object_serializer:
            self.fields["object"] = object_serializer()
        else:
            self.fields["object"] = serializers.CharField()
        if actor_serializer:
            self.fields["actor"] = actor_serializer()
        else:
            self.fields["actor"] = serializers.CharField()


# TODO: check if this works
class AggregatedSerializer(ActivitySerializer):
    group = serializers.CharField()
    activities = ActivitySerializer(many=True)


# TODO: check if this works
class NotificationSerializer(AggregatedSerializer):
    is_seen = serializers.BooleanField()
    is_read = serializers.BooleanField()


def get_activity_serializer(data, object_serializer=None, actor_serializer=None, **kwargs):
    kwargs["object_serializer"] = object_serializer
    kwargs["actor_serializer"] = actor_serializer
    serializer = ActivitySerializer
    if "is_seen" in data:
        serializer = NotificationSerializer
    elif "activities" in data:
        serializer = AggregatedSerializer
    return serializer(data, **kwargs)
