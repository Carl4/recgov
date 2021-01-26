from .utils import next_month
from datetime import datetime

class TestUtils:
    """Tests utils.

    """
    def test_next_month(self):
        """Next month retuns the first day of the next month.
        """

        d = datetime(2011, 1, 1)
        assert next_month(d) == datetime(2011, 2, 1)

