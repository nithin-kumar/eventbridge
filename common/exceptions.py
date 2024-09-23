class MaxRetriesReached(Exception):
    def __init__(self, retries, message="Max retries reached"):
        self.retries = retries
        self.message = f"{message} after {retries} attempts."
        super().__init__(self.message)