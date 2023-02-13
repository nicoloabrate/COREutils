class LeadProp():
    """Lead thermo-physical properties, provided by:
    `Handbook on Lead-bismuth Eutectic Alloy and Lead Properties, Materials
    Compatibility, Thermal-hydraulics and Technologies
    2007 Edition
    Chapter 2: Thermophysical and Electric Properties
    Section 2.10.1 (pag. 52)`

    """
    @staticmethod
    def density(T):
        """ Density.

        Parameters
        ----------
        T : float or list
            Fluid temperature in [K]

        Returns
        -------
        density: float
            Specific heat in [kg/m3]
        """
        return 11367-1.1944*T

    @staticmethod
    def specific_heat(T):
        """ Specific heat.

        Parameters
        ----------
        T : float or list
            Fluid temperature in [K]

        Returns
        -------
        conductivity: float
            Specific heat in [J/kg/K]
        """
        A = 1.751E+02
        B = 4.961E-02
        C = 1.985E-05
        D = 2.099E-09
        E = 1.524E+06
        Tlim = 1300
        if max(T) > Tlim:
            logging.info(f"Inlet T > {Tlim} K, out of specific heat correlation range!")
        return A-B*T+C*(T**2)-D*(T**3)-E*(T**(-2))
    
    @staticmethod
    def conductivity(T):
        """ Conductivity.

        Parameters
        ----------
        T : float or list
            Fluid temperature in [K]

        Returns
        -------
        conductivity: float
            Heat conductivity in [W/m/K]
        """
        A = 9.2E+00
        B = 1.1E-02
        Tlim = 1300
        if T > Tlim:
            logging.info(f"Inlet T > {Tlim} K, out of specific heat correlation range!")
        return A+B*T

    @staticmethod
    def viscosity(T):
        """ Viscosity.

        Parameters
        ----------
        T : float or list
            Fluid temperature in [K]

        Returns
        -------
        viscosity: float
            Thermal expansion coefficient in [Pa*s]
        """
        A = 4.550E-04
        B = 1.069E+03
        Tlim = 1470
        if T > Tlim:
            logging.info(f"Inlet T > {Tlim} K, out of specific heat correlation range!")
        return A*exp(B/T)

    @staticmethod
    def thermal_expansion_coefficient(T):
        """ -1/density*(d_density/d_temperature)

        Parameters
        ----------
        T : float or list
            Fluid temperature in [K]

        Returns
        -------
        thermal_expansion_coefficient: float
            Thermal expansion coefficient in [1/K]
        """
        A = 9.5169E+03
        return 1/(A-T)