# Create your views here.
from django.views.generic import TemplateView
from django.conf import settings
import yaml

special = ['_extends']


class FixError(Exception):
    pass


def get_fixes(the_yaml, template):
    """
    Return a dictionary populated from the_yaml (which may be anything
    that yaml.load will accept).
    """
    fixes = yaml.load(the_yaml)
    context = {}
    try:
        our_fixes = fixes[template]
    except (KeyError, TypeError):
        return context
    else:
        try:
            inheritance_list = our_fixes['_extends']
        except KeyError:
            pass
        else:

            if isinstance(inheritance_list, (unicode, str)):
                inheritance_list = [inheritance_list]
            for ancestor in inheritance_list:
                if ancestor == template:
                    raise FixError, "Cyclical inheritance in %s" % template
                try:
                    context.update(fixes[ancestor])
                except KeyError:
                    raise FixError, "You are trying to inherit from a fixture that does not exist: %s" % ancestor
        context.update(our_fixes)
        for x in special:
            try:
                del context[x]
            except KeyError:
                pass
    return context


class MockDataTemplateView(TemplateView):
    def get_template_names(self):
        return self.kwargs.get('template_name', self.template_name)

    def get_context_data(self, **kwargs):
        context = super(MockDataTemplateView, self).get_context_data(**kwargs)
        context.update(get_fixes(open(settings.TEMPLATE_FIX), self.get_template_names()))
        return context
