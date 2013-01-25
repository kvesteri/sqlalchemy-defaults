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
    column.nullable = False

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


def lazy_config_listener(mapper, class_):
    if issubclass(class_, LazyConfigured):
        table = class_.__table__
        for column in table.columns:
            if class_._get_lazy_option('min_max_check_constraints'):
                append_check_constraints(table, column)

            if (isinstance(column.type, sa.Boolean) and
                    class_._get_lazy_option('boolean_defaults')):
                assign_boolean_defaults(column)

            elif ((isinstance(column.type, sa.Unicode) or
                    isinstance(column.type, sa.UnicodeText)) and
                    class_._get_lazy_option('string_defaults')):
                assign_string_defaults(column)

            elif ((isinstance(column.type, sa.Integer) or
                    isinstance(column.type, sa.SmallInteger) or
                    isinstance(column.type, sa.BigInteger)) and
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
