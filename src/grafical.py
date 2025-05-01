import numpy as np
import abc
import matplotlib.pyplot as plt
import matplotlib.colors as pltcolors

class ComplexFunction(abc.ABC):
    def __init__(self, resolution: int=500, real_range: tuple=(-1000, 1000), imag_range: tuple=(-1000, 1000)):
        self.resolution = resolution
        self.real_range = real_range
        self.imag_range = imag_range

    @staticmethod
    @abc.abstractmethod
    def f(s: complex) -> complex:
        pass

    @staticmethod
    def module(s: complex) -> complex:
        return np.abs(s)

    @staticmethod
    def phase(s: complex) -> complex:
        return np.angle(s)

    def plot_bode(self, cut: float=0.0) -> None:
        freq = np.linspace(self.imag_range[0], self.imag_range[1], self.resolution)
        full_domain = cut + 1j*freq

        f_jw = self.f(full_domain)

        plt.figure(figsize=(9.6, 10))

        plt.subplot(2, 1, 1)
        plt.ylabel("Module")
        plt.plot(freq, self.module(f_jw), color="black")

        plt.subplot(2, 1, 2)
        plt.ylabel("Phase")
        plt.xlabel("Frequency")
        plt.plot(freq, self.phase(f_jw), color="black")

        plt.show()

    def plot_laplace(self) -> None:
        real_domain = np.linspace(self.real_range[0], self.real_range[1], min(self.resolution, 50))
        freq = np.linspace(self.imag_range[0], self.imag_range[1], min(self.resolution, 50))
        real_part, imag_part = np.meshgrid(real_domain, freq)
        full_domain = real_part + 1j*imag_part

        f_s = self.f(full_domain)

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, figsize=(9.6, 10))

        norm = pltcolors.Normalize(vmin=-np.pi/2, vmax=np.pi/2)
        colors = plt.cm.Greys(norm(self.phase(f_s)))

        ax.plot_surface(real_part, imag_part, self.module(f_s), 
                        facecolors=colors, rstride=1, cstride=1, linewidth=0.1, antialiased=False)

        mappable = plt.cm.ScalarMappable(cmap='Greys', norm=norm)
        mappable.set_array([])

        cbar = fig.colorbar(mappable, ax=ax, shrink=0.5)
        cbar.set_ticks([-np.pi/2, 0, np.pi/2])
        cbar.set_ticklabels([r"$-\frac{\pi}{2}$", r"$0$", r"$\frac{\pi}{2}$"])

        ax.set_xlabel("Real part")
        ax.set_ylabel("Frequency")
        ax.set_zlabel("Module")

        plt.show()