import copy
from queue import Queue

max_backtracks: int
history: Queue
maxage: int


def initialize(max_backtracking: int = 2, max_age_in_millis: int = 10000):
    global max_backtracks, history, maxage
    max_backtracks = max_backtracking
    history = Queue(maxsize=max_backtracking)
    maxage = max_age_in_millis


def calculateMaxAbsDiffs(
    data_with_abs: list[dict[str, tuple[float, ...]]],
    backtracks: int,
):
    max_abs_diff: float = 0.0
    start = max(len(data_with_abs) - backtracks, 1)
    for i in range(1, len(data_with_abs)):
        abs_diff: float = abs(
            data_with_abs[i]["summed_abs_measurements"][0]
            - data_with_abs[i - 1]["summed_abs_measurements"][0]
        )
        data_with_abs[i]["abs_diff"] = (abs_diff,)
    for i in range(start, len(data_with_abs)):
        if data_with_abs[i]["abs_diff"][0] > max_abs_diff:
            max_abs_diff = data_with_abs[i]["abs_diff"][0]
    return max_abs_diff


def calculateTotalGravitySquared(
    data_with_abs: list[dict[str, tuple[float, ...]]],
):
    def addAbsoluteMeasurementsSquared(data_entry: dict[str, tuple[float, ...]]):
        clone = copy.deepcopy(data_entry)
        clone["total_grav_sq"] = (
            data_entry["absolute_measurements"][0] ** 2
            + data_entry["absolute_measurements"][1] ** 2
            + data_entry["absolute_measurements"][2] ** 2,
        )
        return clone

    data_with_total_grav_sq: list[dict[str, tuple[float, ...]]] = [
        addAbsoluteMeasurementsSquared(data_entry) for data_entry in data_with_abs
    ]
    return data_with_total_grav_sq


def calculateGravityDiffs(data_with_total_grav_sq: list[dict[str, tuple[float, ...]]]):
    data_with_grav_diffs: list[dict[str, tuple[float, ...]]] = []
    if len(data_with_total_grav_sq) == 0:
        return []
    elif len(data_with_total_grav_sq) == 1:
        entry = copy.deepcopy(data_with_total_grav_sq[0])
        if not "measurement_diffs" in entry:
            entry["measurement_diffs"] = (
                entry["measurements"][0],
                entry["measurements"][1],
                entry["measurements"][2],
            )
        data_with_grav_diffs.append(entry)
    else:
        for i in range(0, len(data_with_total_grav_sq)):
            entry = copy.deepcopy(data_with_total_grav_sq[i])
            if not "measurement_diffs" in entry:
                if i == 0:
                    entry["measurement_diffs"] = (
                        entry["measurements"][0],
                        entry["measurements"][1],
                        entry["measurements"][2],
                    )
                else:
                    previousEntry = data_with_grav_diffs[-1]
                    entry["measurement_diffs"] = (
                        previousEntry["measurements"][0] - entry["measurements"][0],
                        previousEntry["measurements"][1] - entry["measurements"][1],
                        previousEntry["measurements"][2] - entry["measurements"][2],
                    )
            data_with_grav_diffs.append(entry)
    return data_with_grav_diffs


def calculateTotalGravDiffsSquared(
    data_with_grav_diffs: list[dict[str, tuple[float, ...]]],
):
    def addTotalGravDiffs(data_entry: dict[str, tuple[float, ...]]):
        clone = copy.deepcopy(data_entry)
        clone["total_grav_diffs_sq"] = (
            data_entry["measurement_diffs"][0] ** 2
            + data_entry["measurement_diffs"][1] ** 2
            + data_entry["measurement_diffs"][2] ** 2,
        )
        return clone

    data_with_total_grav_diffs_sq: list[dict[str, tuple[float, ...]]] = [
        addTotalGravDiffs(data_entry) for data_entry in data_with_grav_diffs
    ]
    return data_with_total_grav_diffs_sq


def calculateAverageTotalGravSquaredDiffs(
    data_with_total_grav_diffs_sq: list[dict[str, tuple[float, ...]]],
    backtracks: int,
):
    total_grav_squared_diff: float = 0.0
    start = max(len(data_with_total_grav_diffs_sq) - backtracks, 0)
    for i in range(start, len(data_with_total_grav_diffs_sq)):
        total_grav_squared_diff = (
            total_grav_squared_diff
            + data_with_total_grav_diffs_sq[i]["total_grav_diffs_sq"][0]
        )
    avg = total_grav_squared_diff / (len(data_with_total_grav_diffs_sq) - start)
    return avg


def calculateAbsDiffsToPrevious(
    data_with_total_grav_diffs_squared: list[dict[str, tuple[float, ...]]]
):
    if len(data_with_total_grav_diffs_squared) == 0:
        return (0, 0, 0, 0)
    elif len(data_with_total_grav_diffs_squared) == 1:
        x, y, z = data_with_total_grav_diffs_squared[0].get(
            "measurement_diffs", (0, 0, 0)
        )
        sum = abs(x) + abs(y) + abs(z)
        return (abs(x), abs(y), abs(z), sum)
    else:
        x1, y1, z1 = data_with_total_grav_diffs_squared[-1].get(
            "measurement_diffs", (0, 0, 0)
        )
        x2, y2, z2 = data_with_total_grav_diffs_squared[-2].get(
            "measurement_diffs", (0, 0, 0)
        )
        sum = (abs(x1) + abs(y1) + abs(z1)) - (abs(x2) + abs(y2) + abs(z2))
        return (abs(x1 - x2), abs(y1 - y2), abs(z1 - z2), abs(sum))


def updateState(time: int, measurements: tuple[float, float, float]):
    # tag::updateState-history[]
    if history.full():
        history.get()  # Remove one item from the queue
    history.put((time, measurements))
    # Filter out any entries that are older than maxage
    pops = 0
    for entry_time, _ in history.queue:
        if time - entry_time > maxage:
            pops += 1
    for i in range(0, pops):
        history.get()
    # end::updateState-history[]

    # tag::updateState-absDiffs[]
    data_with_abs: list[dict[str, tuple[float, ...]]] = [
        {
            "time": (float(entry_time),),
            "measurements": entry_measurements,
            "absolute_measurements": (
                abs(entry_measurements[0]),
                abs(entry_measurements[1]),
                abs(entry_measurements[2]),
            ),
        }
        for entry_time, entry_measurements in history.queue
    ]

    data_with_grav_diffs = calculateGravityDiffs(data_with_abs)
    abs_diffs_to_previous = calculateAbsDiffsToPrevious(data_with_grav_diffs)
    if (
        abs_diffs_to_previous[0] >= 1.1
        or abs_diffs_to_previous[1] >= 1.1
        or abs_diffs_to_previous[2] >= 1.1
        or abs_diffs_to_previous[3] >= 2.2
    ):
        return "Rolling"
    # end::updateState-absDiffs[]

    # tag::updateState-totalAcceleration[]
    # Check whether the total acceleration has been changing. This can be a simple way to detect whether the die is laying on its face.
    def addSummedAbsMeasurements(data_entry: dict[str, tuple[float, ...]]):
        clone = copy.deepcopy(data_entry)
        clone["summed_abs_measurements"] = (
            data_entry["absolute_measurements"][0]
            + data_entry["absolute_measurements"][1]
            + data_entry["absolute_measurements"][2],
        )
        return clone

    data_with_abs_summed: list[dict[str, tuple[float, ...]]] = [
        addSummedAbsMeasurements(data_entry) for data_entry in data_with_grav_diffs
    ]
    max_abs_diff = calculateMaxAbsDiffs(
        data_with_abs_summed, backtracks=min(2, max_backtracks)
    )
    if max_abs_diff < 0.01:
        return "OnFace"
    # end::updateState-totalAcceleration[]

    # tag::updateState-totalGravitySquared[]
    # Calculate the squared accumulated gravity for each entry
    data_with_total_grav_sq = calculateTotalGravitySquared(data_with_abs_summed)
    if (
        data_with_total_grav_sq[-1]["total_grav_sq"][0] >= 1.0
        and data_with_total_grav_sq[-1]["total_grav_sq"][0] < 1.11
    ):
        return "OnFace"
    # end::updateState-totalGravitySquared[]

    # tag::updateState-measurementDiffs[]
    data_with_total_grav_diffs_squared = calculateTotalGravDiffsSquared(
        data_with_grav_diffs
    )
    if data_with_total_grav_diffs_squared[-1]["total_grav_diffs_sq"][0] == 0:
        return "OnFace"
    elif (
        len(data_with_total_grav_diffs_squared) >= 2
        and data_with_total_grav_diffs_squared[-1]["total_grav_diffs_sq"][0] <= 0.3
        and data_with_total_grav_diffs_squared[-2]["total_grav_diffs_sq"][0] <= 0.3
    ):
        return "Handling"
    elif data_with_total_grav_diffs_squared[-1]["total_grav_diffs_sq"][0] >= 3.5:
        return "Rolling"
    # end::updateState-measurementDiffs[]

    # tag::updateState-totalGravitySquaredDiffs[]
    avg_grav_squared_diffs = calculateAverageTotalGravSquaredDiffs(
        data_with_total_grav_diffs_squared, max_backtracks
    )
    if avg_grav_squared_diffs >= 1.0:
        return "Rolling"
    elif avg_grav_squared_diffs <= 0.35:
        return "Handling"
    # end::updateState-totalGravitySquaredDiffs[]

    # tag::updateState-finalCase[]
    return "Rolling"
    # end::updateState-finalCase[]
