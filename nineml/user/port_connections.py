from . import BaseULObject
from abc import ABCMeta, abstractmethod
from nineml.xml import E, unprocessed_xml
from nineml.annotations import read_annotations, annotate_xml
from nineml.exceptions import (
    NineMLRuntimeError, NineMLMissingElementError, NineMLDimensionError)
from nineml.abstraction.ports import (
    AnalogSendPort, AnalogReceivePort, AnalogReducePort, EventSendPort,
    EventReceivePort)


class BasePortConnection(BaseULObject):

    __metaclass__ = ABCMeta

    defining_attributes = ('_sender_role', '_receiver_role',
                           '_send_port', '_receive_port',
                           '_sender_name', '_receiver_name')

    def __init__(self, send_port, receive_port,
                 sender_role=None, receiver_role=None,
                 sender_name=None, receiver_name=None):
        """
        `send_port`     -- The name of the sending port
        `receiver_port` -- The name of the receiving port
        `sender_role`   -- A reference to the sending object via the role it
                           plays in the container
        `receiver_role` -- A reference to the receiving object via the role it
                           plays in the container
        `sender_name`   -- A reference to the sending object via its name,
                           which uniquely identifies it within the container
        `receiver_name` -- A reference to the receiving object via its name,
                           which uniquely identifies it within the container
        """
        BaseULObject.__init__(self)
        self._send_port_name = send_port
        self._receive_port_name = receive_port
        if sender_role is not None:
            if sender_name is not None:
                raise NineMLRuntimeError(
                    "Both 'sender_role' ({}) and 'sender_name' ({}) cannot"
                    " be provided to PortConnection __init__"
                    .format(sender_role, sender_name))
        elif sender_name is None:
            raise NineMLRuntimeError(
                "Either 'sender_role' or 'sender_name' must be "
                "provided to PortConnection __init__")
        if receiver_role is not None:
            if receiver_name is not None:
                raise NineMLRuntimeError(
                    "Both 'receiver_role' ({}) and 'receiver_name' ({}) cannot"
                    " be provided to PortConnection __init__"
                    .format(receiver_role, receiver_name))
        elif receiver_name is None:
            raise NineMLRuntimeError(
                "Either 'receiver_role' or 'receiver_name' must be "
                "provided to PortConnection __init__")
        self._sender_role = sender_role
        self._sender_name = sender_name
        self._receiver_name = receiver_name
        self._receiver_role = receiver_role
        # Initialise members that will hold the connected objects once they are
        # bound
        self._sender = None
        self._receiver = None
        self._sender_dynamics = None
        self._receiver_dynamics = None
        self._send_port = None
        self._receive_port = None

    def __repr__(self):
        return ("{}(sender={}->{}, receiver={}->{})"
                .format(self.element_name,
                        (self.sender_name if self.sender_name is not None
                         else 'role:' + self.sender_role),
                        self.send_port_name,
                        (self.receiver_name if self.receiver_name is not None
                         else 'role:' + self.receiver_role),
                        self.receive_port_name))

    @property
    def name(self):
        return '_'.join((
            (self.sender_role if self._sender_role is not None
             else self.sender_name), self.send_port_name,
            (self.receiver_role if self._receiver_role is not None
             else self.receiver_name), self.receive_port_name))

    @property
    def sender(self):
        if self._sender is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._sender

    @property
    def receiver(self):
        if self._receiver is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._receiver

    @property
    def sender_dynamics(self):
        if self._sender_dynamics is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._sender_dynamics

    @property
    def receiver_dynamics(self):
        if self._receiver_dynamics is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._receiver_dynamics

    @property
    def send_port(self):
        if self._send_port is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._send_port

    @property
    def receive_port(self):
        if self._receive_port is None:
            raise NineMLRuntimeError("Ports have not been bound")
        return self._receive_port

    @property
    def send_port_name(self):
        if self._send_port is None:
            return self._send_port_name
        else:
            return self._send_port.name

    @property
    def receive_port_name(self):
        if self._receive_port is None:
            return self._receive_port_name
        else:
            return self._receive_port.name

    @property
    def sender_role(self):
        if self._sender_role is None:
            raise NineMLRuntimeError(
                "Sender object was not identified by its role")
        return self._sender_role

    @property
    def receiver_role(self):
        if self._receiver_role is None:
            raise NineMLRuntimeError(
                "Sender object was not identified by its role")
        return self._receiver_role

    @property
    def sender_name(self):
        if self._sender_name is None:
            raise NineMLRuntimeError(
                "Sender object was not identified by its name")
        return self._sender_name

    @property
    def receiver_name(self):
        if self._receiver_name is None:
            raise NineMLRuntimeError(
                "Sender object was not identified by its name")
        return self._receiver_name

    def bind(self, container, to_roles=False):
        """
        Binds the PortConnection to the components it is connecting
        """
        # If the sender and receiver should be identified by their role
        # i.e. pre, pos, response, plasticity, etc... or by name
        if to_roles:
            self._sender = getattr(container, self.sender_role)
            self._receiver = getattr(container, self.receiver_role)
        else:
            self._sender = container[self.sender_name]
            self._receiver = container[self.receiver_name]
        try:
            self._sender_dynamics = self._sender.cell.component_class
        except AttributeError:
            self._sender_dynamics = self._sender.component_class
        try:
            self._receiver_dynamics = self._receiver.cell.component_class
        except AttributeError:
            self._receiver_dynamics = self._receiver.component_class
        try:
            self._send_port = self._sender_dynamics.port(self.send_port_name)
        except KeyError:
            raise NineMLMissingElementError(
                "Could not bind '{}' send port to '{}' dynamics class in '{}'"
                .format(self.receive_port_name, self.sender_dynamics.name,
                        self.sender.name))
        try:
            self._receive_port = self._receiver_dynamics.port(
                self.receive_port_name)
        except KeyError:
            raise NineMLMissingElementError(
                "Could not bind '{}' receive port to '{}' dynamics class in "
                "'{}'".format(self.receive_port_name,
                              self.receiver_dynamics.name, self.receiver.name))
        self._check_ports()

    @annotate_xml
    def to_xml(self, document, **kwargs):  # @UnusedVariable
        attribs = {}
        try:
            attribs['sender_role'] = self.sender_role
        except NineMLRuntimeError:
            attribs['sender_name'] = self.sender_name
        try:
            attribs['receiver_role'] = self.receiver_role
        except NineMLRuntimeError:
            attribs['receiver_name'] = self.receiver_name
        return E(
            self.element_name,
            send_port=self.send_port_name, receive_port=self.receive_port_name,
            **attribs)

    @classmethod
    @read_annotations
    @unprocessed_xml
    def from_xml(cls, element, document, **kwargs):  # @UnusedVariable
        cls.check_tag(element)
        return cls(send_port=element.attrib['send_port'],
                   receive_port=element.attrib['receive_port'],
                   sender_role=element.get('sender_role', None),
                   receiver_role=element.get('receiver_role', None),
                   sender_name=element.get('sender_name', None),
                   receiver_name=element.get('receiver_name', None))

    @abstractmethod
    def _check_ports(self):
        pass

    @classmethod
    def from_tuple(cls, tple, container):
        sender, send_port, receiver, receive_port = tple
        init_kwargs = {}
        try:
            sender_dynamics = getattr(container, sender).component_class
            init_kwargs['sender_role'] = sender
        except AttributeError:
            sender_dynamics = container[sender].component_class
            init_kwargs['sender_name'] = sender
        try:
            getattr(container, receiver).component_class
            init_kwargs['receiver_role'] = receiver
        except AttributeError:
            container[receiver].component_class
            init_kwargs['receiver_name'] = receiver
        if isinstance(sender_dynamics.port(send_port), AnalogSendPort):
            port_connection = AnalogPortConnection(
                receive_port=receive_port, send_port=send_port, **init_kwargs)
        else:
            port_connection = EventPortConnection(
                receive_port=receive_port, send_port=send_port, **init_kwargs)
        return port_connection


class AnalogPortConnection(BasePortConnection):

    element_name = 'AnalogPortConnection'

    def _check_ports(self):
        if not isinstance(self.send_port, AnalogSendPort):
            raise NineMLRuntimeError(
                "Send port '{}' must be an AnalogSendPort to be connected with"
                " an AnalogPortConnection".format(self.send_port.name))
        if not isinstance(self.receive_port, (AnalogReceivePort,
                                              AnalogReducePort)):
            raise NineMLRuntimeError(
                "Send port '{}' must be an AnalogSendPort to be connected with"
                " an AnalogPortConnection".format(self.receive_port.name))
        if self.send_port.dimension != self.receive_port.dimension:
            raise NineMLDimensionError(
                "Dimensions do not matc in analog port connection: sender port"
                " '{}' has dimensions of '{}' and receive port '{}' has "
                "dimensions of '{}'"
                .format(self.send_port.name, self.send_port.dimension,
                        self.receive_port.name, self.receive_port.dimension))


class EventPortConnection(BasePortConnection):

    element_name = 'EventPortConnection'

    def _check_ports(self):
        if not isinstance(self.send_port, EventSendPort):
            raise NineMLRuntimeError(
                "Send port '{}' must be an EventSendPort to be connected with"
                " an EventPortConnection".format(self.send_port.name))
        if not isinstance(self.receive_port, EventReceivePort):
            raise NineMLRuntimeError(
                "Send port '{}' must be an EventSendPort to be connected with"
                " an EventPortConnection".format(self.receive_port.name))

    @property
    def delay(self):
        """
        Included for compatibility with code written in
        nineml.user.multi.component for future versions
        """
        return 0.0
