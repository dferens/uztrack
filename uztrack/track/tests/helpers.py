from random import sample, randrange

from bitfield.types import BitHandler
from model_mommy.recipe import Recipe

from ..models import TrackedWay, \
                     TrackedWayDayHistory as History, \
                     TrackedWayDayHistorySnapshot as Snapshot


def tracked_way_days_generator(as_integer=True):
    """
    Returns randomly selected days.
    """
    possible_days = list(TrackedWay.days)
    selected_days = sample(possible_days, randrange(1, len(possible_days)))

    result = BitHandler(0, possible_days)
    for random_day in selected_days:
        setattr(result , random_day, True)

    return int(result) if as_integer else result


def __snapshot_data_generator():
    return '{}'


def _recipe_wrapper(recipe):
    return lambda **kwargs: recipe.make(**kwargs)


TrackedWayRecipe = Recipe(TrackedWay,
    days = tracked_way_days_generator,
)
TrackedWayFactory = _recipe_wrapper(TrackedWayRecipe)
TrackedWayDayHistoryRecipe = Recipe(History,
    tracked_way = TrackedWayFactory,
)
TrackedWayDayHistoryFactory = _recipe_wrapper(TrackedWayDayHistoryRecipe)
TrackedWayDayHistorySnapshotRecipe = Recipe(Snapshot,
    history = TrackedWayDayHistoryFactory,
    snapshot_data = __snapshot_data_generator,
)
TrackedWayDayHistorySnapshotFactory = _recipe_wrapper(TrackedWayDayHistorySnapshotRecipe)
