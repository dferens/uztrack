from django_tables2.columns.base import library
from django_tables2.columns.linkcolumn import LinkColumn


@library.register
class FixedLinkColumn(LinkColumn):
    """
    Default :class:`LinkColumn` does not allow to specify custom link text,
    and when it can't get value by accessor it just fails silently.
    """
    def __init__(self, *args, **kwargs):
        self.link_text = kwargs.pop('text', None)
        kwargs['empty_values'] = ()
        super(FixedLinkColumn, self).__init__(*args, **kwargs)

    def render(self, value, record, bound_column):
        if self.link_text is not None:
            value = self.link_text
        return super(FixedLinkColumn, self).render(value, record, bound_column)
