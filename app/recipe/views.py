from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe import serializers

class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in db"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_querset(self):
        """Return objects for current authenticate user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
