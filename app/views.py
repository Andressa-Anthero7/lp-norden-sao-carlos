from django.shortcuts import render, redirect
import requests
from .models import Leads, Config_WhatsApp
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# importação do webhook
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json 
import hmac
import hashlib

# Create your views here.
def index(request):
    if request.method == 'POST':
        # Capturar os dados do formulário
        nome_leads = request.POST.get('nome') 
        whats_app_leads = request.POST.get('whatsapp')
        recebido_em = datetime.now()
        Leads.objects.create(nome_leads=nome_leads, whats_app_leads=whats_app_leads, data_recebimento=recebido_em)
        
        # Montar a mensagem
        message = f"Olá, Adriana! Você recebeu novo lead - Nome: {nome_leads} - WhatsApp: {whats_app_leads}<br>Acesse: www.afunimedsaocarlos.com.br/accounts/login/adriana/dashboard/"
        
        config_wa = Config_WhatsApp.objects.values('numero_whats_app', 'chave_api_whats_app')
        print(config_wa)
        for item in config_wa:
            # Pegando os valores diretamente do dicionário
            whats_app_receptor = item['numero_whats_app']
            api_key = item['chave_api_whats_app']
            print(f'receptor',whats_app_receptor)
            print(f'api key',api_key)
    
        # URL da API do CallMeBot (o WhatsApp deve estar no formato internacional)
        url = f'https://api.callmebot.com/whatsapp.php?phone=55{whats_app_receptor}&text={message}&apikey={api_key}'


        # Enviar a mensagem via requisição GET
        response = requests.get(url)

        # Verificar a resposta
        if response.status_code == 200:
            print("Mensagem enviada com sucesso!")
            return render(request, 'site/agradecimento.html')
        else:
            print("Falha ao enviar a mensagem.")
            print(f"Status code: {response.status_code}")
            return render(request, 'site/agradecimento.html')
    else:
        return render(request, 'site/index.html')

def agradecimento(request):
    return render(request, 'site/agradecimento.html')

@login_required
def dashboard(request,user):
    leads = Leads.objects.all().order_by('-data_recebimento')
    quantidade_leads = Leads.objects.all()
    return render(request, 'site/dashboard.html', {'leads': leads,'quantidade_leads':quantidade_leads})

def status_envelope_leads(request,pk):
    if request.method == "POST":
        print('post')
        novo_status_envelope_leads = 'fa-envelope-open-text'
        Leads.objects.filter(pk=pk).update(status_envelope=novo_status_envelope_leads)
        leads = Leads.objects.all().order_by('-data_recebimento')
        quantidade_leads = Leads.objects.all()
        return redirect(reverse('dashboard',args=[request.user]))
    else:
        return redirect(reverse('dashboard',args=[request.user]))

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('login_redirect')  # Chama a URL de redirecionamento
        else:
            return render(request, 'registration/login.html', {'error': 'Usuário ou senha inválidos.'})
    return render(request, 'registration/login.html')

@login_required
def login_redirect(request):
    username = request.user.username
    url_redirect = f'/accounts/login/{username}/dashboard/'  # URL do dashboard
    return redirect(url_redirect)

import hmac
import hashlib

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        try:
            secret = b''  # Mesmo valor configurado no GitHub
            signature = request.headers.get('X-Hub-Signature-256', '')
            payload = request.body
            mac = hmac.new(secret, msg=payload, digestmod=hashlib.sha256)
            expected_signature = f"sha256={mac.hexdigest()}"

            if not hmac.compare_digest(signature, expected_signature):
                return JsonResponse({'error': 'Invalid signature'}, status=403)

            payload = json.loads(payload)
            if payload.get('ref') == 'refs/heads/dev':
                subprocess.call(['/home/ubuntu/deploy.sh'])
                return JsonResponse({'status': 'Deployed successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)
