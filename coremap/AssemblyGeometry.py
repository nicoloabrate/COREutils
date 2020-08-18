################################
#  _   _ ______ __  __  ____   #
# | \ | |  ____|  \/  |/ __ \  #
# |  \| | |__  | \  / | |  | | #
# | . ` |  __| | |\/| | |  | | #
# | |\  | |____| |  | | |__| | #
# |_| \_|______|_|  |_|\____/  #
#                              #
################################
# Author: N. Abrate
# File: AssemblyGeometry.py
# Description: This file contains classes for some typical assembly geometries
# in a nuclear fission reactor


class AssemblyHex:
    """
    This class defines operations on a hexagonal assembly
        Parameters:
    =========== INPUT
    pitch: float
        Assembly pitch inside the core
    =========== OUTPUT

    """

    def __init__(self, pitch):

        # by definition of pitch between two hexagonal assemblies
        self.apothema = pitch/2
        self.edge = 2*self.apothema/3**0.5
        self.area = 3*(3**0.5)/2*self.edge**2
        self.perimeter = 6*self.edge
        self.type = "H"
        self.numedges = 6

    def compute_volume(self, height):
        self.height = height  # assign height property
        self.volume = self.area*self.height  # compute volume


class AssemblySqr:
    """
    This class defines operations on a squared assembly
    ===========
    pitch: float
        Assembly pitch inside the core
    """

    def __init__(self, pitch):
        # by definition of pitch between two squared assemblies
        self.edge = pitch
        self.area = self.edge**2
        self.perimeter = 4*self.edge
        self.type = "S"
        self.numedges = 4

    def compute_volume(self, height):
        volume = self.area*height  # compute volume
        return volume


if __name__ == "__main__":
    P = 1.386  # working example
    assembly = AssemblyHex(P)
    print(assembly.area)
