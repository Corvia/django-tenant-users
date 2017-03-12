
from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'core/main.html'

