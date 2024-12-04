from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.note.views import NoteContentViewSet, NoteLinkViewSet
from api.query_search.views import SearchQueryViewSet, ApplyQueryViewSet
from api.words.views import WordListViewSet
from api.auth.login_views import UserLoginAPIView

router = DefaultRouter()


router.register('search_query', SearchQueryViewSet)
router.register('apply_query', ApplyQueryViewSet)

router.register('word_list', WordListViewSet)
router.register('note_content', NoteContentViewSet)
router.register('note_link', NoteLinkViewSet)
urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.catalogs.urls')),
    path('', include(router.urls)),
]
