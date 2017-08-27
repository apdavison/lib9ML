"""
docstring needed

:copyright: Copyright 2010-2013 by the Python lib9ML team, see AUTHORS.
:license: BSD-3, see LICENSE for details.
"""

from ....componentclass.visitors.validators.types import (
    TypesComponentValidator)
from ..base import BaseConnectionRuleVisitor
from ...base import ConnectionRule


class TypesConnectionRuleValidator(TypesComponentValidator,
                                   BaseConnectionRuleVisitor):

    def action_connectionrule(self, connectionrule, **kwargs):  # @UnusedVariable @IgnorePep8
        assert isinstance(connectionrule, ConnectionRule)
