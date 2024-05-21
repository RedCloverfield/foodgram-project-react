from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, permission_classes=(IsAuthenticated,), pagination_class=LimitOffsetPagination)  # дописать permission_classes
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following_users__user=request.user)  # нужен объект пользователя!
        # if not subscriptions:
        #     return Response(data='Вы еще ни на кого не подписаны.', status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, context={'request': request}, many=True)  # уточнить про context
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'), permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        followed_user = self.get_object()
        if request.method == 'POST':
            if user == self.get_object():
                return Response(dict(errors='Нельзя подписаться на самого себя.'), status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, followed_user=followed_user).exists():
                return Response(dict(errors='Вы уже подписаны на этого пользователя.'), status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, followed_user=followed_user)
            serializer = FollowSerializer(instance=followed_user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not Follow.objects.filter(user=user, followed_user=followed_user).exists():
                return Response(dict(errors='Вы не подписаны на этого пользователя.'), status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get(user=user, followed_user=followed_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action == 'me':
            return IsAuthenticated(),
        elif self.action == 'retrive':
            return AllowAny(),
        return super().get_permissions()  # переделать
