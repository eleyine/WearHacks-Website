from django import template
import unicodedata

register = template.Library()

def stripaccents(value, arg=""):
    if type(value) == str:
        return value
    return ''.join((c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'))

register.filter("stripaccents", stripaccents)