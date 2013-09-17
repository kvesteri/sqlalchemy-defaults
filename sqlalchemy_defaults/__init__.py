from datetime import datetime
from inspect import isclass
import six
import sqlalchemy as sa


__version__ = '0.3.0'


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
        kwargs['info'].setdefault(
            'form_field_class',
            kwargs.pop('form_field_class', None)
        )

        # Make strings and booleans not nullable by default
        if args:
            if (
                any([bool_or_str(arg) for arg in args[0:2]]) or
                ('type' in kwargs and bool_or_str(kwargs['type']))
            ):
                kwargs.setdefault('nullable', False)

        sa.Column.__init__(self, *args, **kwargs)

    @property
    def choices(self):
        return self.info['choices'] if 'choices' in self.info else []

    @property
    def validators(self):
        return self.info['validators'] if 'validators' in self.info else []

    @property
    def label(self):
        return self.info['label'] if 'label' in self.info else ''

    @property
    def description(self):
        return self.info['description'] if 'description' in self.info else ''


class ConfigurationManager(object):
    DEFAULT_OPTIONS = {
        'auto_now': True,
        'integer_defaults': True,
        'string_defaults': True,
        'boolean_defaults': True,
        'min_max_check_constraints': True,
        'enum_names': True,
        'index_foreign_keys': True
    }

    def __call__(self, mapper, class_):
        if hasattr(class_, '__lazy_options__'):
            configurator = ModelConfigurator(self, class_)
            configurator()


class ModelConfigurator(object):
    def __init__(self, manager, model):
        self.manager = manager
        self.model = model
        self.table = self.model.__table__

    def get_option(self, name):
        try:
            return self.model.__lazy_options__[name]
        except (AttributeError, KeyError):
            return self.manager.DEFAULT_OPTIONS[name]

    def append_check_constraints(self, column):
        """
        Generate check constraints based on min and max column info arguments
        """
        if 'min' in column.info and column.info['min'] is not None:
            constraint = sa.schema.CheckConstraint(
                '%s >= %d' % (column.name, column.info['min'])
            )
            self.table.append_constraint(constraint)
        if 'max' in column.info and column.info['max'] is not None:
            constraint = sa.schema.CheckConstraint(
                '%s <= %d' % (column.name, column.info['max'])
            )
            self.table.append_constraint(constraint)

    def assign_foreign_key_indexes(self, column):
        """
        Assign index for column if column has foreign key constraints.
        """
        if column.foreign_keys:
            column.index = True

    def assign_datetime_auto_now(self, column):
        """
        Assigns datetime auto now defaults
        """
        if 'auto_now' in column.info and column.info['auto_now']:
            column.default = sa.schema.ColumnDefault(datetime.utcnow)
            column.server_default = sa.schema.DefaultClause(sa.func.now())

    def assign_int_defaults(self, column):
        """
        Assigns int column server_default based on column default value
        """
        if column.default is not None:
            if (isinstance(column.default.arg, six.text_type) or
                    isinstance(column.default.arg, six.integer_types)):
                column.server_default = sa.schema.DefaultClause(
                    six.text_type(column.default.arg)
                )

    def assign_string_defaults(self, column):
        """
        Assigns string column server_default based on column default value
        """
        if column.default is not None and (
            isinstance(column.default.arg, six.text_type)
        ):
            column.server_default = sa.schema.DefaultClause(
                column.default.arg
            )

    def assign_boolean_defaults(self, column):
        """
        Assigns int column server_default based on column default value
        """
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

    def assign_type_defaults(self, column):
        if (isinstance(column.type, sa.Boolean) and
                self.get_option('boolean_defaults')):
            self.assign_boolean_defaults(column)

        elif (is_string(column.type) and self.get_option('string_defaults')):
            self.assign_string_defaults(column)

        elif (is_integer(column.type) and self.get_option('integer_defaults')):
            self.assign_int_defaults(column)

        elif ((isinstance(column.type, sa.Date) or
                isinstance(column.type, sa.DateTime))
                and self.get_option('auto_now')):
            self.assign_datetime_auto_now(column)

        elif (isinstance(column.type, sa.Enum) and
                self.get_option('enum_names')):
            if (not hasattr(column.type, 'name') or not
                    column.type.name):
                column.type.name = '%s_enum' % column.name

    def __call__(self):
        for column in self.table.columns:
            if self.get_option('min_max_check_constraints'):
                self.append_check_constraints(column)

            if self.get_option('index_foreign_keys'):
                self.assign_foreign_key_indexes(column)
            self.assign_type_defaults(column)


def bool_or_str(type_):
    return is_string(type_) or is_boolean(type_)


def is_string(type_):
    return (
        isinstance(type_, sa.String) or
        (isclass(type_) and issubclass(type_, sa.String))
    )


def is_boolean(type_):
    return (
        isinstance(type_, sa.Boolean) or
        (isclass(type_) and issubclass(type_, sa.Boolean))
    )


def is_integer(type_):
    return (
        isinstance(type_, sa.Integer) or
        (isclass(type_) and issubclass(type_, sa.Integer))
    )


def make_lazy_configured(mapper):
    manager = ConfigurationManager()
    sa.event.listen(
        mapper,
        'mapper_configured',
        manager
    )
