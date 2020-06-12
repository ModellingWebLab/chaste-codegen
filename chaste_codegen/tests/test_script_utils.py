import logging
import os
import random

import pytest

from chaste_codegen._script_utils import write_file


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_wrong_params1():
    """ Check save_np_to_file works as expected """
    with pytest.raises(AssertionError, match="Expecting a file path as string"):
        write_file([], [])


def test_wrong_params2():
    """ Check save_np_to_file works as expected """
    with pytest.raises(AssertionError, match="Contents should be a string"):
        write_file("1.txt", [])


def test_svae_reload(tmp_path):
    """ Check save_np_to_file works as expected """
    tmp_path = str(tmp_path)
    file_name = os.path.join(tmp_path, "random_data.txt")
    file_contents = str([random.random() for _ in range(1000)])
    write_file(file_name, file_contents)
    assert open(file_name, 'r').read() == file_contents
