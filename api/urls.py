from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.note.views import NoteContentView, NoteViewSet
from api.query_search.views import SearchQueryViewSet
from api.words.views import WordListViewSet
from api.auth.login_views import UserLoginAPIView

router = DefaultRouter()


router.register('search_query', SearchQueryViewSet)
router.register('word_list', WordListViewSet)
router.register('note', NoteViewSet)
urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.catalogs.urls')),
    path('note_content/', NoteContentView.as_view(), name='note_content'),
    path('', include(router.urls)),
]
