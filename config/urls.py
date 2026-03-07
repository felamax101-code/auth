from django.urls import path,include 
from django.conf import settings 
from django.contrib import admin
from django.conf.urls.static import static
urlpatterns=[
    path('admin/',admin.site.urls),
    path("api/auth/",include("apps.users.urls")),
    path("api/",include("apps.blog.urls")),
    path("api/cw/",include("apps.carwash.urls")),
    path("api/ec/",include("apps.EC.urls")),
    path("api/smartpythonists/",include("apps.smartpythonists.urls"))
    ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
