"""Schemas for stats."""

from typing import Any

from pydantic import Field

from ..base import BaseSchema


class _DistributionBase(BaseSchema):
    """Base class for distribution schemas that adds 'distribution' key to config."""

    def to_config(self) -> dict:
        """Convert to parser-compatible format with 'distribution' key."""
        config = {}
        # Process each field, calling to_config on nested schemas
        for key, value in self:
            if value is None:
                continue
            if hasattr(value, "to_config"):
                config[key] = value.to_config()
            elif hasattr(value, "tolist"):
                config[key] = value.tolist()
            else:
                config[key] = value
        # Add 'distribution' key with the class name (NOT 'type')
        config["distribution"] = self.__class__.__name__
        return config


class Dirichlet(_DistributionBase):
    """Schema for Dirichlet."""

    alpha: Any = Field(...)

    def __init__(self, alpha):
        super().__init__(alpha=alpha)


class Distribution(BaseSchema):
    """Schema for Distribution."""

    distribution: Any | None = Field(default=None)

    def __init__(self, distribution=None):
        super().__init__(distribution=distribution)


class LogNormal(_DistributionBase):
    """Schema for LogNormal."""

    mean: Any = Field(...)
    std: Any = Field(...)

    def __init__(self, mean, std):
        super().__init__(mean=mean, std=std)


class MultivariateLogNormal(_DistributionBase):
    """Schema for MultivariateLogNormal."""

    mean: Any = Field(...)
    cov: Any = Field(...)

    def __init__(self, mean, cov):
        super().__init__(mean=mean, cov=cov)


class MultivariateNormal(_DistributionBase):
    """Schema for MultivariateNormal."""

    mean: Any = Field(...)
    cov: Any = Field(...)

    def __init__(self, mean, cov):
        super().__init__(mean=mean, cov=cov)


class Normal(_DistributionBase):
    """Schema for Normal."""

    mean: Any = Field(...)
    std: Any = Field(...)

    def __init__(self, mean, std):
        super().__init__(mean=mean, std=std)


class PointMass(_DistributionBase):
    """Schema for PointMass."""

    value: Any = Field(...)

    def __init__(self, value):
        super().__init__(value=value)


class Uniform(_DistributionBase):
    """Schema for Uniform."""

    lb: Any = Field(...)
    ub: Any = Field(...)

    def __init__(self, lb, ub):
        super().__init__(lb=lb, ub=ub)
