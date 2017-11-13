# -*- coding: utf-8 -*-  
"""  
 @date: 2017/11/11
 @author: wdj  

"""

class DataPicker(object):

    def __init__(self, adt):
        self.adt = adt

    def filter(self, condition):
        return self.adt.objects.filter(**condition)

    def all(self):
        return self.adt.objects.filter()

    def get(self, condition):
        return self.adt.objects.get(**condition)

    def save(self, data):
        return self.adt.objects.create(**data)



class DemoPicker(DataPicker):
    def __init__(self):
        pass

    def filter(self):
        return [{'id':1, 'name':'a'}, {'id':2, 'name':'b'}]

    def get(self):
        return {'id':1, 'name': 'a'}

    def all(self):
        return [{'id':1, 'name':'a'}, {'id':2, 'name':'b'}]

    def save(self, data):
        print('creating data:', data)
        return data


