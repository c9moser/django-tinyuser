from django import template
from logging import getLogger

register = template.Library()
logger = getLogger('django.' + __name__)


@register.filter('tinyuser_template')
def tinyuser_template(template_name):
    """
    Template tag to retrieve the template path for a given template name.

    :param template_name: The name of the template to retrieve.
    :type template_name: str
    :return: The path to the template.
    :rtype: str
    """
    from django_tinyuser.settings import TEMPLATE_MAPPING
    try:
        return TEMPLATE_MAPPING[template_name]
    except KeyError:
        logger.error(f"Template path for '{template_name}' not found. Returning empty string.")
    return TEMPLATE_MAPPING.get(template_name, '')
