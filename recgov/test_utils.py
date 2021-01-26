from .utils import next_month, this_month, tokenize, represents_int
from datetime import datetime

class TestUtils:
    """Tests utils.

    """
    def test_next_month(self):
        """Next month retuns the first day of the next month.
        """

        d = datetime(2011, 1, 1)
        assert next_month(d) == datetime(2011, 2, 1)


    def test_this_month(self):
        """Next month retuns the first day of the next month.
        """

        d = datetime(2021, 5, 10)
        assert this_month(d) == datetime(2021, 5, 1)

    def test_tokenize(self):
        s = "This is a string"
        assert tokenize(s) == ["This", "is", "a", "string"]

    def test_represents_int(self):
        good="124"
        assert represents_int(good)
        bad="123.14"
        assert not represents_int(bad)