"""
URL configuration for connector project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from django.contrib import admin
from . import views  # Assuming the views are in the same directory for now
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from connector import consumers

websocket_urlpatterns = [
    path('ws/console/', consumers.ConsoleConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns)
})

urlpatterns = [
    path('app/', views.vue_app, name='vue_app'),
    path('admin/', admin.site.urls),
    path('list_blocks/', views.list_blocks, name='list_blocks'),
    path('start_block/<int:block_id>/', views.start_block, name='start_block'),
    path('stop_block/<int:block_id>/', views.stop_block, name='stop_block'),
    path('delete_block/<int:block_id>/', views.delete_block, name='delete_block'),
    path('create_block/', views.create_block, name='create_block'),
    path('', views.list_blocks, name='list_blocks'),
    re_path(r'^.*$', views.vue_app, name='vue_app'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)