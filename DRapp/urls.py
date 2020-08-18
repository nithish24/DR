from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.prelogin),
    path('home/', views.home),
    path('add', views.add),
    path('insert', views.insert),
    path('view/<int:id>', views.view_patient),
    path('search', views.search),
    path('list/<list_type>', views.get_all),
    path('addDR/<int:id>', views.dr),
    path('predict/<int:id>', views.preprocess),
    path('delete/<int:id>', views.delete),
    path('edit/<int:id>', views.edit_patient),
    path('update', views.update),
    path('print_pdf/<int:id>', views.print),
    path('login', views.loggingin),
    path('logout', views.user_logout)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
