import typing
import abc
import numpy as np
import pandas as pd

class Componente:

    @abc.abstractmethod
    def corrente(self, s: complex) -> complex:
        pass

    @abc.abstractmethod
    def estampa(self, matriz: np.ndarray) -> None:
        pass

class Resistor(Componente):

    def __init__(self, positivo: int, negativo: int, resistencia: float):
        self.positivo: int = positivo
        self.negativo: int = negativo
        self.resistencia: float = resistencia

    def corrente(self, s: complex) -> complex:
        return s/self.resistencia

    def estampa(self, matriz: np.ndarray) -> None:
        matriz[self.negativo, self.negativo] += 1/self.resistencia
        matriz[self.positivo, self.negativo] -= 1/self.resistencia
        matriz[self.negativo, self.positivo] -= 1/self.resistencia
        matriz[self.positivo, self.positivo] += 1/self.resistencia

class Circuito:

    def __init__(self) -> None:
        self.matriz: np.ndarray
        self.componentes: typing.List[Componente]
        self.numero_de_nos: int
        self.voltagens: typing.List[complex]

    def add_componente(componente: Componente) -> None:
        pass

    def remove_componente(id: int) -> None:
        pass

    def solve(terra: int) -> None:
        pass

    def componente_info(id: int) -> pd.Series:
        pass

    def transfer_function(entrada: typing.Tuple[int, int], 
                        saída: typing.Tuple[int, int]) \
                        -> typing.Callable[[complex], complex]:
        pass