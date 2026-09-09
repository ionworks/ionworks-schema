"""Tests for ionworks_schema data_fit (DataFit, ArrayDataFit)."""

import ionworks_schema as iws
from ionworks_schema.data_fit import ArrayDataFit, DataFit
from ionworks_schema.objectives import FittingObjective, Objective
from ionworks_schema.parameter_estimators import AskTellOptimizer
import pandas as pd
from pydantic import ValidationError
import pytest


def test_data_fit_requires_parameters_or_priors():
    """DataFit model validator requires at least one of parameters or priors."""
    obj = Objective(data_input="file:data.csv")
    with pytest.raises(ValueError, match="Either 'parameters' or 'priors'"):
        DataFit(objectives={"fit1": obj}, source="test")


def test_data_fit_accepts_parameters_and_priors_together():
    """DataFit accepts both parameters and priors — priors then act as
    regularizers on the listed fit parameters (matches runtime behavior)."""
    obj = Objective(data_input="file:data.csv")
    df = DataFit(
        objectives={"fit1": obj},
        source="test",
        parameters={"k": 1.0},
        priors={"x": {"distribution": "Normal", "mean": 0, "std": 1}},
    )
    assert df.parameters == {"k": 1.0}
    assert type(df.priors["x"]).__name__ == "Prior"
    assert df.priors["x"].name == "x"


def test_data_fit_wraps_bare_objective():
    """A bare objective (not wrapped in a dict) is auto-wrapped."""
    obj = Objective(data_input="file:data.csv")
    df = DataFit(objectives=obj, source="test", parameters={"x": 1.0})
    assert isinstance(df.objectives, dict)
    assert "Objective" in df.objectives
    cfg = df.to_config()
    assert "Objective" in cfg["objectives"]


def test_data_fit_minimal_with_parameters():
    """DataFit with objectives and parameters serializes."""
    obj = Objective(data_input="file:data.csv")
    df = DataFit(
        objectives={"fit1": obj},
        source="test source",
        parameters={"x": 1.0},
    )
    cfg = df.to_config()
    assert "objectives" in cfg
    assert "source" not in cfg  # source is excluded from serialization
    assert cfg.get("parameters") == {"x": 1.0}


def test_data_fit_minimal_with_priors():
    """DataFit with objectives and priors (non-empty) is valid."""
    obj = Objective(data_input="file:data.csv")
    df = DataFit(
        objectives={"fit1": obj},
        source="test",
        priors={"x": {"distribution": "Normal", "mean": 0, "std": 1}},
    )
    cfg = df.to_config()
    assert "objectives" in cfg
    assert cfg.get("priors") is not None


def test_data_fit_to_config_includes_objectives():
    """DataFit to_config serializes nested objectives."""
    obj = Objective(data_input="file:path.csv", options={"key": "value"})
    df = DataFit(objectives={"obj1": obj}, source="", parameters={"p": 1})
    cfg = df.to_config()
    assert "objectives" in cfg
    # Nested schema should be serialized (e.g. to dict with data key)
    objs = cfg["objectives"]
    assert "obj1" in objs
    assert objs["obj1"].get("data") == "file:path.csv"


def test_objective_bare_dataframe_is_wrapped():
    """A bare DataFrame in `data` serializes wrapped as {"data": <columns>}.

    The server parser expects the wrapped form; previously callers had to write
    {"data": df} by hand to avoid a "Required field 'data' missing" error.
    """
    df = pd.DataFrame({"Voltage [V]": [4.2, 3.5], "Capacity [A.h]": [0.0, 1.0]})
    obj = FittingObjective(data_input=df)
    cfg = obj.to_config()
    assert cfg["data"] == {"data": df.to_dict(orient="list")}


def test_objective_bare_polars_dataframe_is_wrapped():
    """A bare polars DataFrame is wrapped the same way as pandas."""
    pl = pytest.importorskip("polars")
    df = pl.DataFrame({"Voltage [V]": [4.2, 3.5], "Capacity [A.h]": [0.0, 1.0]})
    obj = FittingObjective(data_input=df)
    cfg = obj.to_config()
    assert cfg["data"] == {"data": df.to_dict(as_series=False)}


def test_objective_string_data_is_not_wrapped():
    """A string path stays a string — only bare DataFrames are wrapped."""
    obj = FittingObjective(data_input="file:foo.csv")
    assert obj.to_config()["data"] == "file:foo.csv"


def test_objective_prewrapped_dataframe_is_not_double_wrapped():
    """An already-wrapped {"data": df} keeps a single level of wrapping."""
    df = pd.DataFrame({"Voltage [V]": [4.2, 3.5], "Capacity [A.h]": [0.0, 1.0]})
    obj = FittingObjective(data_input={"data": df})
    cfg = obj.to_config()
    assert cfg["data"] == {"data": df.to_dict(orient="list")}


def test_array_data_fit_does_not_wrap_bare_objective():
    """ArrayDataFit must NOT auto-wrap a bare objective (keys carry IV values)."""
    obj = Objective(data_input="file:data.csv")
    adf = ArrayDataFit(objectives=obj, parameters={"p": 1.0})
    assert not isinstance(adf.objectives, dict)


def test_array_data_fit_requires_objectives():
    """ArrayDataFit requires objectives dict."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        ArrayDataFit(objectives=None)
    with pytest.raises(Exception):
        ArrayDataFit()


def test_array_data_fit_minimal():
    """ArrayDataFit with objectives dict serializes (inherits DataFit validator: needs parameters or priors)."""
    obj = Objective(data_input="file:data.csv")
    adf = ArrayDataFit(objectives={"T1": obj}, parameters={"p": 1.0})
    cfg = adf.to_config()
    assert "objectives" in cfg
    assert "T1" in cfg["objectives"]


def test_array_data_fit_multiple_temperatures():
    """ArrayDataFit can hold multiple objectives keyed by independent variable."""
    obj1 = Objective(data_input="file:T1.csv")
    obj2 = Objective(data_input="file:T2.csv")
    adf = ArrayDataFit(
        objectives={"298.15": obj1, "318.15": obj2},
        parameters={"p": 1.0},
    )
    cfg = adf.to_config()
    assert set(cfg["objectives"].keys()) == {"298.15", "318.15"}


# --- Discriminated optimizer union (contract hardening, slice A.5) ---


def test_optimizer_dict_roundtrip_discriminates(min_fit):
    fit = min_fit({"type": "DifferentialEvolution", "max_iterations": 20})
    assert fit.to_config()["optimizer"]["type"] == "DifferentialEvolution"


def test_native_de_rejects_scipy_kwargs_via_datafit(min_fit):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        min_fit({"type": "DifferentialEvolution", "popsize": 5, "maxiter": 10})


def test_optimizer_instance_preserved_through_union(min_fit):
    import ionworks_schema as iws

    fit = min_fit(iws.parameter_estimators.CMAES())
    assert type(fit.optimizer).__name__ == "CMAES"


def test_optimizer_dict_missing_type_rejected(min_fit):
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        min_fit({"max_iterations": 20})  # no discriminator


def test_datafit_rejects_removed_resource_fields():
    """num_workers/parallel/max_batch_size are removed; extra='forbid' rejects them."""
    obj = Objective(data_input="file:data.csv")
    base = {"objectives": {"fit1": obj}, "parameters": {"x": 1.0}}
    for field in ("num_workers", "parallel", "max_batch_size"):
        with pytest.raises(Exception):
            DataFit(**base, **{field: 1})


def test_datafit_objective_parallelism_roundtrips():
    """objective_parallelism serializes and round-trips through to_config."""
    obj = Objective(data_input="file:data.csv")
    fit = DataFit(
        objectives={"fit1": obj}, parameters={"x": 1.0}, objective_parallelism="off"
    )
    assert fit.objective_parallelism == "off"
    assert DataFit.model_validate(fit.to_config()).objective_parallelism == "off"
    assert (
        DataFit(objectives={"fit1": obj}, parameters={"x": 1.0}).objective_parallelism
        == "auto"
    )


def test_datafit_objective_parallelism_validates_choices():
    """objective_parallelism rejects values outside the allowed literal set."""
    obj = Objective(data_input="file:data.csv")
    with pytest.raises(Exception):
        DataFit(
            objectives={"fit1": obj},
            parameters={"x": 1.0},
            objective_parallelism="sometimes",
        )


def test_asktell_rejects_async_mode():
    """async_mode is removed; passing it must raise and the field must not exist."""
    with pytest.raises(Exception):
        AskTellOptimizer(async_mode=True)
    opt = AskTellOptimizer(method="CMAES")
    assert not hasattr(opt, "async_mode")


def test_array_data_fit_element_type_in_pipeline():
    """ArrayDataFit.to_config() in pipeline context produces element_type: 'array_data_fit'."""
    from ionworks_schema.base import Pipeline

    obj = Objective(data_input="file:data.csv")
    adf = ArrayDataFit(objectives={"T1": obj}, parameters={"p": 1.0})
    pipeline = Pipeline(elements={"fit": adf})
    cfg = pipeline.to_config()
    assert cfg["elements"]["fit"]["element_type"] == "array_data_fit"


def test_data_fit_element_type_in_pipeline():
    """DataFit.to_config() in pipeline context produces element_type: 'data_fit'."""
    from ionworks_schema.base import Pipeline

    obj = Objective(data_input="file:data.csv")
    df = DataFit(objectives={"fit1": obj}, source="test", parameters={"p": 1.0})
    pipeline = Pipeline(elements={"fit": df})
    cfg = pipeline.to_config()
    assert cfg["elements"]["fit"]["element_type"] == "data_fit"


class TestDataFitOptions:
    """The ``options`` bag is a closed contract, not a free-form dict."""

    @staticmethod
    def _fit(**kwargs):
        return iws.DataFit(
            objectives={
                "ocp": iws.objectives.OCPHalfCell(
                    electrode="positive", data_input="file:ocp.csv"
                )
            },
            parameters={"p": iws.Parameter("p", initial_value=1.0, bounds=(0.0, 2.0))},
            **kwargs,
        )

    def test_misplaced_top_level_field_is_rejected(self):
        """``multistarts`` is a DataFit field, not a runtime option."""
        with pytest.raises(ValidationError, match="multistarts"):
            self._fit(options={"multistarts": 4})

    def test_unknown_option_key_is_rejected(self):
        with pytest.raises(ValidationError, match="not_an_option"):
            self._fit(options={"not_an_option": 1})

    def test_wrong_option_type_is_rejected(self):
        with pytest.raises(ValidationError, match="max_iterations"):
            self._fit(options={"max_iterations": "many"})

    @pytest.mark.parametrize("options", [{"max_iterations": 0}, {"maxtime": 0}])
    def test_non_positive_budget_is_rejected(self, options):
        """The runtime requires a positive budget, so reject it at submission."""
        with pytest.raises(ValidationError, match="greater than 0"):
            self._fit(options=options)

    @pytest.mark.parametrize("seed", [-1, 2**32])
    def test_seed_outside_numpy_range_is_rejected(self, seed):
        """``np.random.seed`` only accepts [0, 2**32 - 1]."""
        with pytest.raises(ValidationError, match="seed"):
            self._fit(options={"seed": seed})

    @pytest.mark.parametrize("maxtime", [float("inf"), float("nan")])
    def test_non_finite_maxtime_is_rejected(self, maxtime):
        with pytest.raises(ValidationError, match="maxtime"):
            self._fit(options={"maxtime": maxtime})

    def test_valid_options_are_accepted(self):
        fit = self._fit(options={"seed": 7, "max_iterations": 100})
        assert fit.options.seed == 7
        assert fit.options.max_iterations == 100

    def test_validate_accepted_under_both_spellings(self):
        assert self._fit(options={"validate": False}).options.validate_ is False
        assert (
            self._fit(options=iws.DataFitOptions(validate_=False)).options.validate_
            is False
        )

    def test_to_config_emits_only_set_options(self):
        assert self._fit(options={"seed": 1}).to_config()["options"] == {"seed": 1}

    def test_to_config_maps_validate_alias_back(self):
        config = self._fit(options={"validate": False}).to_config()
        assert config["options"] == {"validate": False}

    def test_options_omitted_when_unset(self):
        assert "options" not in self._fit().to_config()

    def test_to_config_omits_unset_non_none_defaults(self):
        """Non-None defaults must not leak into a stored config unset.

        DataFitOptions is the only bag with non-None defaults, so it is the
        only one that distinguishes set-fields-only from non-None-only.
        """
        assert iws.DataFitOptions().to_config() == {}


def test_data_fit_rejects_null_parameter_value():
    """DataFit.parameters bypasses the serializer, so it needs its own guard."""
    with pytest.raises(ValueError, match="'x'"):
        iws.DataFit(objectives={}, parameters={"x": None}, cost=iws.costs.RMSE())


def test_data_fit_non_mapping_parameters_raises_validation_error():
    """A non-mapping ``parameters`` must surface pydantic's shape error.

    The null guard runs before pydantic sees the value, so an ``AttributeError``
    escaping it would reach the caller as a 500 rather than a 400.
    """
    with pytest.raises(ValidationError):
        iws.DataFit(objectives={}, parameters="x", cost=iws.costs.RMSE())
