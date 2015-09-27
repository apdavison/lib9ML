from itertools import chain
from .. import BaseULObject
from collections import defaultdict
from itertools import product, groupby, izip
from nineml.reference import resolve_reference, write_reference
from nineml import DocumentLevelObject
from nineml.xmlns import NINEML, E
from nineml.utils import expect_single
from nineml.user import DynamicsProperties
from nineml.annotations import annotate_xml, read_annotations
from nineml.exceptions import NineMLRuntimeError, NineMLMissingElementError
from ..port_connections import (
    AnalogPortConnection, EventPortConnection, BasePortConnection)
from nineml.abstraction import BaseALObject
from nineml.base import MemberContainerObject
from nineml.utils import ensure_valid_identifier
from nineml import units as un
from nineml.annotations import VALIDATE_DIMENSIONS
from nineml.abstraction import (
    Dynamics, Regime, AnalogReceivePort, AnalogReducePort, EventReceivePort,
    StateVariable, OnEvent, OnCondition, OutputEvent, StateAssignment)
from nineml.abstraction.dynamics.transitions import Transition
from .ports import (
    EventReceivePortExposure, EventSendPortExposure, AnalogReducePortExposure,
    AnalogReceivePortExposure, AnalogSendPortExposure, BasePortExposure,
    LocalReducePortConnections, LocalAnalogPortConnection)
from .namespace import (
    _NamespaceAlias, _NamespaceRegime, _NamespaceStateVariable,
    _NamespaceConstant, _NamespaceParameter, _NamespaceProperty,
    append_namespace, split_namespace, make_regime_name,
    make_delay_trigger_name)


class MultiDynamicsProperties(DynamicsProperties):

    element_name = "MultiDynamics"
    defining_attributes = ('_name', '_sub_component_properties',
                           '_port_exposures', '_port_connections')

    def __init__(self, name, sub_components, port_connections,
                 port_exposures=[]):
        if isinstance(sub_components, dict):
            sub_components = [
                SubDynamics(n, sc.component_class)
                for n, sc in sub_components.iteritems()]
        else:
            sub_components = [
                SubDynamics(sc.name, sc.component.component_class)
                for sc in sub_components]
        component_class = MultiDynamics(
            name + '_Dynamics', sub_components,
            port_exposures=port_exposures, port_connections=port_connections)
        super(MultiDynamicsProperties, self).__init__(
            name, definition=component_class,
            properties=chain(*[p.properties for p in sub_components]))
        self._sub_component_properties = dict(
            (p.name, p) for p in sub_components)

    @property
    def name(self):
        return self._name

    @property
    def sub_components(self):
        return self._sub_component_properties.itervalues()

    @property
    def port_connections(self):
        return iter(self._port_connections)

    @property
    def port_exposures(self):
        return self._port_exposures.itervalues()

    def sub_component(self, name):
        return self._sub_component_properties[name]

    def port_exposure(self, name):
        return self._port_exposures[name]

    @property
    def sub_component_names(self):
        return self.sub_component.iterkeys()

    @property
    def port_exposure_names(self):
        return self._port_exposures.iterkeys()

    @property
    def attributes_with_units(self):
        return chain(*[c.attributes_with_units
                       for c in self.sub_component])

    @write_reference
    @annotate_xml
    def to_xml(self, document, **kwargs):
        members = [c.to_xml(document, **kwargs)
                   for c in self.sub_component_properties]
        members.extend(pe.to_xml(document, **kwargs)
                        for pe in self.port_exposures)
        members.extend(pc.to_xml(document, **kwargs)
                       for pc in self.port_connections)
        return E(self.element_name, *members, name=self.name)

    @classmethod
    @resolve_reference
    @read_annotations
    def from_xml(cls, element, document, **kwargs):
        cls.check_tag(element)
        sub_component_properties = [
            SubDynamicsProperties.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'SubDynamics')]
        port_exposures = [
            AnalogSendPortExposure.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'AnalogSendPortExposure')]
        port_exposures.extend(
            AnalogReceivePortExposure.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'AnalogReceivePortExposure'))
        port_exposures.extend(
            AnalogReducePortExposure.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'AnalogReducePortExposure'))
        port_exposures.extend(
            EventSendPortExposure.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'EventSendPortExposure'))
        port_exposures.extend(
            EventReceivePortExposure.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'EventReceivePortExposure'))
        analog_port_connections = [
            AnalogPortConnection.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'AnalogPortConnection')]
        event_port_connections = [
            EventPortConnection.from_xml(e, document, **kwargs)
            for e in element.findall(NINEML + 'EventPortConnection')]
        return cls(name=element.attrib['name'],
                   sub_component_properties=sub_component_properties,
                   port_exposures=port_exposures,
                   port_connections=chain(analog_port_connections,
                                          event_port_connections))


class SubDynamicsProperties(BaseULObject):

    element_name = 'SubDynamicsProperties'
    defining_attributes = ('_name', '_dynamics')

    def __init__(self, name, component):
        BaseULObject.__init__(self)
        self._name = name
        self._component = component

    @property
    def name(self):
        return self._name

    @property
    def component(self):
        return self._component

    @property
    def properties(self):
        return (_NamespaceProperty(self, p)
                for p in self._component.properties)

    def __iter__(self):
        return self.properties

    @annotate_xml
    def to_xml(self, document, **kwargs):  # @UnusedVariable
        return E(self.element_name, self._component.to_xml(document, **kwargs),
                 name=self.name)

    @classmethod
    @read_annotations
    def from_xml(cls, element, document, **kwargs):
        try:
            dynamics_properties = DynamicsProperties.from_xml(
                expect_single(
                    element.findall(NINEML + 'DynamicsProperties')),
                document, **kwargs)
        except NineMLRuntimeError:
            dynamics_properties = MultiDynamicsProperties.from_xml(
                expect_single(
                    element.findall(NINEML + 'MultiDynamics')),
                document, **kwargs)
        return cls(element.attrib['name'], dynamics_properties)


class MultiDynamics(Dynamics):

    def __init__(self, name, sub_components, port_connections,
                 port_exposures=None, url=None, validate_dimensions=True):
        ensure_valid_identifier(name)
        self._name = name
        BaseALObject.__init__(self)
        DocumentLevelObject.__init__(self, url)
        MemberContainerObject.__init__(self)
        # =====================================================================
        # Create the structures unique to MultiDynamics
        # =====================================================================
        if isinstance(sub_components, dict):
            self._sub_components = dict(
                (name, SubDynamics(name, dyn))
                for name, dyn in sub_components.iteritems())
        else:
            self._sub_components = dict((d.name, d) for d in sub_components)
        self._analog_port_connections = {}
        self._zero_delay_event_port_connections = defaultdict(dict)
        self._nonzero_delay_event_port_connections = defaultdict(dict)
        self._reduce_port_connections = defaultdict(dict)
        # Insert an empty list for each event and reduce port in the combined
        # model
        # Parse port connections (from tuples if required), bind them to the
        # ports within the subcomponents and append them to their respective
        # member dictionaries
        for port_connection in port_connections:
            if isinstance(port_connection, tuple):
                port_connection = BasePortConnection.from_tuple(
                    port_connection, self)
            port_connection.bind(self)
            snd_key = (port_connection.sender_name,
                       port_connection.send_port_name)
            rcv_key = (port_connection.receiver_name,
                       port_connection.receive_port_name)
            if isinstance(port_connection.receive_port, AnalogReceivePort):
                if rcv_key in self._analog_port_connections:
                    raise NineMLRuntimeError(
                        "Multiple connections to receive port '{}' in '{} "
                        "sub-component of '{}'"
                        .format(port_connection.receive_port_name,
                                port_connection.receiver_name, name))
                port_connection = LocalAnalogPortConnection(
                    port_connection)
                self._analog_port_connections[rcv_key] = port_connection
            elif isinstance(port_connection.receive_port, EventReceivePort):
                if port_connection.delay:
                    self._nonzero_delay_event_port_connections[
                        snd_key][rcv_key] = port_connection
                else:
                    self._zero_delay_event_port_connections[
                        snd_key][rcv_key] = port_connection
            elif isinstance(port_connection.receive_port, AnalogReducePort):
                self._reduce_port_connections[
                    rcv_key][snd_key] = port_connection
            else:
                raise NineMLRuntimeError(
                    "Unrecognised port connection type '{}'"
                    .format(port_connection))
        # =====================================================================
        # Save port exposurs into separate member dictionaries
        # =====================================================================
        self._analog_send_port_exposures = {}
        self._analog_receive_port_exposures = {}
        self._analog_reduce_port_exposures = {}
        self._event_send_port_exposures = {}
        self._event_receive_port_exposures = {}
        if port_exposures is not None:
            for exposure in port_exposures:
                if isinstance(exposure, tuple):
                    exposure = BasePortExposure.from_tuple(exposure, self)
                exposure.bind(self)
                if isinstance(exposure, AnalogSendPortExposure):
                    self._analog_send_port_exposures[exposure.name] = exposure
                elif isinstance(exposure, AnalogReceivePortExposure):
                    self._analog_receive_port_exposures[
                        exposure.name] = exposure
                elif isinstance(exposure, AnalogReducePortExposure):
                    self._analog_reduce_port_exposures[
                        exposure.name] = exposure
                elif isinstance(exposure, EventSendPortExposure):
                    self._event_send_port_exposures[exposure.name] = exposure
                elif isinstance(exposure, EventSendPortExposure):
                    self._event_receive_port_exposures[
                        exposure.name] = exposure
                else:
                    raise NineMLRuntimeError(
                        "Unrecognised port exposure '{}'".format(exposure))
        self.annotations[NINEML][VALIDATE_DIMENSIONS] = validate_dimensions
        self.validate()

    def __getitem__(self, name):
        return self.sub_component(name)

    @property
    def sub_components(self):
        return self._sub_components.itervalues()

    @property
    def sub_component_names(self):
        return self._sub_components.iterkeys()

    @property
    def num_sub_components(self):
        return len(self._sub_components)

    @property
    def analog_port_connections(self):
        return self._analog_port_connections.itervalues()

    @property
    def event_port_connections(self):
        return chain(self.zero_delay_event_port_connections,
                     self.nonzero_delay_event_port_connecttions)

    @property
    def zero_delay_event_port_connections(self):
        return chain(*[
            d.itervalues()
            for d in self._zero_delay_event_port_connections.itervalues()])

    @property
    def nonzero_delay_event_port_connections(self):
        return chain(*[
            d.itervalues()
            for d in self._nonzero_delay_event_port_connections.itervalues()])

    @property
    def reduce_port_connections(self):
        return chain(*[d.itervalues()
                       for d in self._reduce_port_connections.itervalues()])

    @property
    def port_connections(self):
        return chain(self.analog_port_connections, self.event_port_connections,
                     self.reduce_port_connections)

    def sub_component(self, name):
        return self._sub_components[name]

    # =========================================================================
    # Dynamics members properties and accessors
    # =========================================================================

    @property
    def parameters(self):
        return chain(*[sc.parameters for sc in self.sub_components])

    @property
    def aliases(self):
        """
        Chains port connections to analog receive and reduce ports, which
        are treated simply as aliases in the flattened representation, with
        all aliases defined in the sub components
        """
        return chain(
            self.analog_port_connections,
            (LocalReducePortConnections(
                prt, rcv, self._reduce_port_connections[(prt, rcv)])
             for prt, rcv in self._reduce_port_connections.iterkeys()),
            *[sc.aliases for sc in self.sub_components])

    @property
    def constants(self):
        return chain(*[sc.constants for sc in self.sub_components])

    @property
    def state_variables(self):
        # All statevariables in all subcomponents mapped into the container
        # namespace, plus state variables used to trigger local event
        # connections after a delays
        return chain((StateVariable(make_delay_trigger_name(pc),
                                    dimension=un.time)
                      for pc in self.nonzero_delay_event_port_connections),
                     *[(_NamespaceStateVariable(sc, sv)
                        for sv in sc.state_variables)
                       for sc in self.sub_components])

    @property
    def regimes(self):
        # Create multi-regimes for each combination of regimes across the
        # sub components
        combinations = product(*[sc.regimes for sc in self.sub_components])
        return (
            _MultiRegime(comb, self._event_send_port_exposures,
                         self._event_receive_port_exposures,
                         self._event_port_connections)
            for comb in combinations)

    @property
    def analog_send_ports(self):
        """Returns an iterator over the local |AnalogSendPort| objects"""
        return self._analog_send_port_exposures.itervalues()

    @property
    def analog_receive_ports(self):
        """Returns an iterator over the local |AnalogReceivePort| objects"""
        return self._analog_receive_port_exposures.itervalues()

    @property
    def analog_reduce_ports(self):
        """Returns an iterator over the local |AnalogReducePort| objects"""
        return self._analog_reduce_port_exposures.itervalues()

    @property
    def event_send_ports(self):
        """Returns an iterator over the local |EventSendPort| objects"""
        return self._event_send_port_exposures.itervalues()

    @property
    def event_receive_ports(self):
        """Returns an iterator over the local |EventReceivePort| objects"""
        return self._event_receive_port_exposures.itervalues()

    @property
    def parameter_names(self):
        return (p.name for p in self.parameters)

    @property
    def alias_names(self):
        return (a.name for a in self.aliases)

    @property
    def constant_names(self):
        return (c.name for c in self.constants)

    @property
    def state_variable_names(self):
        return (sv.name for sv in self.state_variables)

    @property
    def analog_send_port_names(self):
        """Returns an iterator over the local |AnalogSendPort| names"""
        return self._analog_send_port_exposures.iterkeys()

    @property
    def analog_receive_port_names(self):
        """Returns an iterator over the local |AnalogReceivePort| names"""
        return self._analog_receive_port_exposures.iterkeys()

    @property
    def analog_reduce_port_names(self):
        """Returns an iterator over the local |AnalogReducePort| names"""
        return self._analog_reduce_port_exposures.iterkeys()

    @property
    def event_send_port_names(self):
        """Returns an iterator over the local |EventSendPort| names"""
        return self._event_send_port_exposures.iterkeys()

    @property
    def event_receive_port_names(self):
        """Returns an iterator over the local |EventReceivePort| names"""
        return self._event_receive_port_exposures.iterkeys()

    def parameter(self, name):
        name, comp_name = split_namespace(name)
        return self.sub_component(comp_name).component_class.parameter(name)

    def state_variable(self, name):
        name, comp_name = split_namespace(name)
        component_class = self.sub_component(comp_name).component_class
        return component_class.state_variable(name)

    def alias(self, name):
        try:
            alias = self._analog_port_connections[name]
        except KeyError:
            try:
                alias = self._reduce_port_connections[name]
            except KeyError:
                name, comp_name = split_namespace(name)
                component_class = self.sub_component(comp_name).component_class
                alias = component_class.alias(name)
        return alias

    def constant(self, name):
        name, comp_name = split_namespace(name)
        return self.sub_component(comp_name).component_class.constant(name)

    def analog_send_port(self, name):
        return self._analog_send_port_exposures[name]

    def analog_receive_port(self, name):
        return self._analog_receive_port_exposures[name]

    def analog_reduce_port(self, name):
        return self._analog_reduce_port_exposures[name]

    def event_send_port(self, name):
        return self._event_send_port_exposures[name]

    def event_receive_port(self, name):
        return self._event_receive_port_exposures[name]

    @property
    def num_parameters(self):
        return len(list(self.parameters))

    @property
    def num_aliases(self):
        return len(list(self.aliases))

    @property
    def num_constants(self):
        return len(list(self.constants))

    @property
    def num_state_variables(self):
        return len(list(self.state_variables))

    @property
    def num_analog_send_ports(self):
        """Returns an iterator over the local |AnalogSendPort| objects"""
        return len(self._analog_send_port_exposures)

    @property
    def num_analog_receive_ports(self):
        """Returns an iterator over the local |AnalogReceivePort| objects"""
        return len(self._analog_receive_port_exposures)

    @property
    def num_analog_reduce_ports(self):
        """Returns an iterator over the local |AnalogReducePort| objects"""
        return len(self._analog_reduce_port_exposures)

    @property
    def num_event_send_ports(self):
        """Returns an iterator over the local |EventSendPort| objects"""
        return len(self._event_send_port_exposures)

    @property
    def num_event_receive_ports(self):
        """Returns an iterator over the local |EventReceivePort| objects"""
        return len(self._event_receive_port_exposures)

    def lookup_member_dict(self, element):
        """
        Looks up the appropriate member dictionary for objects of type element
        """
        dct_name = self.lookup_member_dict_name(element)
        comp_name = split_namespace(element._name)[1]
        return getattr(self.sub_component[comp_name], dct_name)

    @property
    def all_member_dicts(self):
        return chain(
            *[(getattr(sc.component, n)
               for n in sc.component.class_to_member_dict.itervalues())
              for sc in self.sub_components])


class SubDynamics(object):

    def __init__(self, name, component_class):
        self._name = name
        self._component_class = component_class

    @property
    def name(self):
        return self._name

    def append_namespace(self, name):
        return append_namespace(name, self.name)

    @property
    def component_class(self):
        return self._component_class

    @property
    def parameters(self):
        return (_NamespaceParameter(self, p)
                for p in self.component_class.parameters)

    @property
    def aliases(self):
        return (_NamespaceAlias(self, a) for a in self.component_class.aliases)

    @property
    def state_variables(self):
        return (_NamespaceStateVariable(self, v)
                for v in self.component.state_variables)

    @property
    def constants(self):
        return (_NamespaceConstant(self, p)
                for p in self.component_class.constants)

    @property
    def regimes(self):
        return (_NamespaceRegime(self, r)
                for r in self.component_class.regimes)


# =============================================================================
# _Namespace wrapper objects, which append namespaces to their names and
# expressions
# =============================================================================


class _MultiRegime(Regime):

    def __init__(self, sub_regimes, parent):
        """
        `sub_regimes_dict`       -- a dictionary containing the sub_regimes and
                                    referenced by the names of the
                                    sub_components they respond to
        `event_send_port_exposures`    -- reference to the event send port
                                          exposures in the MultiDynamics
        `event_receive_port_exposures` -- reference to the event receive port
                                          exposures in the MultiDynamics
        `event_port_connections` -- reference to the event send port
                                    connections in the MultiDynamics
        """
        self._sub_regimes = dict((r.component.name, r) for r in sub_regimes)
        self._parent = parent

    @property
    def sub_regimes(self):
        return self._sub_regimes.itervalues()

    @property
    def sub_components(self):
        return self._sub_regimes.iterkeys()

    @property
    def num_sub_regimes(self):
        return len(self._sub_regimes)

    def sub_regime(self, sub_component):
        return self._sub_regimes[sub_component]

    @property
    def _name(self):
        return make_regime_name(self._sub_regimes)

    def lookup_member_dict(self, element):
        """
        Looks up the appropriate member dictionary for objects of type element
        """
        dct_name = self.lookup_member_dict_name(element)
        comp_name = MultiDynamics.split_namespace(element._name)[1]
        return getattr(self.sub_regime(comp_name), dct_name)

    @property
    def all_member_dicts(self):
        return chain(*[
            (getattr(r, n) for n in r.class_to_member_dict.itervalues())
            for r in self.sub_regimes])

    # Member Properties:
    # ------------------

    @property
    def time_derivatives(self):
        return chain(*[r.time_derivatives for r in self.sub_regimes])

    @property
    def aliases(self):
        return chain(*[r.aliases for r in self.sub_regimes])

    @property
    def on_events(self):
        """
        All OnEvents in sub_regimes that are exposed via an event receive
        port exposure
        """
        # Zip together all on events with their EventReceivePortExposures,
        # if present
        # NB: izip will return an empty list if there is no exposure for the
        #     on event port or a list of length 1 (containing a tuple of the
        #     port exposure and the on event that listens to it if there is)
        #     these lists are then chained to form a list of 2-tuples (ie. not
        #     a list of lists) containing port exposure and on event pairs
        exposed_on_events = chain(*[
            izip((pe for pe in self.parent._event_receive_port_exposures
                  if oe.port is pe.port), (oe,))
            for oe in self._all_sub_on_events])
        # Group on events by their port exposure and return as an _MultiOnEvent
        key = lambda tple: tple[0]
        return (
            _MultiOnEvent(prt, self.with_daisy_chained(grp), self)
            for prt, grp in groupby(sorted(exposed_on_events, key=key),
                                    key=key))

    @property
    def _all_sub_on_events(self):
        return chain(*[r.on_events for r in self.sub_regimes])

    @property
    def on_conditions(self):
        """
        All conditions across all sub-regimes sorted, grouped by their trigger
        and chained output-event -> on-events
        """
        # Group on conditions by their trigger condition and return as an
        # _MultiOnCondition
        all_on_conds = chain(*[r.on_conditions for r in self.sub_regimes])
        key = lambda oc: oc.trigger  # Group key for on conditions
        return (
            _MultiOnCondition(tr, self.with_daisy_chained(grp), self)
            for tr, grp in groupby(sorted(all_on_conds, key=key), key=key))

    def time_derivative(self, variable):
        name, comp_name = split_namespace(variable)
        return self.sub_regime(comp_name).time_derivative(name)

    def alias(self, name):
        name, comp_name = split_namespace(name)
        return self.sub_regime(comp_name).alias(name)

    def on_event(self, port_name):
        raise NotImplementedError

    def on_condition(self, condition):
        raise NotImplementedError

    @property
    def time_derivative_variables(self):
        return (td.variable for td in self.time_derivatives)

    @property
    def alias_names(self):
        return (a.name for a in self.aliases)

    @property
    def on_event_port_names(self):
        return (oe.src_port_name for oe in self.on_events)

    @property
    def on_condition_triggers(self):
        return (oc.trigger for oc in self.on_conditions)

    @property
    def num_time_derivatives(self):
        return len(list(self.time_derivatives))

    @property
    def num_on_events(self):
        return len(list(self.on_events))

    @property
    def num_on_conditions(self):
        return len(list(self.on_conditions))

    @property
    def num_aliases(self):
        return len(list(self.aliases))

    def with_daisy_chained(self, sub_on_events):
        """
        Yields a sub-OnEvent (i.e. an OnEvent in a sub-regime) along with
        all the other sub-OnEvents that are daisy-chained with it via event
        event port connections with zero delay.
        """
        if isinstance(sub_on_events, Transition):
            sub_on_events = (sub_on_events,)  # wrap single transition in tuple
        for sub_on_event in sub_on_events:
            yield sub_on_event  # Yield the sub event at the start of the chain
            # Loop through all its output events and yield any daisy chained
            # events
            for output_event in sub_on_event.output_events:
                # Get all receive ports that are activated by this output event
                # i.e. all zero-delay event port connections that are linked to
                # this output_event
                active_ports = set(
                    pc.receive_port for pc in
                    self.parent._zero_delay_event_port_connections[
                        (output_event.sub_component.name, output_event.name)])
                # Get all the OnEvent transitions that are connected to this
                for on_event in self._all_sub_on_events:
                    if on_event.port in active_ports:
                        for chained_event in self.with_daisy_chained(on_event):
                            yield chained_event


class _MultiTransition(object):
    """
    Collects multiple simultaneous transitions into a single transition
    """

    def __init__(self, sub_transitions, parent):
        self._sub_transitions = dict((t.sub_component.name, t)
                                     for t in sub_transitions)
        if len(self._sub_transitions) != len(sub_transitions):
            raise NineMLRuntimeError(
                "Transition loop with non-zero delay found in transitions: {}"
                .format(", ".join(t._name for t in sub_transitions)))
        self._parent = parent

    @property
    def target_regime(self):
        raise NotImplementedError

    @property
    def target_regime_name(self):
        raise NotImplementedError

    @property
    def sub_transitions(self):
        return self._sub_transitions

    def sub_transition(self, sub_component):
        return next(t for t in self._sub_transitions
                    if t.sub_component is sub_component)

    @property
    def sub_transition_namespaces(self):
        return self._sub_transitions.iterkeys()

    @property
    def state_assignments(self):
        # All state assignments within the sub_transitions plus
        # state-assignments of delay triggers for output events connected to
        # local event port connections with non-zero delay
        return chain(
            (StateAssignment(make_delay_trigger_name(pc),
                             't + {}'.format(pc.delay))
             for pc in self.parent.parent._nonzero_delay_event_port.connections
             if pc.port in self._all_output_event_ports),
            *[t.state_assignments for t in self.sub_transitions])

    @property
    def output_events(self):
        # Return all output events that are exposed by port exposures
        return (
            _ExposedOutputEvent(pe)
            for pe in self.parent.parent._event_send_port_exposures
            if pe.port in self._all_output_event_ports)

    def state_assignment(self, variable):
        try:
            next(sa for sa in self.state_assignments
                 if sa.variable == variable)
        except StopIteration:
            raise NineMLMissingElementError(
                "No state assignment for variable '{}' found in transition"
                .format(variable))

    def output_event(self, name):
        exposure = self.parent.parent._event_send_port_exposures[name]
        if exposure.port not in self._all_output_event_ports:
            raise NineMLMissingElementError(
                "Output event for '{}' port is not present in transition"
                .format(name))
        return _ExposedOutputEvent(exposure)

    @property
    def num_state_assignments(self):
        return len(list(self.state_assignments))

    @property
    def num_output_events(self):
        return len(list(self.output_events))

    @property
    def _all_output_event_ports(self):
        return set(oe.port for oe in chain(
            *[t.output_events for t in self.sub_transitions]))


class _MultiOnEvent(_MultiTransition, OnEvent):

    def __init__(self, src_port_name, sub_transitions):
        _MultiTransition.__init__(self, sub_transitions)
        self._src_port_name = src_port_name

    @property
    def src_port_name(self):
        return self._src_port_name


class _MultiOnCondition(_MultiTransition, OnCondition):

    def __init__(self, trigger, sub_transitions):
        _MultiTransition.__init__(self, sub_transitions)
        self._trigger = trigger

    @property
    def trigger(self):
        return self._trigger


class _ExposedOutputEvent(OutputEvent):

    def __init__(self, port_exposure):
        self._port_exposure = port_exposure

    @property
    def _name(self):
        return self._port_exposure.name
