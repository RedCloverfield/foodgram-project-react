from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, pagination_class=LimitOffsetPagination)
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following_users__user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            page, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        user = request.user
        followed_user = self.get_object()
        if request.method == 'POST':
            if user == self.get_object():
                raise exceptions.ParseError(
                    detail='Нельзя подписаться на самого себя.'
                )
            _, creation_status = Follow.objects.get_or_create(
                user=user, followed_user=followed_user
            )
            if not creation_status:
                raise exceptions.ParseError(
                    detail='Вы уже подписаны на этого пользователя.'
                )
            serializer = FollowSerializer(
                instance=followed_user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            Follow.objects.get(user=user, followed_user=followed_user).delete()
        except Follow.DoesNotExist:
            raise exceptions.ParseError(
                detail='Вы не подписаны на этого пользователя.'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'me':
            return IsAuthenticated(),
        elif self.action == 'retrive':
            return AllowAny(),
        return super().get_permissions()
