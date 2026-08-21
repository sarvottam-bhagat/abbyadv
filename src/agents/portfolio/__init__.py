"""Compatibility alias for EquityNav's portfolio-agent slot.

AbbyAdv uses case_workspace as the domain name; this package keeps the
reference tree familiar for integrations migrating from EquityNav.
"""
from src.agents.case_workspace.case_agent import CaseWorkspaceAgent as PortfolioAgent

