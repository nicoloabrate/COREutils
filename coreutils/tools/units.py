"""Small unit conversion helpers for FRENETIC post-processing."""

import re

import numpy as np


class UnitConversionError(ValueError):
    pass


_DISPLAY_UNITS = {
    "k": "K",
    "degc": r"^\circ C",
    "m": "m",
    "cm": "cm",
    "s": "s",
    "ms": "ms",
    "us": r"\mu s",
    "w": "W",
    "mw": "MW",
    "w/m3": "W/m^3",
    "mw/m3": "MW/m^3",
    "w/cm3": "W/cm^3",
    "mw/cm3": "MW/cm^3",
}


_UNIT_ALIASES = {
    "kelvin": "k",
    "degc": "degc",
    "celsius": "degc",
    "centigrade": "degc",
    "c": "degc",
    "°c": "degc",
    "^{\\circ}c": "degc",
    "^\\circc": "degc",
    "seconds": "s",
    "second": "s",
    "sec": "s",
    "msec": "ms",
    "millisecond": "ms",
    "milliseconds": "ms",
    "microsecond": "us",
    "microseconds": "us",
    "micros": "us",
    "usec": "us",
    "μs": "us",
    "µs": "us",
}


def _strip_outer_brackets(unit):
    if unit.startswith("[") and unit.endswith("]"):
        return unit[1:-1]
    return unit


def canonical_unit(unit):
    """Return a compact canonical unit key."""
    if unit is None:
        raise UnitConversionError("Cannot convert values with undefined unit.")

    unit = str(unit).strip()
    unit = _strip_outer_brackets(unit)
    unit = unit.strip()
    unit = unit.replace("**", "^")
    unit = unit.replace(" ", "")
    unit = unit.replace("·", "*")
    unit = unit.replace("μ", "u").replace("µ", "u")
    unit = unit.lower()
    unit = re.sub(r"\^\{(-?\d+)\}", r"^\1", unit)

    if unit in _UNIT_ALIASES:
        return _UNIT_ALIASES[unit]

    if unit in _DISPLAY_UNITS:
        return unit

    power_density_aliases = {
        "wcm^-3": "w/cm3",
        "wcm-3": "w/cm3",
        "w/cm^3": "w/cm3",
        "w/cm**3": "w/cm3",
        "w/m^3": "w/m3",
        "w/m**3": "w/m3",
        "mwcm^-3": "mw/cm3",
        "mwcm-3": "mw/cm3",
        "mw/cm^3": "mw/cm3",
        "mw/cm**3": "mw/cm3",
        "mw/m^3": "mw/m3",
        "mw/m**3": "mw/m3",
    }
    if unit in power_density_aliases:
        return power_density_aliases[unit]

    return unit


def display_unit(unit):
    return _DISPLAY_UNITS.get(canonical_unit(unit), str(unit))


def _linear_convert(values, factor):
    return np.asarray(values) * factor


def convert_units(values, from_unit, to_unit):
    """Convert values and return ``(converted_values, display_unit)``."""
    src = canonical_unit(from_unit)
    dst = canonical_unit(to_unit)

    if src == dst:
        return values, display_unit(dst)

    conversions = {
        ("k", "degc"): lambda x: np.asarray(x) - 273.15,
        ("degc", "k"): lambda x: np.asarray(x) + 273.15,
        ("m", "cm"): lambda x: _linear_convert(x, 100.0),
        ("cm", "m"): lambda x: _linear_convert(x, 0.01),
        ("s", "ms"): lambda x: _linear_convert(x, 1.0e3),
        ("ms", "s"): lambda x: _linear_convert(x, 1.0e-3),
        ("s", "us"): lambda x: _linear_convert(x, 1.0e6),
        ("us", "s"): lambda x: _linear_convert(x, 1.0e-6),
        ("ms", "us"): lambda x: _linear_convert(x, 1.0e3),
        ("us", "ms"): lambda x: _linear_convert(x, 1.0e-3),
        ("w", "mw"): lambda x: _linear_convert(x, 1.0e-6),
        ("mw", "w"): lambda x: _linear_convert(x, 1.0e6),
    }

    power_density_to_w_per_cm3 = {
        "w/cm3": 1.0,
        "mw/cm3": 1.0e6,
        "w/m3": 1.0e-6,
        "mw/m3": 1.0,
    }
    if src in power_density_to_w_per_cm3 and dst in power_density_to_w_per_cm3:
        factor = power_density_to_w_per_cm3[src] / power_density_to_w_per_cm3[dst]
        return _linear_convert(values, factor), display_unit(dst)

    try:
        return conversions[(src, dst)](values), display_unit(dst)
    except KeyError as exc:
        raise UnitConversionError(f"Cannot convert from {from_unit!r} to {to_unit!r}.") from exc
