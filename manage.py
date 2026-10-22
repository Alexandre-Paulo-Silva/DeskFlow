#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Define a variável de ambiente padrão que aponta para as configurações do projeto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        # Tenta importar o utilitário de execução de comandos do Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Lança uma exceção amigável caso o Django não esteja instalado ou o ambiente virtual não esteja ativo
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Executa os comandos passados via terminal (ex: runserver, migrate, etc.)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()