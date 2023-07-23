from queue import Queue

max_backtracks: int
history: Queue
maxage: int


def initialize(max_backtracking: int = 2, max_age_in_millis: int = 10000):
    global max_backtracks, history, maxage
    max_backtracks = max_backtracking
    history = Queue(maxsize=max_backtracking)
    maxage = max_age_in_millis


def calculateMaxAbsDiffsInQueue(
    data_with_abs: list[dict[str, tuple[float, ...]]],
    backtracks: int,
):
    max_abs_diff: float = 0.0
    start = max(len(data_with_abs) - backtracks, 1)
    for i in range(start, len(data_with_abs)):
        abs_diff: float = abs(
            data_with_abs[i]["summed_abs_measurements"][0]
            - data_with_abs[i - 1]["summed_abs_measurements"][0]
        )
        if abs_diff > max_abs_diff:
            max_abs_diff = abs_diff
    return max_abs_diff


def updateState(time: int, measurements: tuple[float, float, float]):
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

    # Check whether the total acceleration has been changing. This can be a simple way to detect whether the die is laying on its face.
    data_with_abs_tmp: list[dict[str, tuple[float, ...]]] = [
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
    data_with_abs: list[dict[str, tuple[float, ...]]] = [
        {
            "time": data_entry["time"],
            "measurements": data_entry["measurements"],
            "absolute_measurements": data_entry["absolute_measurements"],
            "summed_abs_measurements": (
                data_entry["absolute_measurements"][0]
                + data_entry["absolute_measurements"][1]
                + data_entry["absolute_measurements"][2],
            ),
        }
        for data_entry in data_with_abs_tmp
    ]

    max_abs_diff = calculateMaxAbsDiffsInQueue(
        data_with_abs, backtracks=min(2, max_backtracks)
    )
    if max_abs_diff < 0.01:
        return "OnFace"

    return "Unknown"
