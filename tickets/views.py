from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Ticket, Comentario
import datetime
import io

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- AUTENTICAÇÃO ---

# View responsável pelo login de usuários no sistema
def login_view(request):
    # Se o usuário já estiver autenticado, redireciona diretamente para a lista de chamados
    if request.user.is_authenticated:
        return redirect('ticket_list')
    
    # Processa os dados enviados via formulário POST
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('ticket_list')
        else:
            error = "Usuário ou senha inválidos."
            return render(request, 'tickets/login.html', {'error': error})
            
    return render(request, 'tickets/login.html')

# View responsável pelo registro de novos usuários no SQLite do Django
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        empresa = request.POST.get('empresa', '').strip()
        tipo = request.POST.get('tipo', 'cliente')

        # Validação estrita para garantir que não há espaços no nome de usuário
        if ' ' in username:
            return render(request, 'tickets/register.html', {
                'error': 'O nome de usuário não pode conter espaços!'
            })

        # Verifica se o nome de usuário já existe na base de dados
        if User.objects.filter(username=username).exists():
            return render(request, 'tickets/register.html', {
                'error': 'Este nome de usuário já está em uso.'
            })

        # Define as bandeiras de permissão (is_staff e is_superuser) com base no tipo de conta escolhido
        is_staff = False
        is_superuser = False
        
        if tipo == 'tecnico':
            is_staff = True
        elif tipo == 'admin':
            is_staff = True
            is_superuser = True

        # Cria o usuário no banco relacional do Django
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Realiza o login automático após o cadastro e redireciona
        login(request, user)
        return redirect('ticket_list')

    return render(request, 'tickets/register.html')

# View para encerrar a sessão do usuário atual
def logout_view(request):
    logout(request)
    return redirect('login')


# --- TICKETS ---

# View que lista os chamados com suporte a filtros e métricas baseadas no perfil (Cliente vs Staff)
@login_required
def ticket_list(request):
    status_filter = request.GET.get('status')
    categoria_filter = request.GET.get('categoria')
    
    # Monta a query dinâmica para o MongoEngine
    query = {}
    if status_filter:
        query['status'] = status_filter
    if categoria_filter:
        query['categoria'] = categoria_filter

    # Se não for staff/técnico, restringe a visualização apenas aos chamados criados pelo próprio usuário
    if not request.user.is_staff:
        query['solicitante'] = request.user.username

    tickets = Ticket.objects(**query)
    
    # Define o escopo base para o cálculo dos indicadores/métricas
    base_qs = Ticket.objects(solicitante=request.user.username) if not request.user.is_staff else Ticket.objects
    
    total = base_qs.count()
    abertos = base_qs(status='ABERTO').count()
    em_andamento = base_qs(status='EM_ANDAMENTO').count()
    resolvidos = base_qs(status__in=['RESOLVIDO', 'FECHADO']).count()

    context = {
        'tickets': tickets,
        'metrics': {'total': total, 'abertos': abertos, 'em_andamento': em_andamento, 'resolvidos': resolvidos},
        'selected_status': status_filter,
        'selected_categoria': categoria_filter,
    }
    return render(request, 'tickets/ticket_list.html', context)

# View para a criação de um novo chamado com suporte opcional a upload de arquivos/imagens
@login_required
def ticket_create(request):
    if request.method == 'POST':
        anexo_url = None
        
        # Tratamento de upload de imagem/arquivo utilizando o FileSystemStorage do Django
        if 'anexo' in request.FILES:
            myfile = request.FILES['anexo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            anexo_url = fs.url(filename)

        # Instancia e salva o novo ticket no MongoDB
        ticket = Ticket(
            titulo=request.POST.get('titulo'),
            solicitante=request.user.username,
            categoria=request.POST.get('categoria'),
            prioridade=request.POST.get('prioridade'),
            descricao=request.POST.get('descricao'),
            anexo=anexo_url
        )
        ticket.save()
        return redirect('ticket_list')

    return render(request, 'tickets/ticket_create.html')

# View para exibir os detalhes de um chamado específico, interações, comentários e ações de técnico
@login_required
def ticket_detail(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404("Chamado não encontrado.")

    # Trata requisições POST (mudança de status, assumir chamado ou adicionar comentário)
    if request.method == 'POST':
        # 1. Técnico ou Admin assume a responsabilidade pelo chamado
        if 'assumir' in request.POST and (request.user.is_staff or request.user.is_superuser):
            ticket.tecnico_responsavel = request.user.username
            if ticket.status == 'ABERTO':
                ticket.status = 'EM_ANDAMENTO'
            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket.id)

        # 2. Técnico ou Admin altera o status do chamado diretamente
        if 'status' in request.POST and (request.user.is_staff or request.user.is_superuser):
            novo_status = request.POST.get('status')
            if novo_status in ['ABERTO', 'EM_ANDAMENTO', 'RESOLVIDO', 'FECHADO']:
                ticket.status = novo_status
                ticket.save()
                return redirect('ticket_detail', ticket_id=ticket.id)

        # 3. Adiciona um novo comentário anexo ao documento do ticket
        mensagem = request.POST.get('comentario', '').strip()
        if mensagem:
            novo_comentario = Comentario(
                autor=request.user.username,
                mensagem=mensagem,
                criado_em=datetime.datetime.now(datetime.timezone.utc)
            )
            ticket.comentarios.append(novo_comentario)
            ticket.atualizado_em = datetime.datetime.now(datetime.timezone.utc)
            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


# --- PERFIL ---

# View para gerenciar e atualizar informações cadastrais e senhas do usuário logado
@login_required
def profile_view(request):
    error = None
    success = None

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha_atual = request.POST.get('senha_atual', '')
        nova_senha = request.POST.get('nova_senha', '')
        
        # Atualiza o endereço de e-mail do usuário
        if email:
            request.user.email = email
            request.user.save()
            success = 'Dados atualizados com sucesso!'

        # Valida e processa a alteração de senha caso os campos estejam preenchidos
        if senha_atual and nova_senha:
            if request.user.check_password(senha_atual):
                request.user.set_password(nova_senha)
                request.user.save()
                update_session_auth_hash(request, request.user) # Mantém a sessão ativa após mudar a senha
                success = 'Senha alterada com sucesso!'
            else:
                error = 'A senha atual está incorreta.'

    return render(request, 'tickets/profile.html', {
        'error': error,
        'success': success
    })


# --- PAINEL ADMINISTRATIVO (DASHBOARD) ---

# View exclusiva para Administradores gerenciarem usuários, chamados e métricas globais
@login_required
def admin_dashboard(request):
    # Restrição estrita: apenas superusuários podem acessar este painel
    if not request.user.is_superuser:
        return redirect('ticket_list')

    # Processa ações administrativas via POST (exclusão de tickets ou de usuários)
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        
        if action_type == 'delete_ticket':
            ticket_id = request.POST.get('ticket_id')
            Ticket.objects(id=ticket_id).delete()
            return redirect('admin_dashboard')
            
        elif action_type == 'delete_user':
            user_id = request.POST.get('user_id')
            target_user = User.objects.get(id=user_id)
            if target_user != request.user: # Impede que o admin exclua a si mesmo
                target_user.delete()
            return redirect('admin_dashboard')

    # Coleta indicadores estatísticos gerais do MongoDB
    total_tickets = Ticket.objects.count()
    abertos = Ticket.objects(status='ABERTO').count()
    em_andamento = Ticket.objects(status='EM_ANDAMENTO').count()
    resolvidos = Ticket.objects(status='RESOLVIDO').count()
    fechados = Ticket.objects(status='FECHADO').count()

    # Listagens completas para gerenciamento administrativo
    todos_chamados = Ticket.objects.order_by('-criado_em')
    todos_usuarios = User.objects.all()

    context = {
        'total_tickets': total_tickets,
        'abertos': abertos,
        'em_andamento': em_andamento,
        'resolvidos': resolvidos,
        'fechados': fechados,
        'todos_chamados': todos_chamados,
        'todos_usuarios': todos_usuarios,
    }
    return render(request, 'tickets/admin_dashboard.html', context)

# View para gerar relatórios gerenciais personalizados em PDF formatados via ReportLab com filtros dinâmicos
@login_required
def admin_relatorios(request):
    if not request.user.is_superuser:
        return redirect('ticket_list')

    if request.method == 'POST':
        tipo_relatorio = request.POST.get('tipo_relatorio')
        status_filtro = request.POST.get('status_filtro')
        categoria_filtro = request.POST.get('categoria_filtro')

        # Monta os filtros dinâmicos para a busca no MongoDB
        query = {}
        if status_filtro:
            query['status'] = status_filtro
        if categoria_filtro:
            query['categoria'] = categoria_filtro

        chamados = Ticket.objects(**query).order_by('-criado_em')

        # Configura o layout e documento PDF com margens e tamanho Letter
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightWidth=letter[0],
            leftMargin=40, rightMargin=40,
            topMargin=40, bottomMargin=40
        )
        
        elements = []
        styles = getSampleStyleSheet()

        # Estilos customizados de texto para o PDF
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e1b4b'), # Azul escuro corporativo
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'), # Cinza elegante
            spaceAfter=15
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#1e293b')
        )

        # Adiciona o cabeçalho descritivo do relatório
        elements.append(Paragraph("DeskFlow — Relatório Gerencial", title_style))
        filtros_txt = f"Filtros aplicados: Status = <b>{status_filtro or 'Todos'}</b> | Categoria = <b>{categoria_filtro or 'Todas'}</b>"
        gerado_txt = f"Emitido em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        elements.append(Paragraph(f"{filtros_txt} | {gerado_txt}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Constrói a estrutura de dados da tabela do relatório
        data = [[
            Paragraph("<b>Título</b>", table_header_style),
            Paragraph("<b>Solicitante</b>", table_header_style),
            Paragraph("<b>Categoria</b>", table_header_style),
            Paragraph("<b>Status</b>", table_header_style),
            Paragraph("<b>Prioridade</b>", table_header_style)
        ]]

        for t in chamados:
            data.append([
                Paragraph(str(t.titulo), table_cell_style),
                Paragraph(str(t.solicitante), table_cell_style),
                Paragraph(str(t.categoria), table_cell_style),
                Paragraph(str(t.status), table_cell_style),
                Paragraph(str(t.prioridade), table_cell_style)
            ])

        # Tratamento caso nenhum registro seja encontrado
        if len(data) == 1:
            data.append([
                Paragraph("Nenhum chamado encontrado com estes filtros.", table_cell_style),
                "", "", "", ""
            ])

        # Formatação e estilização visual da tabela (incluindo efeito zebra nas linhas)
        tabela = Table(data, colWidths=[160, 110, 90, 90, 82])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')), # Fundo índigo no cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]), # Alternância de cores nas linhas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')), # Linhas divisórias suaves
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))

        elements.append(tabela)

        # Função auxiliar para renderizar o rodapé dinâmico em cada página do PDF
        def add_footer(canvas_obj, doc_obj):
            canvas_obj.saveState()
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.setFillColor(colors.HexColor('#94a3b8'))
            canvas_obj.drawString(40, 20, "DeskFlow Helpdesk System — Documento Gerado Automaticamente")
            canvas_obj.drawRightString(letter[0] - 40, 20, f"Página {doc_obj.page}")
            canvas_obj.restoreState()

        # Compila e gera o arquivo PDF final no buffer de memória
        doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_gerencial_deskflow.pdf"'
        return response

    return render(request, 'tickets/admin_relatorios.html')