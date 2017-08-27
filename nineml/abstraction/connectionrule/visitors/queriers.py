from ...componentclass.visitors.queriers import (
    ComponentRequiredDefinitions, ComponentClassInterfaceInferer,
    ComponentElementFinder, ComponentExpressionExtractor,
    ComponentDimensionResolver)
from .base import BaseConnectionRuleVisitor


class ConnectionRuleInterfaceInferer(ComponentClassInterfaceInferer,
                                     BaseConnectionRuleVisitor):

    """
    Not extended from base classes currently, just mixes in the connectionrule-
    specific action visitor to the component-class interface inferer.
    """
    pass


class ConnectionRuleRequiredDefinitions(ComponentRequiredDefinitions,
                                        BaseConnectionRuleVisitor):
    pass


class ConnectionRuleElementFinder(ComponentElementFinder,
                                  BaseConnectionRuleVisitor):

    def action_connectionrule(self, connectionrule, **kwargs):  # @UnusedVariable @IgnorePep8
        return self.action_componentclass(connectionrule, **kwargs)


class ConnectionRuleExpressionExtractor(ComponentExpressionExtractor,
                                        BaseConnectionRuleVisitor):
    pass


class ConnectionRuleDimensionResolver(ComponentDimensionResolver,
                                      BaseConnectionRuleVisitor):
    pass
