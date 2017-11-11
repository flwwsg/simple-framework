
import itertools
import re
import datetime
import json

from validators import ValidationError
from validators import EMPTY_VALUES


class Field(object):
    
    default_validator = []
    empty_values = list(EMPTY_VALUES)
    default_error_messages = {
        'required': 'this field is required',
    }

    def __init__(self, required=True, validators=(), error_messages={}, source=None, label=None):
        self.required = required
        self.validators = list(itertools.chain(self.default_validator, validators))
        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.source = source
        self.label = label
        self.parent = None

    def validate(self,value):
        if value in self.empty_values and self.required:
            raise ValidationError(self.error_messages['required'], code='required')

    def run_validators(self, value):
        if value in self.empty_values:
            return 
        errors = []
        for v in self.validators:
            try:
                v(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.append(e.message)
        if errors:
            raise ValidationError

    def bind(self, field_name, parent):
        assert self.source != field_name, (
            "It is redundant to specify `source='%s'` on field '%s' in "
            "serializer '%s', because it is the same as the field name. "
            "Remove the `source` keyword argument." %
            (field_name, self.__class__.__name__, parent.__class__.__name__)
        )

        self.field_name = field_name
        self.parent = parent
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()
        
        if self.source is None:
            self.source = field_name
        
        # self.source_attrs is a list of attributes that need to be looked up
        # when serializing the instance, or populating the validated data.
        if self.source == '*':
            self.source_attrs = []
        else:
            self.source_attrs = self.source.split('.')




    def to_python(self, value):
        return value


class CharField(Field):
    '''
    represent a string
    '''

    def __init__(self, strip=True, empty_value='', **kwargs):
        self.strip = strip
        self.empty_value = empty_value
        Field.__init__(self, **kwargs)
    
    def to_python(self, value):
        '''
        return a string 
        '''
        if value not in self.empty_values:
            value = str(value)
            if self.strip:
                value = value.strip()
        if value in self.empty_values:
            return self.empty_value
        return value


class IntegerField(Field):
    default_error_messages = {
        'invalid': 'Enter a whole number.',
    }

    def __init__(self, **kwargs):
        Field.__init__(self, **kwargs)


    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None
            
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value

class DateTimeField(Field):
    
    default_error_messages = {
        'invalid': 'Enter a valid date.',
    }

    def __init__(self, inpu_formats=None, **kwargs):
        Field.__init__(**kwargs)
        if not inpu_formats:
            self.inpu_formats = inpu_formats

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format)

class JSONField(Field):
    default_error_messages = {
        'invalid': 'value must be valid JSON'
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            value = json.loads(value)    
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value



if __name__ == '__main__':
    name = CharField()
