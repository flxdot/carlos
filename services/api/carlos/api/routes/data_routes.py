__all__ = ["data_router"]


from carlos.database.context import RequestContext
from carlos.database.data.timeseries import (
    MAX_QUERY_RANGE,
    DatetimeRange,
    TimeseriesData,
    get_timeseries,
)
from fastapi import APIRouter, Depends, Query
from starlette import status

from carlos.api.depends.context import request_context
from carlos.api.params.query import datetime_range
from carlos.api.utils.data_reduction import optimize_timeseries

data_router = APIRouter()


@data_router.get(
    "/timeseries",
    summary="Get timeseries data",
    response_model=list[TimeseriesData],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Timeseries not found."},
        status.HTTP_400_BAD_REQUEST: {
            "description": f"Range was invalid or more than {MAX_QUERY_RANGE}"
        },
    },
)
async def get_timeseries_route(
    timeseries_id: list[int] = Query(
        ...,
        alias="timeseriesId",
        description="One ore more timeseries identifiers to get data for.",
    ),
    reduce_samples: bool = Query(
        True,
        alias="reduceSamples",
        description="Activated by default. This function will try to reduce the "
        "number of samples returned by removing consecutive samples that change less "
        "than 0.5% as they are not visible in the UI any how.",
    ),
    dt_range: DatetimeRange = Depends(datetime_range),
    context: RequestContext = Depends(request_context),
):
    """Returns the timeseries data for the given timeseries identifiers."""

    timeseries = await get_timeseries(
        context=context, timeseries_ids=timeseries_id, datetime_range=dt_range
    )

    sample_reduce_threshold = 0.005 if reduce_samples else 0.0

    return [
        optimize_timeseries(
            timeseries=ts, sample_reduce_threshold=sample_reduce_threshold
        )
        for ts in timeseries
    ]
