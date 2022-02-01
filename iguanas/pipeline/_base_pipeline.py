from copy import deepcopy
from typing import List, Tuple, Union
from iguanas.pipeline.class_accessor import ClassAccessor
from iguanas.utils.typing import PandasDataFrameType, PandasSeriesType
import iguanas.utils.utils as utils
from iguanas.exceptions import DataFrameSizeError


class _BasePipeline:
    """
    Base pipeline class. Main pipeline classes inherit from this one.

    Parameters
    ----------
    steps : List[Tuple[str, object]]
        The steps to be applied as part of the pipeline.         

    Attributes
    ----------
    steps_ : List[Tuple[str, object]]
        The steps corresponding to the fitted pipeline.
    """

    def __init__(self, steps: List[Tuple[str, object]]) -> None:
        self.steps = steps
        self.steps_ = None

    def get_params(self) -> dict:
        """
        Returns the parameters of each step in the pipeline.

        Returns
        -------
        dict
            The parameters of each step in the pipeline.
        """

        pipeline_params = {}
        steps_ = self.steps if self.steps_ is None else self.steps_
        for step_tag, step in steps_:
            # If step inherits from _BasePipeline, call its get_params
            if issubclass(step.__class__, _BasePipeline):
                step_param_dict = step.get_params()
                pipeline_params.update(step_param_dict)
            else:
                step_param_dict = deepcopy(step.__dict__)
                pipeline_params[step_tag] = step_param_dict
        return pipeline_params

    def _update_kwargs(self, params: dict) -> None:
        """
        Updates the given parameters of the given steps in the pipeline.

        Parameters
        ----------
        params : dict
            A dictionary where each key corresponds to the tag used for the 
            pipeline step. Each value should be a dictionary of the parameters
            (keys) and their new values (values).
        """

        for step_tag, step in self.steps:
            # If step inherits from _BasePipeline, call its _update_kwargs
            if issubclass(step.__class__, _BasePipeline):
                step._update_kwargs(params)
            if step_tag in params.keys():
                step.__dict__.update(params[step_tag])

    def _pipeline_fit(self,
                      step_tag: str,
                      step: object,
                      X: Union[PandasDataFrameType, dict],
                      y: Union[PandasSeriesType, dict],
                      sample_weight: Union[PandasSeriesType, dict]) -> None:
        """
        Runs the following before applying the `fit` method of `step`:

          1. Checks the parameters of `step` for `ClassAccessor` objects. If a
            `ClassAccessor` object is found, the parameter in `step` is updated
            with the class attribute denoted by the `ClassAccessor` object.
          2. Checks if `X`, `y` or `sample_weight` are dictionaries. If so, 
            then the dataset aligned to `step_tag` is extracted.

        Parameters
        ----------
        step_tag : str
            The tag corresponding to the step.
        step : object
            The step in the pipeline.
        X : Union[PandasDataFrameType, dict]
            The dataset or dictionary of datasets for each pipeline step.
        y : Union[PandasSeriesType, dict]
            The binary target column or dictionary of binary target columns
            for each pipeline step.
        sample_weight : Union[PandasSeriesType, dict], optional
            Row-wise weights or dictionary of row-wise weights for each
            pipeline step. Defaults to None.
        """

        step = self._check_accessor(step)
        X, y, sample_weight = [
            utils.return_dataset_if_dict(
                step_tag=step_tag, df=df
            ) for df in (X, y, sample_weight)
        ]
        step.fit(X, y, sample_weight)

    def _pipeline_transform(self,
                            step_tag: str,
                            step: object,
                            X: Union[PandasDataFrameType, dict]) -> PandasDataFrameType:
        """
        Runs the following before applying the `transform` method of `step`:

          1. Checks the parameters of `step` for `ClassAccessor` objects. If a
            `ClassAccessor` object is found, the parameter in `step` is updated
            with the class attribute denoted by the `ClassAccessor` object.
          2. Checks if `X`, `y` or `sample_weight` are dictionaries. If so, 
            then the dataset aligned to `step_tag` is extracted.

        Parameters
        ----------
        step_tag : str
            The tag corresponding to the step.
        step : object
            The step in the pipeline.
        X : Union[PandasDataFrameType, dict]
            The dataset or dictionary of datasets for each pipeline step.                        

        Returns
        -------
        PandasDataFrameType
            The transformed dataset.
        """

        step = self._check_accessor(step)
        X = utils.return_dataset_if_dict(step_tag=step_tag, df=X)
        X = step.transform(X)
        self._exception_if_no_cols_in_X(X, step_tag)
        return X

    def _pipeline_predict(self,
                          step: object,
                          X: Union[PandasDataFrameType, dict]) -> PandasSeriesType:
        """
        Runs the following before applying the `predict` method of `step`:

          1. Checks the parameters of `step` for `ClassAccessor` objects. If a
            `ClassAccessor` object is found, the parameter in `step` is updated
            with the class attribute denoted by the `ClassAccessor` object.          

        Parameters
        ----------        
        step : object
            The step in the pipeline.
        X : Union[PandasDataFrameType, dict]
            The dataset or dictionary of datasets for each pipeline step.        

        Returns
        -------
        PandasSeriesType
            The prediction of the final step.
        """

        step = self._check_accessor(step)
        return step.predict(X)

    def _pipeline_fit_transform(self,
                                step_tag: str,
                                step: object,
                                X: Union[PandasDataFrameType, dict],
                                y: Union[PandasSeriesType, dict],
                                sample_weight: Union[PandasSeriesType, dict]) -> PandasDataFrameType:
        """
        Runs the following before applying the `fit_transform` method of `step`:

          1. Checks the parameters of `step` for `ClassAccessor` objects. If a
            `ClassAccessor` object is found, the parameter in `step` is updated
            with the class attribute denoted by the `ClassAccessor` object.
          2. Checks if `X`, `y` or `sample_weight` are dictionaries. If so, 
            then the dataset aligned to `step_tag` is extracted.

        Parameters
        ----------
        step_tag : str
            The tag corresponding to the step.
        step : object
            The step in the pipeline.
        X : Union[PandasDataFrameType, dict]
            The dataset or dictionary of datasets for each pipeline step.
        y : Union[PandasSeriesType, dict]
            The binary target column or dictionary of binary target columns
            for each pipeline step.
        sample_weight : Union[PandasSeriesType, dict], optional
            Row-wise weights or dictionary of row-wise weights for each
            pipeline step. Defaults to None.

        Returns
        -------
        PandasDataFrameType
            The transformed dataset.
        """

        step = self._check_accessor(step)
        X, y, sample_weight = [
            utils.return_dataset_if_dict(
                step_tag=step_tag, df=df
            ) for df in (X, y, sample_weight)
        ]
        X = step.fit_transform(X, y, sample_weight)
        self._exception_if_no_cols_in_X(X, step_tag)
        return X

    def _check_accessor(self,
                        step: object) -> object:
        """
        Checks whether the any of the parameters in the given `step` is of type
        ClassAccessor. If so, then it runs the ClassAccessor's `get` method,
        which extracts the given attribute from the given step in the pipeline,
        and injects it into the parameter.
        """

        step_param_dict = step.__dict__
        for param, value in step_param_dict.items():
            if isinstance(value, ClassAccessor):
                pipeline_params = self.get_params()
                step.__dict__[param] = value.get(pipeline_params)
        return step

    @staticmethod
    def _exception_if_no_cols_in_X(X: PandasDataFrameType,
                                   step_tag: str) -> Union[None, DataFrameSizeError]:
        """Raises an exception if `X` has no columns."""

        if X.shape[1] == 0:
            raise DataFrameSizeError(
                f'`X` has been reduced to zero columns after the `{step_tag}` step in the pipeline.'
            )
