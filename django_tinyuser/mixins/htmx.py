from abc import ABC


class HtmxMixin(ABC):
    """
    Mixin to provide HTMX support for views.
    """

    @property
    def is_htmx_request(self):
        """
        Checks if the current request is an HTMX request.

        :return: True if the current request is an HTMX request, False otherwise
        :rtype: bool
        """
        request = getattr(self, 'request', None)
        if request is None:
            return False
        return self.request.headers.get('Hx-Request') == 'true'
