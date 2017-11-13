
import copy
from collections import OrderedDict
import ast

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
    
    def __init__(self, *args, **kwargs):
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
        self.validated_data = []
        BaseSerializer.__init__(self, *args, **kwargs)

    def get(self, condition={}, ignore_fields=[]):
        if not condition:
            res = self.picker.all()
        else:
            res = self.picker.filter(condition)
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

                
    def to_representation(self, res, ignore_fields):
        newdata = []
        for ires in res:
            tmp = {
                k:self.fields[k].to_representation(ires[k])
                for k in set(self.fields.keys()) - set(ignore_fields)
                }
            newdata.append(tmp)

        return newdata


class DCSerializer(Serializer):

    def __init__(self, picker, *args, **kwargs):
        Serializer.__init__(self, picker, *args, **kwargs)

    def to_representation(self, res, ignore_fields):
        newdata = []
        for ires in res:
            tmp = {
                self.underline_to_camel(k):self.fields[k].to_representation(getattr(ires, k))
                for k in set(self.fields.keys()) - set(ignore_fields)
                }
            newdata.append(tmp)

        return newdata

    def is_valid(self, data):
        errors = []
        validated_data = {}
        for fieldname, v in self.fields.items():
            k = self.underline_to_camel(fieldname)
            if k in data.keys():
                value = data[k]
            else:
                continue

            try:
                v.run_validators(value)
                validated_data[fieldname] = value
            except ValidationError as e:
                errors.append(e.msg)

        if not errors:
            self.validated_data.append(validated_data)
            return True
        else:
            raise ValidationError(errors)

    def validate(self,data):
        errors = []
        for fieldname, v in self.fields.items():
            k = self.underline_to_camel(fieldname)
            if k not in data.keys() and v.required:
                errors.append({k: v.error_messages['required']})

        if errors:
            raise ValidationError(errors)

    def is_valid_all(self, data):
        for idata in data:
            try:
                self.validate(idata)
                self.is_valid(idata)
            except ValidationError as e:
                self.errors.extend(e.msg)

        if not self.errors:
            return True
        else:
            return False

    def create(self):
        for idata in self.validated_data:
            if 'id' in idata.keys():
                idata.pop('id')
            idata['version'] = 0
            self.picker.save(idata)

    def update(self):
        for idata in self.validated_data:
            if 'id' not in idata.keys():
                continue
            res = self.picker.get({'id':idata['id']})
            res.version += 1
            for k in idata.keys():
                if k != 'id' or k != 'version':
                    setattr(res,k,idata[k])
            res.save()

    def delete(self, idlist):
        if isinstance(idlist, str):
            idlist = ast.literal_eval(idlist)
        errors = self.picker.delete(idlist)
        return errors

    @classmethod
    def underline_to_camel(cls,snake_str):
        """
        下划线命名转驼峰命名
        :param snake_str:
        :return:
        """
        components = snake_str.split('_')
        if '_' not in snake_str:
            return snake_str
        return components[0] + "".join(x.title() for x in components[1:])

    @classmethod
    def camel_to_underline(cls, field_name):
        """
        驼峰命名法转小写加下划线

        Role > role
        roleName > role_name
        RoleName > role_name
        _RoleName > __role_name
        role_name > role_name
        """
        return ''.join(
            [c.lower() if not c.isalpha() or c.islower() or (c.isupper() and idx == 0)
             else '_%c' % c.lower()
             for idx, c in enumerate(field_name)])


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

