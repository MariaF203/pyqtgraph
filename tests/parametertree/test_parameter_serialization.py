from pyqtgraph.parametertree import Parameter
from pyqtgraph.parametertree.utils import compare_parameters

from pyqtgraph.examples._buildParamTypes import makeAllParamTypes

from serializall.factory import SerializableFactory

ser_factory = SerializableFactory()

def test_all_param_ser_des():
    p = Parameter.create(name="params", type="group", children=[makeAllParamTypes()])
    serialized_p = ser_factory.get_apply_serializer(p)
    assert isinstance(serialized_p, bytes)
    p_back = ser_factory.get_apply_deserializer(serialized_p)
    assert compare_parameters(p, p_back)