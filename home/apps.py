from django.apps import AppConfig
from django.db.utils import OperationalError

class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        from .models import MerchandiseCategory
        try:
            default_categories = [
                "Skateboards",
                "Longboards",
                "Rollerblades",
                "Gears",
                "Scooters",
                "Accessories",
                "Apparel",
            ]
            for name in default_categories:
                MerchandiseCategory.objects.get_or_create(name=name)
        except OperationalError:
            # Happens on first migrate or database isn't ready
            pass



