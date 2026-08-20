import pytest
from src.engine.rules.drug_trafficking_rule import DrugTraffickingRule
from src.engine.rules.vehicle_robbery_rule import VehicleRobberyRule
from src.engine.rules.vehicle_theft_rule import VehicleTheftRule
from src.engine.rules.pedestrian_robbery_rule import PedestrianRobberyRule
from src.engine.rules.residence_robbery_rule import ResidenceRobberyRule
from src.engine.rules.establishment_robbery_rule import EstablishmentRobberyRule

def test_drug_trafficking_rule():
    rule = DrugTraffickingRule()
    
    # matches_filter
    assert rule.matches_filter("Prisão por tráfico de drogas") is True
    assert rule.matches_filter("Apreensão de entorpecentes") is True
    assert rule.matches_filter("Roubo de celular") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "tráfico de drogas", "drogas": "maconha"}) is True
    assert rule.validate_qa_results({"natureza": "porte de entorpecente", "drogas": "sim"}) is True
    assert rule.validate_qa_results({"natureza": "roubo", "drogas": "nenhuma"}) is False

def test_vehicle_robbery_rule():
    rule = VehicleRobberyRule()
    
    # matches_filter (requires "roubo" AND vehicle type)
    assert rule.matches_filter("Ocorreu um roubo de carro na via") is True
    assert rule.matches_filter("Assalto seguido de roubo de veículo") is True
    assert rule.matches_filter("Roubo de celular") is False
    assert rule.matches_filter("Furto de carro") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "roubo", "objeto": "carro"}) is True
    assert rule.validate_qa_results({"natureza": "assalto", "objeto": "motocicleta"}) is True
    assert rule.validate_qa_results({"natureza": "furto", "objeto": "carro"}) is False
    assert rule.validate_qa_results({"natureza": "roubo", "objeto": "celular"}) is False

def test_vehicle_theft_rule():
    rule = VehicleTheftRule()
    
    # matches_filter (requires "furto" AND vehicle type)
    assert rule.matches_filter("Ocorreu um furto de carro") is True
    assert rule.matches_filter("Furto de veículo na madrugada") is True
    assert rule.matches_filter("Roubo e furto de carro") is True # Não há exclusão explícita de roubo no matches_filter
    assert rule.matches_filter("Furto de celular") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "furto", "objeto": "carro"}) is True
    assert rule.validate_qa_results({"natureza": "roubo", "objeto": "carro"}) is False
    assert rule.validate_qa_results({"natureza": "furto", "objeto": "celular"}) is False

def test_pedestrian_robbery_rule():
    rule = PedestrianRobberyRule()
    
    # matches_filter (requires "roubo" and pedestrian context)
    assert rule.matches_filter("Roubo a transeunte na rua") is True
    assert rule.matches_filter("Assalto a pedestre") is False # O matches_filter atual exige a palavra 'roubo' explicitamente
    assert rule.matches_filter("Roubo de carro") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "roubo a transeunte"}) is True
    assert rule.validate_qa_results({"natureza": "assalto a pedestre"}) is True
    assert rule.validate_qa_results({"natureza": "roubo de veículo"}) is False

def test_residence_robbery_rule():
    rule = ResidenceRobberyRule()
    
    # matches_filter
    assert rule.matches_filter("Roubo a residência") is True
    assert rule.matches_filter("Assalto em casa") is False # Exige palavra roubo
    assert rule.matches_filter("Roubo de veículo") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "roubo a residência"}) is True
    assert rule.validate_qa_results({"natureza": "assalto a casa"}) is True
    assert rule.validate_qa_results({"natureza": "furto a residência"}) is False

def test_establishment_robbery_rule():
    rule = EstablishmentRobberyRule()
    
    # matches_filter
    assert rule.matches_filter("Roubo a estabelecimento comercial") is True
    assert rule.matches_filter("Assalto a loja") is False # Exige palavra roubo
    assert rule.matches_filter("Roubo de pedestre") is False
    
    # validate_qa_results
    assert rule.validate_qa_results({"natureza": "roubo a estabelecimento"}) is True
    assert rule.validate_qa_results({"natureza": "assalto a comércio"}) is True
    assert rule.validate_qa_results({"natureza": "furto a loja"}) is False
