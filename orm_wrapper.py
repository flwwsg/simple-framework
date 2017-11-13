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

    def delete(self, idlist):
        '''
        :param idlist:
        :return:
        '''
        errors = []
        for idx in idlist:
            try:
                newidx = int(idx)
            except (ValueError, TypeError):
                errors.append(idx)
            res = self.adt.objects.get(id=newidx)
            if res:
                try:
                    res.delete()
                    print('==' * 80)
                    print('deleting id={}'.format(newidx))
                except Exception:
                    errors.append(idx)
            else:
                errors.append(idx)

        return errors






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


