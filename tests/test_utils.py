"""Tests para el módulo utils."""

from src.utils.decorators import timed


def test_timed_decorator():
    """Verifica que el decorador @timed retorna el resultado correctamente."""

    @timed
    def suma(a: int, b: int) -> int:
        return a + b

    assert suma(2, 3) == 5
