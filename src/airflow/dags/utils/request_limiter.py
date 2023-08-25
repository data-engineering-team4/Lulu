import time


class RequestLimiter:
    def __init__(self, max_requests, per_seconds):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self.requests = 0
        self.start_time = time.time()

    def wait_for_request_slot(self):
        if time.time() - self.start_time >= self.per_seconds:
            self.requests = 0
            self.start_time = time.time()

        if self.requests < self.max_requests:
            self.requests += 1
        else:
            time_remaining = self.per_seconds - (time.time() - self.start_time)
            time.sleep(time_remaining)
            self.requests = 0
            self.start_time = time.time() + 1
