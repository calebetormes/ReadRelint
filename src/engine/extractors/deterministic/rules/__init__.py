# -*- coding: utf-8 -*-
from src.engine.extractors.deterministic.rules.base_rule import IDeterministicRule
from src.engine.extractors.deterministic.rules.homicide_rule import HomicideDeterministicRule
from src.engine.extractors.deterministic.rules.drug_trafficking_rule import DrugTraffickingDeterministicRule

__all__ = [
    "IDeterministicRule",
    "HomicideDeterministicRule",
    "DrugTraffickingDeterministicRule",
]
