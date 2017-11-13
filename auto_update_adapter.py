
# //auto generate adapters 

import os
from core.utils.data_struct import underline_to_camel, camel_to_underline
import importlib
import inspect
import remote_api
import datetime

from remote_api.models.attributes import Attribute
from remote_api.models.attributes import IntegerField

#     with open(fname, 'w') as f:
#         f.write(tmpl)


root = os.path.dirname(os.path.abspath(__file__))

adt_path = os.path.join(root, 'adapters')
def_path = os.path.join(root, 'define')

def_names = []
adt_names = []

def_module = importlib.import_module('orm.define.character')

for mname, obj in inspect.getmembers(def_module):
    tmp = {}
    if inspect.isclass(obj) and obj.__name__[:2] == 'Tb':
        tmp['cls_name'] = mname
        tlist = []
        for mname, attr in inspect.getmembers(obj):
            if isinstance(attr, Attribute):
                tlist.append(mname)
        tmp['fields'] = tlist
        def_names.append(tmp)
        # print(attrs)
print(def_names)
# adt_c_path = os.path.join(adt_path, 'character')
# for adt in os.listdir(adt_c_path):
#     tpath = os.path.join(adt_c_path, adt)
#     if os.path.isfile(tpath) and adt[:4] == 'adt_':
#         adt_names.append(adt)

# req_names = ['_'.join(['adt', camel_to_underline(model_name[2:] + '.py')])
#              for model_name in def_names]

# added_names = set(req_names) - set(adt_names)
# del_names = set(adt_names) - set(req_names)

# # delete not exist adapters
# for name in del_names:
#     tpath = os.path.join(adt_c_path, name)
#     if os.path.exists(tpath):
#         os.remove(tpath)
#
# # add adapters
# for name in added_names:
#     components = name[4:-3].split('_')
#     classname = 'Tb'+"".join(x.title() for x in components)
#     fname = os.path.join(adt_c_path,name)
#     # adt_generator(getattr(def_module,classname), fname)
#
# # generating character_adt.py
# adt_character = os.path.join(adt_path, 'character_adt.py')
# if added_names or del_names or not os.path.exists(adt_character):
#     with open(adt_character, 'w') as f:
#         f.write('#autho generated.\n')
#         for mname in req_names:
#             f.write('from orm.adapters.character.%s import *\n' % mname[:-3])

# print('adding', added_names)
# print('deleting', del_names)
