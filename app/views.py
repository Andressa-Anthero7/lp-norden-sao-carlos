from django.shortcuts import render, redirect
import requests
from .models import Leads, Config_WhatsApp
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404
# importação do webhook
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json 
import hmac
import hashlib
import os
import logging

# Create your views here.
def index(request):
    if request.method == 'POST':
        # Capturar os dados do formulário
        nome_leads = request.POST.get('nome') 
        whats_app_leads = request.POST.get('whatsapp')
        recebido_em = datetime.now()
        Leads.objects.create(nome_leads=nome_leads, whats_app_leads=whats_app_leads, data_recebimento=recebido_em)
        
        # Montar a mensagem
        message = f"Olá, Adriana! Você recebeu novo lead - Nome: {nome_leads} - WhatsApp: {whats_app_leads}<br>Acesse: www.afnordensaude.com.br/accounts/login/adriana/dashboard/"
        
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
        config_wa = Config_WhatsApp.objects.last()
        print(config_wa)
        return render(request, 'site/index.html',{'config_wa':config_wa})

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

# Configuração de log para capturar as ações
logger = logging.getLogger(__name__)

@csrf_exempt
def webhook(request):
    if request.method == "POST":
        try:
            # Obtém o segredo da variável de ambiente (melhor prática de segurança)
            #secret = os.getenv('GITHUB_WEBHOOK_SECRET').encode('utf-8')  # Certifique-se de definir essa variável no servidor
            secret = b'deploy_key_norden'
            signature = request.headers.get('X-Hub-Signature-256', '')  # Obtém a assinatura enviada pelo GitHub
            payload = request.body  # Corpo da requisição (dados enviados pelo GitHub)

            # Calcula a assinatura usando o segredo e o corpo da requisição
            mac = hmac.new(secret, msg=payload, digestmod=hashlib.sha256)
            expected_signature = f"sha256={mac.hexdigest()}"

            # Verifica se a assinatura recebida é válida comparando com a esperada
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Assinatura inválida recebida do GitHub")
                return JsonResponse({'error': 'Invalid signature'}, status=403)

            # Carrega o payload como JSON
            payload = json.loads(payload)

            # Verifica se o evento é um push no branch 'dev'
            if payload.get('ref') == 'refs/heads/dev':
                logger.info("Push detectado no branch 'dev', iniciando o deploy.")
                # Chama o script de deploy no servidor
                subprocess.call(['/home/ubuntu/deploy.sh'])

                # Retorna resposta de sucesso
                return JsonResponse({'status': 'Deployed successfully'}, status=200)
            else:
                logger.info(f"Push para outro branch: {payload.get('ref')}")
                return JsonResponse({'status': 'Not a push to dev branch'}, status=200)

        except Exception as e:
            logger.error(f"Erro ao processar o webhook: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)

def remover_lead(request,pk):
    lead_remover = get_object_or_404(Leads, pk=pk)
    lead_remover.delete()
    return JsonResponse({'Status': 'Leads Removido com Sucesso!!'}, status=200)