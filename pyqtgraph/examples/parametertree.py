"""
This example demonstrates the use of pyqtgraph's parametertree system. This provides
a simple way to generate user interfaces that control sets of parameters. The example
demonstrates a variety of different parameter types (int, float, list, etc.)
as well as some customized parameter types
"""

# `makeAllParamTypes` creates several parameters from a dictionary of config specs.
# This contains information about the options for each parameter so they can be directly
# inserted into the example parameter tree. To create your own parameters, simply follow
# the guidelines demonstrated by other parameters created here.
from _buildParamTypes import makeAllParamTypes

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

app = pg.mkQApp("Parameter Tree Example")
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, registerParameterType


## test subclassing parameters
## This parameter automatically generates two child parameters which are always reciprocals of each other
class ComplexParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'complexparam'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        
        self.addChild({'name': 'A = 1/B', 'type': 'float', 'value': 7, 'suffix': 'Hz', 'siPrefix': True})
        self.addChild({'name': 'B = 1/A', 'type': 'float', 'value': 1/7., 'suffix': 's', 'siPrefix': True})
        self.a = self.param('A = 1/B')
        self.b = self.param('B = 1/A')
        self.a.sigValueChanged.connect(self.aChanged)
        self.b.sigValueChanged.connect(self.bChanged)
        
    def aChanged(self):
        self.b.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)

    def bChanged(self):
        self.a.setValue(1.0 / self.b.value(), blockSignal=self.aChanged)

    def saveState(self, filter=None):
        # Unlike the normal GroupParameter, child states shouldn't be separately
        # preserved
        state = super().saveState(filter)
        state.pop("children", None)
        return state


## test add/remove
## this group includes a menu allowing the user to add new parameters into its child list
class ScalableGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'scalablegroup'
        opts['addText'] = "Add"
        opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)
    
    def addNew(self, typ):
        val = {
            'str': '',
            'float': 0.0,
            'int': 0
        }[typ]
        self.addChild(dict(name="ScalableParam %d" % (len(self.childs)+1), type=typ, value=val, removable=True, renamable=True))


all_params_types = makeAllParamTypes()

registerParameterType('complexparam', ComplexParameter)
registerParameterType('scalablegroup', ScalableGroup)

params = [
    all_params_types,
    {'name': 'Save/Restore functionality', 'type': 'group', 'children': [
        {'name': 'Save State', 'type': 'action'},
        {'name': 'Restore State', 'type': 'action', 'children': [
            {'name': 'Add missing items', 'type': 'bool', 'value': True},
            {'name': 'Remove extra items', 'type': 'bool', 'value': True},
        ]},
    ]},
    {'name': 'Custom context menu', 'type': 'group', 'children': [
        {'name': 'List contextMenu', 'type': 'float', 'value': 0, 'context': [
            'menu1',
            'menu2'
        ]},
        {'name': 'Dict contextMenu', 'type': 'float', 'value': 0, 'context': {
            'changeName': 'Title',
            'internal': 'What the user sees',
        }},
    ]},
    ComplexParameter(name='Custom parameter group (reciprocal values)'),
    ScalableGroup(name="Expandable Parameter Group", tip='Click to add children', children=[
        {'name': 'ScalableParam 1', 'type': 'str', 'value': "default param 1"},
        {'name': 'ScalableParam 2', 'type': 'str', 'value': "default param 2"},
    ]),
]

## Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

############################################################################
# TESTS
############################################################################

from timeit import default_timer as timer
import sys

from serializall.factory import SerializableFactory
from pyqtgraph.parametertree.utils import compare_parameters

enc = Parameter.to_json(p)
dec = Parameter.from_json(enc)

print(compare_parameters(p, dec))


# ser_factory = SerializableFactory()
# # ser_p = ser_factory.get_apply_serializer(p)
# # restored_p = ser_factory.get_apply_deserializer(ser_p)
#
#
# start = timer()
# state = p.saveState()
# res_json = json.dumps(state)
# restored = p.restoreState(json.loads(res_json))
# end = timer()
# json_time = end - start
# print(f'JSON: {json_time} seconds')
# print(f'JSON object size: {len(res_json)}')
#
# start = timer()
# res_binary = ser_factory.get_apply_serializer(p)
# restored = ser_factory.get_apply_deserializer(res_binary)
# end = timer()
# binary_time = end - start
# print(f'Binary: {binary_time} seconds')
# print(f'Binary object size: {len(res_binary)}')
#
# if json_time > binary_time:
#     print(f'Fastest: Binary')
# else:
#     print(f'Fastest: JSON')
#
#
# def get_leaf_list(param: Parameter) -> list:
#     leafs = list()
#
#     def get_leaf_rec(param: Parameter, leafs: list):
#         if not param.children():
#             leafs.append(param)
#         else:
#             for ch in param.children():
#                 get_leaf_rec(ch, leafs)
#
#     get_leaf_rec(param, leafs)
#
#     return leafs
#
# leafs = get_leaf_list(p)
#
# json_params = []
# errors_type = []
#
# for elt in leafs:
#     state = elt.saveState()
#     # print(f'{elt}: {state}')
#     # res = json.dumps(state)
#     # json_params.append(res)
#     try:
#         res = json.dumps(state)
#         json_params.append(res)
#         # print(f'{elt}: {res}\nSuccess')
#     except TypeError as e:
#         print(f'{elt}: {state}\nError: {e}')
#
# json_param = json.dumps(p.saveState())

# TODO Check if ser ndarray is ok + colormap linearize


############################################################################
# END TESTS
############################################################################

#
#
# ## If anything changes in the tree, print a message
# def change(param, changes):
#     print("tree changes:")
#     for param, change, data in changes:
#         path = p.childPath(param)
#         if path is not None:
#             childName = '.'.join(path)
#         else:
#             childName = param.name()
#         print('  parameter: %s'% childName)
#         print('  change:    %s'% change)
#         print('  data:      %s'% str(data))
#         print('  ----------')
#
# p.sigTreeStateChanged.connect(change)
#
#
# def valueChanging(param, value):
#     print("Value changing (not finalized): %s %s" % (param, value))
#
# # Only listen for changes of the 'widget' child:
# for child in p.child('Example Parameters'):
#     if 'widget' in child.names:
#         child.child('widget').sigValueChanging.connect(valueChanging)
#
# def save():
#     global state
#     state = p.saveState()
#
# def restore():
#     global state
#     add = p['Save/Restore functionality', 'Restore State', 'Add missing items']
#     rem = p['Save/Restore functionality', 'Restore State', 'Remove extra items']
#     p.restoreState(state, addChildren=add, removeChildren=rem)
# p.param('Save/Restore functionality', 'Save State').sigActivated.connect(save)
# p.param('Save/Restore functionality', 'Restore State').sigActivated.connect(restore)
#
#
# ## Create two ParameterTree widgets, both accessing the same data
# t = ParameterTree()
# t.setParameters(p, showTop=False)
# t.setWindowTitle('pyqtgraph example: Parameter Tree')
# t2 = ParameterTree()
# t2.setParameters(p, showTop=False)
#
# win = QtWidgets.QWidget()
# layout = QtWidgets.QGridLayout()
# win.setLayout(layout)
# layout.addWidget(QtWidgets.QLabel("These are two views of the same data. They should always display the same values."), 0,  0, 1, 2)
# layout.addWidget(t, 1, 0, 1, 1)
# layout.addWidget(t2, 1, 1, 1, 1)
# win.show()
#
# ## test save/restore
# state = p.saveState()
# p.restoreState(state)
# compareState = p.saveState()
# assert pg.eq(compareState, state)
#
#
# if __name__ == '__main__':
#     pg.exec()
