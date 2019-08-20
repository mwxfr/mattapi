import sys

import pytest

from mattapi.base.testcase import BaseTest
from mattapi.api import *


class Test(BaseTest):

    @pytest.mark.details(meta="Sample Test experiment", locale=['en-US', 'es-ES', 'ro'],
                                       description="This test is just an experiment for Sample.",
                                       custom_value="banana")
    def run(self):
        find(Pattern('test.png'), Rectangle(0, 0, 100, 100))
        assert True == True, 'Assert message failed'
