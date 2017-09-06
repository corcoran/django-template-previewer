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
                    raise(FixError, "Cyclical inheritance in %s" % template)
                try:
                    context.update(fixes[ancestor])
                except KeyError:
                    raise(FixError, "You are trying to inherit from a fixture that does not exist: %s" % ancestor)
        context.update(our_fixes)
        for x in special:
            try:
                del context[x]
            except KeyError:
                pass
    return context


def merge(a, b, path=None, update=True):
    "http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge"
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx, val in enumerate(b[key]):
                    a[key][idx] = merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
            elif update:
                a[key] = b[key]
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


class MockDataTemplateView(TemplateView):
    extra_context = None

    def get_template_names(self):
        return self.kwargs.get('template_name', self.template_name)

    def get_context_data(self, **kwargs):
        context = super(MockDataTemplateView, self).get_context_data(**kwargs)
        context = merge(merge((get_fixes(open(settings.TEMPLATE_FIX), self.get_template_names())), context),
                        self.extra_context or {})
        return context
