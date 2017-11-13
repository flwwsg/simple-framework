
import copy
from collections import OrderedDict

from utils import BindingDict
from fields import CharField, Field, IntegerField
from orm_wrapper import DemoPicker
from validators import ValidationError

# get all fields 
class SerializerMetaclass(type):

    def __new__(cls, name, bases, attrs):

        fields = [
            (field_name, attrs.pop(field_name))
            for field_name, obj in list(attrs.items())
            if isinstance(obj, Field)
        ]

        attrs['_declared_fields'] = OrderedDict(fields)

        newclass = super(SerializerMetaclass, cls).__new__(cls, name, bases, attrs)
        declared_fields = OrderedDict()
        for base in reversed(newclass.__mro__):
            if hasattr(base, '_declared_fields'):
                declared_fields.update(base._declared_fields)

        newclass._declared_fields = declared_fields
        return newclass


# derived from django-rest-framework
class BaseSerializer(Field):
    
    def __init__(self, data, *args, **kwargs):
        self.initial_data = data

        super(BaseSerializer, self).__init__(*args, **kwargs)

    @property
    def fields(self):
        if not hasattr(self, '_fields'):
            self._fields = BindingDict(self)
            for key, value in self.get_fields().items():
                self._fields[key] = value
        return self._fields
    
    def get_fields(self):
        return copy.deepcopy(self._declared_fields)
    
    def __getitem__(self, name):
        """Return a bind with the given name."""
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key '%s' not found in '%s'. Choices are: %s." % (
                    name,
                    self.__class__.__name__,
                    ', '.join(sorted(f for f in self.fields)),
                )
            )

        return self._fields[name]


class Serializer(BaseSerializer, metaclass=SerializerMetaclass):
    
    def __init__(self, picker, *args, **kwargs):
        self.picker = picker
        self.errors = []
        self.validated_data = {}
        BaseSerializer.__init__(self, data, *args, **kwargs)

    def get(self, condition={}, ignore_fields=[]):
        if not condition:
            res = self.picker.all()
        else:
            res = self.picker.filter(condition)
        self.validate_fields(res[1])
        return self.to_representation(res, ignore_fields)

    def save(self, data):
        pass

    def is_valid(self, data):
        errors = []
        for k, v in self.fields.items():
            try:
                v.run_validators(data[k])
            except ValidationError as e:
                errors.append(e.msg)

        if not errors:
            self.validated_data = data
            return True
        else:
            self.errors = errors
            return False

    def create(self):
        self.picker.save(self.validated_data)

    def validate_fields(self, data):
        errors = []
        for k, v in self.fields.items():
            try:
                v.validate(data[k])
            except ValidationError as e:
                errors.append({k:e.msg})
        if errors:
            self.errors = errors
            raise ValidationError

                
    def to_representation(self, res, ignore_fields):
        newdata = []
        for ires in res:
            tmp = {
                k:self.fields[k].to_representation(ires[k]) 
                for k in set(self.fields.keys()) -set(ignore_fields)
                }
            newdata.append(tmp)

        return newdata
    

class FooSerializer(Serializer):
    id = IntegerField()    
    name = CharField()
        

if __name__ == '__main__':
    data = [(1, 'a'), (2, 'b'), (3,'c')]
    newdata = []
    for idata in data:
        tmp = {k:v for k, v in zip(('id', 'name'), idata)}
        newdata.append(tmp)

    dp = DemoPicker()
    foo = FooSerializer(dp)
    try:
        foo.get(ignore_fields=['id'])
        if foo.is_valid(newdata[0]):
            foo.create()
    except ValidationError:
        print(foo.errors)

