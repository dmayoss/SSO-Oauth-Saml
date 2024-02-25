from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    # connecting signals
    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals

        # Explicitly connect a signal handler.
        # named_receiver.connect(signals.receiver_function)
