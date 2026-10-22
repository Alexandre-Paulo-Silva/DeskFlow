from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

# Documento embutido (Embedded Document) para armazenar os comentários dentro do próprio documento do ticket no MongoDB
class Comentario(EmbeddedDocument):
    autor = fields.StringField(required=True, max_length=100) # Nome do usuário que escreveu o comentário
    mensagem = fields.StringField(required=True)               # Conteúdo da mensagem/resposta
    criado_em = fields.DateTimeField(default=datetime.now)     # Data e hora exata da criação do comentário

# Documento principal (Document) representando um Chamado/Ticket no banco NoSQL MongoDB
class Ticket(Document):
    # Opções permitidas para o status do chamado
    STATUS_CHOICES = (
        ('ABERTO', 'Aberto'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('RESOLVIDO', 'Resolvido'),
        ('FECHADO', 'Fechado')
    )

    # Opções permitidas para o nível de prioridade
    PRIORIDADE_CHOICES = (
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica')
    )

    # Opções permitidas para a categoria do problema
    CATEGORIA_CHOICES = (
        ('TI', 'Suporte Técnico / T.I.'),
        ('FINANCEIRO', 'Financeiro'),
        ('RH', 'Recursos Humanos'),
        ('INFRA', 'Infraestrutura / Suporte Geral'),
        ('HARDWARE', 'Hardware'),
        ('SOFTWARE', 'Software'),
        ('REDE', 'Rede / Internet'),
        ('OUTROS', 'Outros')
    )

    # Campos principais de texto do chamado
    titulo = fields.StringField(required=True, max_length=200) # Título resumido
    descricao = fields.StringField(required=True)              # Descrição detalhada do problema
    
    # Referências a usuários (salvamos o username do Django para mapeamento)
    solicitante = fields.StringField(required=True, max_length=100)                    # Usuário que criou o ticket
    tecnico_responsavel = fields.StringField(max_length=100, default=None, null=True) # Técnico que assumiu o chamado

    # Campos de seleção baseados nas tuplas de escolhas acima
    categoria = fields.StringField(choices=CATEGORIA_CHOICES, default='TI')
    prioridade = fields.StringField(choices=PRIORIDADE_CHOICES, default='MEDIA')
    status = fields.StringField(choices=STATUS_CHOICES, default='ABERTO')
    
    # Campo para armazenar o caminho ou URL da imagem/arquivo anexado ao chamado
    anexo = fields.StringField(default=None, null=True)
    
    # Lista embutida contendo os comentários vinculados a este ticket
    comentarios = fields.EmbeddedDocumentListField(Comentario)
    
    # Datas de controle de criação e atualização
    criado_em = fields.DateTimeField(default=datetime.now)
    atualizado_em = fields.DateTimeField(default=datetime.now)

    # Metadados de configuração do MongoEngine para a coleção
    meta = {
        'collection': 'tickets',       # Nome da coleção no MongoDB
        'ordering': ['-criado_em']     # Ordenação padrão decrescente (mais recentes primeiro)
    }

    # Representação em string do objeto Ticket
    def __str__(self):
        return f"[{self.status}] {self.titulo}"