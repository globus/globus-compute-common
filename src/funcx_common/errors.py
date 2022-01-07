class MaxResultSizeExceeded(Exception):
    """
    Result produced by the function exceeds the maximum supported result size
    threshold"""

    def __init__(self, result_size: int, result_size_limit: int):
        self.result_size = result_size
        self.result_size_limit = result_size_limit

    def __str__(self) -> str:
        return (
            f"Task result of {self.result_size}B exceeded current "
            f"limit of {self.result_size_limit}B"
        )
