# test/test_utils.py
from decimal import Decimal

# Supondo que você mova a função formatar_moeda para pipeline/utils.py
# from pipeline.utils import formatar_moeda


def formatar_moeda(valor: float | Decimal) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def test_formatar_moeda():
    assert formatar_moeda(1500.50) == "R$ 1.500,50"
    assert formatar_moeda(10) == "R$ 10,00"
