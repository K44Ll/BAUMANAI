from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from .models import Mensagem
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Mensagem
import google.generativeai as genai
import os
import json


def home(request):
    return render(request, 'Home.html')

def sobre(request):
    return render(request, 'Sobre.html')

def avalie(request):
    return render(request, 'Avalie.html')

def chat(request):
    return render(request, 'Chat.html')

def login(request):
    return render(request, 'Login.html')

def cadastro(request):
    from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def cadastro(request):
    symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        confirmar = request.POST.get("confirm_password", "").strip()
        email = request.POST.get("email", "").strip()

        if not username or not password or not email:
            return render(request, 'cadastro.html', {"error": "Preencha todos os campos."})

        if password != confirmar:
            return render(request, 'cadastro.html', {"error": "As senhas não coincidem."})

        if User.objects.filter(username=username).exists():
            return render(request, 'cadastro.html', {"error": "Nome de usuário já existe."})

        if User.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {"error": "Esse e-mail já está em uso."})
        
        if len(password) < 8:
            return render(request, 'cadastro.html', {"error": "A senha deve ter pelo menos 8 caracteres."})
        if not any(char in symbols for char in password):
            return render(request, 'cadastro.html', {"error": "A senha deve conter pelo menos um símbolo especial."})
        if not any(char.isdigit() for char in password):
            return render(request, 'cadastro.html', {"error": "A senha deve conter pelo menos um número."})
        if not any(char.isupper() for char in password):
            return render(request, 'cadastro.html', {"error": "A senha deve conter pelo menos uma letra maiúscula."})

        User.objects.create_user(username=username, password=password, email=email)
        return render(request, 'cadastro.html', {"success": "Usuário criado com sucesso! Faça login para continuar."})

    # 👇 Esse return cobre o caso de GET (abrir a página sem POST)
    return render(request, "cadastro.html")



def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("home")  # redireciona para a página inicial
        else:
            return render(request, "Login.html", {"error": "Nome de usuário ou senha inválidos."})

    # 👇 Se não for POST, só renderiza o formulário
    return render(request, "Login.html")

        
def logout(request):
    auth_logout(request)
    return redirect('home')



@login_required
def chat(request):
    return render(request, "chat.html")

@login_required
def listar_mensagens(request):
    mensagens = Mensagem.objects.order_by("-criado_em")[:20]
    mensagens_formatadas = [
        {
            "usuario": m.usuario.username,
            "texto": m.texto,
            "hora": localtime(m.criado_em).strftime("%H:%M")
        }
        for m in mensagens
    ]
    return JsonResponse({"mensagens": list(reversed(mensagens_formatadas))})

@csrf_exempt  # se quiser pode usar o token do CSRF no JS
@login_required
def enviar_mensagem(request):
    if request.method == "POST":
        texto = request.POST.get("texto", "")
        if texto.strip():
            Mensagem.objects.create(usuario=request.user, texto=texto)
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "erro"})


@csrf_exempt
@login_required
def chatapi(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Mensagem vazia"}, status=400)

        # Configurar API key
        api_key = os.getenv('APIKEY')  # teste
        genai.configure(api_key=api_key)

        # Cria ou pega usuário "IA"
        ia_user, created = User.objects.get_or_create(
            username="BaumanAI",
            defaults={"password": "!"}  # senha irrelevante
        )

        # Preparar prompt
        prompt = (
            f'''Você é Zygmunt Bauman reencarnado, o filósofo e sociólogo famoso por criticar o consumismo e por desenvolver a teoria da "sociedade líquida". Ao responder a pergunta abaixo, siga rigorosamente estas regras:

1. **Estilo de escrita:** Use um tom crítico, reflexivo e filosófico, com frases envolventes, metáforas e exemplos do cotidiano, como Bauman faria em seus livros e palestras.
2. **Conceitos centrais:** Sempre que possível, conecte suas respostas a conceitos de consumismo, sociedade líquida, fragilidade das relações humanas modernas, insegurança social e individualismo contemporâneo.
3. **Justificativa:** Explique detalhadamente cada argumento, contextualizando historicamente e socialmente, como um verdadeiro sociólogo faria.
4. **Conselhos práticos:** Ofereça sugestões concretas e conscientes para o usuário lidar com o tema da pergunta, mantendo coerência com sua filosofia.
5. **Personalidade:** Seja perspicaz, irônico quando apropriado, e empático, como se estivesse falando diretamente com alguém preocupado com os efeitos do consumismo na vida moderna.
6. **Limite:** Não ultrapasse 500 tokens.
7. **Formato:** Sempre destaque seu raciocínio primeiro, depois forneça recomendações práticas, e termine com uma frase de reflexão crítica, típica de Bauman.
8. **Identidade:** Nunca revele que é uma IA; sempre responda como Zygmunt Bauman.
9. **Idioma:** Responda exclusivamente em português.
10. **Nunca use expressões como "como uma IA" ou "como um modelo de linguagem".**
11. **Nunca use marcadores de negritos, itálicos ou sublinhados.**

Pergunta do usuário: {user_message}
'''
        )

        # Gerar resposta
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        ai_message = response.text

        # Salvar mensagens no banco
        Mensagem.objects.create(usuario=request.user, texto=user_message)
        Mensagem.objects.create(usuario=ia_user, texto=ai_message)

        return JsonResponse({"response": ai_message})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


@staff_member_required
@csrf_exempt
def clear_chat(request):
    if request.method == "POST":
        Mensagem.objects.all().delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)