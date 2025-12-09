import warnings
from collections import OrderedDict
import numpy as np

from ... import functions as fn
from ...Qt import QtWidgets
from ..Parameter import Parameter
from .basetypes import WidgetParameterItem

PARAM_NAMES = {}

class ListParameterItem(WidgetParameterItem):
    """
    WidgetParameterItem subclass providing comboBox that lets the user select from a list of options.

    """
    def __init__(self, param, depth):
        self.targetValue = None
        WidgetParameterItem.__init__(self, param, depth)

    def makeWidget(self):
        w = QtWidgets.QComboBox()
        w.setMaximumHeight(20)  ## set to match height of spin box and line edit
        w.sigChanged = w.currentIndexChanged
        w.value = self.value
        w.setValue = self.setValue
        self.widget = w  ## needs to be set before limits are changed
        self.limitsChanged(self.param, self.param.opts['limits'])
        if len(self.forward) > 0 and self.param.hasValue():
            self.setValue(self.param.value())
        return w

    def value(self):
        key = self.widget.currentText()

        return self.forward.get(key, None)

    def setValue(self, val):
        self.targetValue = val
        match = [fn.eq(val, limVal) for limVal in self.reverse[0]]
        if not any(match):
            self.widget.setCurrentIndex(0)
        else:
            idx = match.index(True)
            key = self.reverse[1][idx]
            ind = self.widget.findText(key)
            self.widget.setCurrentIndex(ind)

    def limitsChanged(self, param, limits):
        # set up forward / reverse mappings for name:value

        if len(limits) == 0:
            limits = ['']  ## Can never have an empty list--there is always at least a singhe blank item.

        self.forward, self.reverse = ListParameter.mapping(limits)
        try:
            self.widget.blockSignals(True)
            val = self.targetValue

            self.widget.clear()
            for k in self.forward:
                self.widget.addItem(k)
                if k == val:
                    self.widget.setCurrentIndex(self.widget.count()-1)
                    self.updateDisplayLabel()
        finally:
            self.widget.blockSignals(False)

    def updateDisplayLabel(self, value=None):
        if value is None:
            value = self.widget.currentText()
        super().updateDisplayLabel(value)


class ListParameter(Parameter):
    """Parameter with a list of acceptable values.

    By default, this parameter is represtented by a :class:`ListParameterItem`,
    displaying a combo box to select a value from the list.

    In addition to the generic :class:`~pyqtgraph.parametertree.Parameter`
    options, this parameter type accepts a ``limits`` argument specifying the
    list of allowed values.

    The values may generally be of any data type, as long as they can be
    represented as a string. If the string representation provided is
    undesirable, the values may be given as a dictionary mapping the desired
    string representation to the value.
    """

    itemClass = ListParameterItem

    def __init__(self, **opts):
        self.forward = OrderedDict()  ## {name: value, ...}
        self.reverse = ([], [])       ## ([value, ...], [name, ...])
        if 'values' in opts:
            warning = "ListParameter 'values' argument has been replaced with 'limits' and will be removed in a future version."
            warnings.warn(warning, DeprecationWarning)
            opts['limits'] = opts.pop('values')
        if opts.get('limits', None) is None:
            opts['limits'] = []
        Parameter.__init__(self, **opts)
        self.setLimits(opts['limits'])

    def setLimits(self, limits):
        """Change the list of allowed values."""
        self.forward, self.reverse = self.mapping(limits)

        Parameter.setLimits(self, limits)
        if self.hasValue():
            # 'value in limits' expression will break when reverse contains numpy array
            curVal = self.value()
            if len(self.reverse[0]) > 0 and not any(fn.eq(curVal, limVal) for limVal in self.reverse[0]):
                self.setValue(self.reverse[0][0])

    @staticmethod
    def mapping(limits):
        # Return forward and reverse mapping objects given a limit specification
        forward = OrderedDict()  ## {name: value, ...}
        reverse = ([], [])       ## ([value, ...], [name, ...])
        if not isinstance(limits, dict):
            limits = {str(l): l for l in limits}
        for k, v in limits.items():
            forward[k] = v
            reverse[0].append(v)
            reverse[1].append(k)
        return forward, reverse

    # def saveState(self, filter=None):
    #     """
    #     Return a structure representing the entire state of the parameter tree.
    #     The tree state may be restored from this structure using restoreState().
    #
    #     If *filter* is set to 'user', then only user-settable data will be included in the
    #     returned state.
    #     """
    #     if filter is None:
    #         state = self.opts.copy()
    #
    #         # TODO comment
    #         if 'limits' in state and isinstance(state['limits'], dict):
    #             limits = state['limits']
    #             try:
    #                 for k in limits.keys():
    #                     if isinstance(limits[k], np.ndarray):
    #                         limits[k] = limits[k].tolist()
    #             except ValueError:
    #                 pass
    #
    #         if state['type'] is None:
    #             global PARAM_NAMES
    #             state['type'] = PARAM_NAMES.get(type(self), None)
    #     elif filter == 'user':
    #         if self.hasValue():
    #             state = {'value': self.value()}
    #         else:
    #             state = {}
    #     else:
    #         raise ValueError(f"Unrecognized filter argument: '{filter}'")
    #
    #     ch = OrderedDict([(ch.name(), ch.saveState(filter=filter)) for ch in self])
    #     if len(ch) > 0:
    #         state['children'] = ch
    #     return state
    #
    # def restoreState(self, state, recursive=True, addChildren=True, removeChildren=True, blockSignals=True):
    #     """
    #     Restore the state of this parameter and its children from a structure generated using saveState()
    #     If recursive is True, then attempt to restore the state of child parameters as well.
    #     If addChildren is True, then any children which are referenced in the state object will be
    #     created if they do not already exist.
    #     If removeChildren is True, then any children which are not referenced in the state object will
    #     be removed.
    #     If blockSignals is True, no signals will be emitted until the tree has been completely restored.
    #     This prevents signal handlers from responding to a partially-rebuilt network.
    #     """
    #     state = state.copy()
    #
    #     # TODO comment
    #     if 'limits' in state and isinstance(state['limits'], dict):
    #         limits = state['limits']
    #         for k,v in limits:
    #             if isinstance(v, np.ndarray):
    #                 limits[k] = np.array(v)
    #
    #     childState = state.pop('children', [])
    #
    #     ## list of children may be stored either as list or dict.
    #     if isinstance(childState, dict):
    #         cs = []
    #         for k, v in childState.items():
    #             cs.append(v.copy())
    #             cs[-1].setdefault('name', k)
    #         childState = cs
    #
    #     if blockSignals:
    #         self.blockTreeChangeSignal()
    #
    #     try:
    #         self.setOpts(**state)
    #
    #         if not recursive:
    #             return
    #
    #         ptr = 0  ## pointer to first child that has not been restored yet
    #         foundChilds = set()
    #
    #         for ch in childState:
    #             name = ch['name']
    #             # typ = ch.get('type', None)
    #             # print('child: %s, %s' % (self.name()+'.'+name, typ))
    #
    #             ## First, see if there is already a child with this name
    #             gotChild = False
    #             for i, ch2 in enumerate(self.childs[ptr:]):
    #                 # print "  ", ch2.name(), ch2.type()
    #                 if ch2.name() != name:  # or not ch2.isType(typ):
    #                     continue
    #                 gotChild = True
    #                 # print "    found it"
    #                 if i != 0:  ## move parameter to next position
    #                     # self.removeChild(ch2)
    #                     self.insertChild(ptr, ch2)
    #                     # print "  moved to position", ptr
    #                 ch2.restoreState(ch, recursive=recursive, addChildren=addChildren, removeChildren=removeChildren)
    #                 foundChilds.add(ch2)
    #
    #                 break
    #
    #             if not gotChild:
    #                 if not addChildren:
    #                     # print "  ignored child"
    #                     continue
    #                 # print "    created new"
    #                 ch2 = Parameter.create(**ch)
    #                 self.insertChild(ptr, ch2)
    #                 foundChilds.add(ch2)
    #
    #             ptr += 1
    #
    #         if removeChildren:
    #             for ch in self.childs[:]:
    #                 if ch not in foundChilds:
    #                     # print "  remove:", ch
    #                     self.removeChild(ch)
    #     finally:
    #         if blockSignals:
    #             self.unblockTreeChangeSignal()
