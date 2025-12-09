import json
from json import JSONEncoder, JSONDecoder
import numpy as np
from ..Qt.QtGui import QColor

from .parameterTypes.colormap import ColorMap
from Parameter import Parameter
import pyqtgraph as pg

def get_classes(p: Parameter) -> list:
    """
    Get the classes of all the elements of a Parameter in a list.

    Parameters
    ----------
    p: Parameter
    The parameter from which the classes are going to be extracted.

    Returns
    -------
    list: A list containing a tree structure with the classes of each parameter elements.
    """
    return [p.__class__, [get_classes(c) for c in p.children()]]

def compare_parameters(p1: Parameter, p2: Parameter) -> bool:
    """
    Compare two Parameters.
    Compare the states of the parameters, then recursively compare the class of each parameter's element.

    Parameters
    ----------
    p1: Parameter
    The first parameter to compare.

    p2: Parameter
    The second parameter to compare.

    Returns
    -------
    bool: Return True if both parameters are equal, return False otherwise.

    See Also
    --------
    pg.eq, get_classes
    """
    p1_state = p1.saveState()
    p2_state = p2.saveState()

    if not pg.eq(p1_state, p2_state):
        return False

    return get_classes(p1) == get_classes(p2)


class JsonEncoderDecoder(JSONEncoder):
    def default(self, o):

        if isinstance(o, np.ndarray):
            return dict({'__ndarray__': o.tolist()})

        if isinstance(o, ColorMap):
            attrs = dict()
            attrs['pos'] = json.dumps(o.pos, cls=JsonEncoderDecoder)
            attrs['color'] = o.color
            attrs['mapping_mode'] = o.mapping_mode
            attrs['name'] = o.name
            attrs['stopsCache'] = o.stopsCache

            return dict({'__colormap__': attrs})

        return super().default(o)

    def encode(self, o):
        def hint_special(o):
            if isinstance(o, tuple):
                return dict({'__tuple__': [hint_special(e) for e in o]})
            elif isinstance(o, list):
                return [hint_special(e) for e in o]
            elif isinstance(o, dict):
                return {k: hint_special(v) for k,v in o.items()}
            else:
                return o

        return super(JsonEncoderDecoder, self).encode(hint_special(o))

    @staticmethod
    def decode_hook(dct):
        if '__ndarray__' in dct:
            return np.array(dct['__ndarray__'])

        if '__colormap__' in dct:
            elt = dct['__colormap__']
            rgba_color = []
            for c in elt['color']:
                rgba_color.append(QColor.fromRgbF(*c))

            return ColorMap(pos=JSONDecoder(object_hook=JsonEncoderDecoder.decode_hook).decode(elt['pos']),
                            color=rgba_color, mapping=elt['mapping_mode'], name=elt['name'])

        if '__tuple__' in dct:
            return tuple(dct['__tuple__'])

        return dct

    @staticmethod
    def json_encode(o) -> str:
        enc = JsonEncoderDecoder()
        return enc.encode(o)

    @staticmethod
    def json_decode(json_str: str) -> dict:
        return JSONDecoder(object_hook=JsonEncoderDecoder.decode_hook).decode(json_str)