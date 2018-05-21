if __name__ == '__main__':
    import sys
    import os

    import django

    from django.core.management import call_command

    sys.path.append('gpstats')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'gpstats.settings'
    django.setup()

    call_command('flush', interactive=False)
    call_command('makemigrations', 'motogp')
    call_command('migrate', interactive=False)
    # call_command('runserver')
