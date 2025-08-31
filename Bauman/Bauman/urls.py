from django.contrib import admin
from django.urls import path
from Trabalho.views import home
from Trabalho.views import sobre
from Trabalho.views import avalie
from Trabalho.views import chat
from Trabalho.views import login
from Trabalho.views import cadastro
from Trabalho.views import logout
from django.urls import path
from Trabalho import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('sobre/', sobre, name='sobre'),
    path('avalie/', avalie, name='avalie'),
    path('chat/', chat, name='chat'),
    path('login/', login, name='login'),
    path('cadastro/', cadastro, name='cadastro'),
    path('logout/', logout, name='logout'),
    path('chat', chat, name='chat'),
    path("chat/mensagens/", views.listar_mensagens, name="listar_mensagens"),
    path("chat/enviar/", views.enviar_mensagem, name="enviar_mensagem"),
    path('chatapi/', views.chatapi, name='chatapi'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),  # Novo endpoint para limpar o chat


]
