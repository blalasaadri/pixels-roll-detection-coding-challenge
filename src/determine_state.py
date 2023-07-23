from queue import Queue

history: Queue
maxage: int


def initialize(max_backtrack: int = 10, max_age_in_millis: int = 10000):
    global history, maxage
    history = Queue(maxsize=max_backtrack)
    maxage = max_age_in_millis


def updateState(time: int, measurements: tuple[float, float, float]):
    if history.full():
        history.get()  # Remove one item from the queue
    history.put((time, measurements))
    return "Unknown"
