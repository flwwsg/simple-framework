
import copy
from collections import OrderedDict

from utils import BindingDict
from fields import CharField, Field, IntegerField


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
        BaseSerializer.__init__(self, data, *args, **kwargs)

        # self.map_data()


    # def map_data(self):
    #     self.data = []
    #     for idata in self.initial_data:
    #         tmp = {k:v for k, v in zip(self.fields, idata)}
    #         self.data.append(tmp)
    

    
        


if __name__ == '__main__':
    class FooSerializer(Serializer):
        id = IntegerField(required=False)
        name = CharField()
    data = [(1, 'a'), (2, 'b'), (3,'c')]
    newdata = []
    for idata in data:
        tmp = {k:v for k, v in zip(('id', 'name'), idata)}
        newdata.append(tmp)
    

    foo = FooSerializer(newdata)
    print(foo.initial_data)

