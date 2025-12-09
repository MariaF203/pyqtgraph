from pyqtgraph.parametertree.utils import compare_parameters
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter

class ScalableGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts['type'] = 'group' #issue: hide the real subclass
        opts['addText'] = "Add"
        opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {
            'str': '',
            'float': 0.0,
            'int': 0
        }[typ]
        self.addChild(
            dict(name="ScalableParam %d" % (len(self.childs) + 1), type=typ, value=val, removable=True, renamable=True))


p = ScalableGroup(name='Scalable parameter group')
p_state = p.saveState()
restored_p = Parameter.create(**p_state)

print(p) # <ScalableGroup 'Scalable parameter group' at 0x7eaee1b0e3f0>
print(restored_p) # <GroupParameter 'Scalable parameter group' at 0x75061b256030> <= wrong class

print(compare_parameters(p, restored_p)) # False <= should be True