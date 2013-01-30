from datetime import datetime
import sqlalchemy as sa


DEFAULT_LAZY_OPTIONS = {
    'auto_now': True,
    'integer_defaults': True,
    'string_defaults': True,
    'boolean_defaults': True,
    'min_max_check_constraints': True,
    'enum_names': True
}


class Column(sa.Column):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('info', {})

        kwargs['info'].setdefault('choices', kwargs.pop('choices', None))
        kwargs['info'].setdefault('label', kwargs.pop('label', ''))
        kwargs['info'].setdefault('description', kwargs.pop('description', ''))
        kwargs['info'].setdefault('validators', kwargs.pop('validators', []))
        kwargs['info'].setdefault('min', kwargs.pop('min', None))
        kwargs['info'].setdefault('max', kwargs.pop('max', None))
        kwargs['info'].setdefault('auto_now', kwargs.pop('auto_now', False))

        # Make strings and booleans not nullable by default
        if args and (is_string(args[0]) or isinstance(args[0], sa.Boolean)):
            kwargs.setdefault('nullable', False)

        sa.Column.__init__(self, *args, **kwargs)

    @property
    def validators(self):
        return self.info['validators'] if 'validators' in self.info else []

    @property
    def label(self):
        return self.info['label'] if 'label' in self.info else ''

    @property
    def description(self):
        return self.info['description'] if 'description' in self.info else ''


class LazyConfigured(object):
    @classmethod
    def _get_lazy_option(cls, name):
        try:
            return cls.__lazy_options__[name]
        except (AttributeError, KeyError):
            return DEFAULT_LAZY_OPTIONS[name]


def append_check_constraints(table, column):
    """
    Generate check constraints based on min and max column info arguments
    """
    if 'min' in column.info and column.info['min'] is not None:
        constraint = sa.schema.CheckConstraint(
            '%s >= %d' % (column.name, column.info['min'])
        )
        table.append_constraint(constraint)
    if 'max' in column.info and column.info['max'] is not None:
        constraint = sa.schema.CheckConstraint(
            '%s <= %d' % (column.name, column.info['max'])
        )
        table.append_constraint(constraint)


def assign_datetime_auto_now(column):
    """
    Assigns datetime auto now defaults
    """
    if 'auto_now' in column.info and column.info['auto_now']:
        column.default = sa.schema.ColumnDefault(datetime.utcnow)
        column.server_default = sa.schema.DefaultClause(sa.func.now())


def assign_int_defaults(column):
    """
    Assigns int column server_default based on column default value
    """
    if column.default is not None:
        if (isinstance(column.default.arg, basestring) or
                isinstance(column.default.arg, int)):
            column.server_default = sa.schema.DefaultClause(
                str(column.default.arg)
            )


def assign_string_defaults(column):
    """
    Assigns string column server_default based on column default value
    """
    if column.default is not None:
        column.server_default = sa.schema.DefaultClause(column.default.arg)


def assign_boolean_defaults(column):
    """
    Assigns int column server_default based on column default value
    """
    column.nullable = False

    if column.default is None:
        column.default = sa.schema.ColumnDefault(False)

    if column.default is not None:
        if column.default.arg is False:
            column.server_default = sa.schema.DefaultClause(
                sa.sql.expression.false()
            )
        else:
            column.server_default = sa.schema.DefaultClause(
                sa.sql.expression.true()
            )


def is_string(type_):
    return (
        isinstance(type_, sa.Unicode) or
        isinstance(type_, sa.UnicodeText) or
        isinstance(type_, sa.String) or
        isinstance(type_, sa.Text) or
        type_ is sa.UnicodeText or
        type_ is sa.Text
    )


def is_integer(type_):
    return (
        isinstance(type_, sa.Integer) or
        isinstance(type_, sa.SmallInteger) or
        isinstance(type_, sa.BigInteger)
    )


def lazy_config_listener(mapper, class_):
    if issubclass(class_, LazyConfigured):
        table = class_.__table__
        for column in table.columns:
            if class_._get_lazy_option('min_max_check_constraints'):
                append_check_constraints(table, column)

            if (isinstance(column.type, sa.Boolean) and
                    class_._get_lazy_option('boolean_defaults')):
                assign_boolean_defaults(column)

            elif (is_string(column.type) and
                    class_._get_lazy_option('string_defaults')):
                assign_string_defaults(column)

            elif (is_integer(column.type) and
                    class_._get_lazy_option('integer_defaults')):
                assign_int_defaults(column)

            elif ((isinstance(column.type, sa.Date) or
                    isinstance(column.type, sa.DateTime)) and
                    class_._get_lazy_option('auto_now')):
                assign_datetime_auto_now(column)

            elif (isinstance(column.type, sa.Enum) and
                    class_._get_lazy_option('enum_names')):
                if not hasattr(column.type, 'name') or not column.type.name:
                    column.type.name = '%s_enum' % column.name
