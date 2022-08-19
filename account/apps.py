from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'modules.main.account'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))

# myapp/__init__.py
