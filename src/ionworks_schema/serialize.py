"""Canonical (de)serialisation of parameter-value mappings.

A parameter mapping is ``{name: value}`` where a value may be a number, a
string, a numpy array, a ``pybamm`` symbol (including an ``Interpolant``), or a
raw callable. This module is the single source of truth for converting such
mappings to and from the JSON-native wire format, so ``ionworks_schema`` and
``ionworkspipeline`` agree byte-for-byte instead of each hand-rolling the
branches (which is how they drifted).

It is a thin adapter over pybamm's own codec primitives
(``convert_symbol_to_json`` / ``convert_function_to_symbolic_expression`` /
``convert_symbol_from_json``) plus the two things our wire format needs that
pybamm's ``ParameterValues.to_json`` does not: drop ``citations`` (provenance,
not a parameter) and flatten a ``pybamm.Scalar`` back to a bare float. The
Scalar step is the inverse of the pipeline's parameter parser, which turns
wire-format floats into ``pybamm.Scalar`` for the runtime — serialising undoes
that, which is why the per-value logic lives here rather than delegating to
pybamm's whole-mapping form. Serialisation is idempotent: an already-JSON-native
value (number, string, or a dict from a previous serialise) is returned
unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pybamm
from pybamm.expression_tree.operations.serialise import (
    convert_function_to_symbolic_expression,
    convert_symbol_from_json,
    convert_symbol_to_json,
)


def serialize_parameter_value(name: str, value: Any) -> Any:
    """Serialise a single parameter value to its JSON-native wire form.

    Parameters
    ----------
    name : str
        The parameter name. Used only to name the traced function when
        ``value`` is a raw callable.
    value : Any
        A number, string, numpy array, ``pybamm.Scalar``, ``pybamm`` symbol
        (e.g. an ``Interpolant``), or a raw callable. A value that is already
        JSON-native (number, string, or a dict/list from a previous
        serialisation) is returned unchanged, making this idempotent.

    Returns
    -------
    Any
        The JSON-serialisable representation: numbers/strings pass through;
        ``pybamm.Scalar`` becomes a float; arrays, symbols, and callables
        become symbol-JSON dicts.
    """
    if isinstance(value, pybamm.Scalar):
        return float(value.value)
    # A pybamm.Symbol is callable too but serialises directly; only trace a raw
    # Python callable.
    if callable(value) and not isinstance(value, pybamm.Symbol):
        value = convert_function_to_symbolic_expression(value, name)
    # convert_symbol_to_json passes numbers/strings/already-serialised dicts
    # through and encodes arrays/symbols.
    return convert_symbol_to_json(value)


def serialize_parameters(parameters: Mapping[str, Any]) -> dict:
    """Serialise a ``{name: value}`` mapping to the JSON-native wire format.

    Parameters
    ----------
    parameters : Mapping[str, Any]
        Parameter mapping (a plain dict or a ``pybamm.ParameterValues``). The
        ``"citations"`` key, if present, is dropped — it is provenance
        metadata, not a parameter value, and is not part of the wire format.

    Returns
    -------
    dict
        Mapping with each value passed through :func:`serialize_parameter_value`.
    """
    return {
        name: serialize_parameter_value(name, value)
        for name, value in parameters.items()
        if name != "citations"
    }


def deserialize_parameter_value(value: Any) -> Any:
    """Rebuild a single parameter value from its JSON-native wire form.

    Parameters
    ----------
    value : Any
        A serialised value. A dict is a symbol-JSON tree and is rebuilt into a
        ``pybamm`` symbol; anything else (number, string) is returned unchanged.

    Returns
    -------
    Any
        The reconstructed value.
    """
    if isinstance(value, dict):
        return convert_symbol_from_json(value)
    return value


def deserialize_parameters(parameters: Mapping[str, Any]) -> dict:
    """Rebuild a ``{name: value}`` mapping from the JSON-native wire format.

    Parameters
    ----------
    parameters : Mapping[str, Any]
        Serialised parameter mapping.

    Returns
    -------
    dict
        Mapping with each value passed through
        :func:`deserialize_parameter_value`.
    """
    return {
        name: deserialize_parameter_value(value) for name, value in parameters.items()
    }
