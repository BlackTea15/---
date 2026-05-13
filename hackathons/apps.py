import sys

from django.apps import AppConfig


class HackathonsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hackathons"

    def ready(self):
        # Django 5.1 + Python 3.14 compatibility:
        # BaseContext.__copy__ relies on copy(super()) which is broken on 3.14.
        if sys.version_info < (3, 14):
            return

        from django.template.context import BaseContext

        if getattr(BaseContext, "_py314_copy_patch", False):
            return

        def _base_context_copy(self):
            duplicate = self.__class__.__new__(self.__class__)
            attrs = getattr(self, "__dict__", None)
            if attrs is not None:
                duplicate.__dict__.update(attrs)
            duplicate.dicts = self.dicts[:]
            return duplicate

        BaseContext.__copy__ = _base_context_copy
        BaseContext._py314_copy_patch = True
