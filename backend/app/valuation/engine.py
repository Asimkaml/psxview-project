"""Deterministic valuation engine scaffolding.

Phase 1 defines the interface; concrete sector-appropriate methods and
scenarios will be implemented in later phases.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ValuationInputs:
    company_id: int
    latest_eps: float
    discount_rate: float
    growth_rate: float


@dataclass
class ValuationOutputs:
    fair_value_bear: float
    fair_value_base: float
    fair_value_bull: float


class ValuationEngine:
    def value_company(self, inputs: ValuationInputs) -> ValuationOutputs:
        """Placeholder deterministic valuation method.

        The actual formula will be fleshed out in the valuation phase. For now
        we provide a simple, explicit and testable structure.
        """

        base = inputs.latest_eps * 10
        return ValuationOutputs(
            fair_value_bear=base * 0.8,
            fair_value_base=base,
            fair_value_bull=base * 1.2,
        )
