from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from fastapi import HTTPException
from pydantic import BaseModel, Field, validator

from evaluator.app.mongo.mongo_model import MongoModel
from evaluator.app.mongo.py_object_id import PyObjectId


class ExtractiveQADatasetMapping(BaseModel):
    id_column: str = Field(...)
    question_column: str = Field(...)
    context_column: str = Field(...)
    answers_column: str = Field(...)


class MultipleChoiceQADatasetMapping(BaseModel):
    id_column: str = Field(...)
    question_column: str = Field(...)
    choices_columns: list[str] = Field(...)
    choices_key_mapping_column: Optional[str] = Field(...)
    answer_index_column: str = Field(...)


SUPPORTED_SKILL_TYPES = {
    "extractive-qa": ExtractiveQADatasetMapping,
    "multiple-choice": MultipleChoiceQADatasetMapping,
}
"""
This constant contains all skill types that are supported during evaluation.
It is a dictionary that maps the skill types to their mapping classes.
This dictionary is used to automatically check the schema of the selected skill type.
"""  # pylint: disable=W0105


class DatasetMetadata(MongoModel):
    name: str = Field(...)
    skill_type: str = Field(
        ...,
        description="Name of the skill type. The name must be defined by the application (validated by the constant `SUPPORTED_SKILL_TYPES`).",
    )
    metric: str = Field(..., description="Name of the default metric.")
    mapping: Union[ExtractiveQADatasetMapping, MultipleChoiceQADatasetMapping] = Field(
        ...
    )


class Prediction(BaseModel):
    id: str = Field(
        ..., description="Identifier of the sample in the respective dataset."
    )
    output: str = Field(
        ...,
        description="The actual output of the model as string. "
        "Could be an answer for QA, an argument for AR or a label for Fact Checking.",
    )
    output_score: float = Field(..., description="The score assigned to the output.")


class PredictionResult(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    skill_id: PyObjectId = Field(
        ..., description="Identifier of the skill that generated the prediction."
    )
    dataset_name: str = Field(..., description="Name of the dataset")
    last_updated_at: datetime = Field()
    calculation_time: float = Field(..., description="Calculation time in seconds")
    predictions: List[Prediction] = Field(...)


class EvaluationStatus(str, Enum):
    requested = "REQUESTED"
    started = "STARTED"
    finished = "FINISHED"
    failed = "FAILED"


class Evaluation(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    user_id: str = Field(..., description="ID of the user that started the evaluation.")
    skill_id: PyObjectId = Field(
        ..., description="ID of the skill to use for evaluation."
    )
    dataset_name: str = Field(
        ..., description="Name of the dataset to run the skill on."
    )
    metric_name: str = Field(
        ..., description="Name of the metric to compute on the predictions."
    )
    prediction_status: EvaluationStatus = Field(
        ..., description="Current status of the prediction task."
    )
    prediction_error: Optional[str] = Field(
        None,
        description="Error message of the error that lead to failure of the prediction task.",
    )
    metric_status: EvaluationStatus = Field(
        ..., description="Current status of the evaluation (metric computation) task."
    )
    metric_error: Optional[str] = Field(
        None,
        description="Error message of the error that lead to failure of the evaluation (metric computation) task.",
    )


class Metric(BaseModel):
    last_updated_at: datetime = Field(...)
    calculation_time: float = Field(..., description="Calculation time in seconds")
    results: dict = Field(
        ...,
        description="Dictionary of calculated results. The values depend on the respective metric.",
    )


class MetricResult(MongoModel):
    id: Optional[PyObjectId] = Field(
        None, description="Identifier generated by mongoDB"
    )
    prediction_result_id: PyObjectId = Field(
        ..., description="Identifier of the corresponding PredictionResult object"
    )
    skill_id: PyObjectId = Field(
        ...,
        description="Identifier of the skill that generated the predictions the metrics are calculated on.",
    )
    dataset_name: str = Field(..., description="Name of the dataset")
    metrics: dict = Field(..., description="Dictionary of all Metric objects")


class EvaluationResult(BaseModel):
    evaluation_id: str = Field(..., description="Skill Id + metric name")
    evaluation_status: str = Field(..., description="Evaluation status.")
    evaluation_error: str = Field(None, description="Description of error")
    skill_name: str = Field(..., description="Model name")
    dataset: str = Field(..., description="Dataset used for evaluation")
    public: bool = Field(
        ...,
        description="Describes wether it's a public evaluation or a private evaluation for the user.",
    )
    metric_name: str = Field(..., description="Metric name")
    metric_result: dict = Field(..., description="List with single metric results")
    skill_url: str = Field(
        ...,
        description="Skill url, used to check if skill is available to compute evaluations",
    )


class ExtractiveDatasetSample(BaseModel):
    id: str = Field(..., description="ID of the sample in the dataset.")
    question: str = Field(..., description="Question of the sample.")
    context: str = Field(
        ..., description="Context that contains the answer to the question."
    )
    answers: List[str] = Field(...)


class MultipleChoiceDatasetSample(BaseModel):
    id: str = Field(..., description="ID of the sample in the dataset.")
    question: str = Field(..., description="Question of the sample.")
    choices: List[str] = Field(...)
    answer_index: int = Field(
        ...,
        description="Index of the choice-entry in choices that represents the correct answer.",
    )


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="ID of the task.")
    state: str = Field(..., description="Current state of the task.")
    finished: Optional[datetime] = Field(
        None, description="Date when the task finished processing."
    )
    result: Optional[str] = Field(None, description="Result of the task.")


class LeaderboardEntry(BaseModel):
    rank: Union[None, int] = Field(None, description="Rank of the entry.")
    date: datetime = Field(..., description="Date when the metric got calculated.")
    skill_id: str = Field(..., description="ID of the skill, the results are based on.")
    skill_name: str = Field(
        ..., description="Name of the skill, the results are based on"
    )
    private: bool = Field(
        ...,
        description="Whether the skill is only visible to the currently logged in user.",
    )
    result: dict = Field(..., description="Evaluation results of the metric.")
