"""Solver config schemas."""

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field

from ..base import BaseSchema


class ScipySolverConfig(BaseSchema):
    """Configuration for pybamm.ScipySolver.

    Parameters
    ----------
    type : Literal["ScipySolver"]
        Must be "ScipySolver".
    method : str, optional
        Integration method for scipy.integrate.solve_ivp (e.g. "RK45", "BDF").
    rtol : float, optional
        Relative tolerance.
    atol : float, optional
        Absolute tolerance.
    extra_options : dict, optional
        Additional options passed to the scipy solver.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["ScipySolver"] = Field(..., description="Solver type")
    method: str | None = Field(None, description="Integration method (e.g. RK45, BDF)")
    rtol: float | None = Field(None, description="Relative tolerance")
    atol: float | None = Field(None, description="Absolute tolerance")
    extra_options: dict[str, Any] | None = Field(
        None, description="Extra options for scipy solver"
    )


class CasadiSolverConfig(BaseSchema):
    """Configuration for pybamm.CasadiSolver.

    Parameters
    ----------
    type : Literal["CasadiSolver"]
        Must be "CasadiSolver".
    mode : str, optional
        "safe" or "fast".
    rtol : float, optional
        Relative tolerance.
    atol : float, optional
        Absolute tolerance.
    perturb_algebraic_initial_conditions : bool, optional
        Whether to perturb algebraic initial conditions.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["CasadiSolver"] = Field(..., description="Solver type")
    mode: str | None = Field(None, description="Mode: safe or fast")
    rtol: float | None = Field(None, description="Relative tolerance")
    atol: float | None = Field(None, description="Absolute tolerance")
    perturb_algebraic_initial_conditions: bool | None = Field(
        None, description="Perturb algebraic initial conditions"
    )


class IDAKLUSolverConfig(BaseSchema):
    """Configuration for pybamm.IDAKLUSolver.

    Parameters
    ----------
    type : Literal["IDAKLUSolver"]
        Must be "IDAKLUSolver".
    rtol : float, optional
        Relative tolerance.
    atol : float, optional
        Absolute tolerance.
    options : dict, optional
        IDAKLU-specific options (e.g. num_threads, num_solvers).
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["IDAKLUSolver"] = Field(..., description="Solver type")
    rtol: float | None = Field(None, description="Relative tolerance")
    atol: float | None = Field(None, description="Absolute tolerance")
    options: dict[str, Any] | None = Field(None, description="IDAKLU solver options")


class AlgebraicSolverConfig(BaseSchema):
    """Configuration for pybamm.AlgebraicSolver.

    Parameters
    ----------
    type : Literal["AlgebraicSolver"]
        Must be "AlgebraicSolver".
    method : str, optional
        Root-finding method (e.g. "hybr", "lm").
    tol : float, optional
        Tolerance for the algebraic solver.
    extra_options : dict, optional
        Extra options for the root finder.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["AlgebraicSolver"] = Field(..., description="Solver type")
    method: str | None = Field(None, description="Root-finding method (e.g. hybr, lm)")
    tol: float | None = Field(None, description="Tolerance")
    extra_options: dict[str, Any] | None = Field(
        None, description="Extra options for root finder"
    )


class CasadiAlgebraicSolverConfig(BaseSchema):
    """Configuration for pybamm.CasadiAlgebraicSolver.

    Parameters
    ----------
    type : Literal["CasadiAlgebraicSolver"]
        Must be "CasadiAlgebraicSolver".
    tol : float, optional
        Tolerance.
    step_tol : float, optional
        Step tolerance.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["CasadiAlgebraicSolver"] = Field(..., description="Solver type")
    tol: float | None = Field(None, description="Tolerance")
    step_tol: float | None = Field(None, description="Step tolerance")


# Forward reference for recursive CompositeSolverConfig
SolverConfigDict = dict[str, Any]


class CompositeSolverConfig(BaseSchema):
    """Configuration for pybamm.CompositeSolver.

    Parameters
    ----------
    type : Literal["CompositeSolver"]
        Must be "CompositeSolver".
    sub_solvers : list of solver config dicts
        List of solver configurations (each with "type" and solver-specific keys).
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal["CompositeSolver"] = Field(..., description="Solver type")
    sub_solvers: list[SolverConfigDict] = Field(
        ..., description="List of solver config dicts"
    )


# Union of all solver config types for use in simulation_kwargs
SolverConfig = Annotated[
    ScipySolverConfig
    | CasadiSolverConfig
    | IDAKLUSolverConfig
    | AlgebraicSolverConfig
    | CasadiAlgebraicSolverConfig
    | CompositeSolverConfig,
    Field(discriminator="type"),
]
