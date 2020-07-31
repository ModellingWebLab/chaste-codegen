import os
import random

import pytest

from chaste_codegen._script_utils import write_file


def test_wrong_params1():
    with pytest.raises(AssertionError, match="Expecting a file path as string"):
        write_file([], [])


def test_wrong_params2():
    with pytest.raises(AssertionError, match="Contents should be a string"):
        write_file("1.txt", [])


def test_save_reload(tmp_path):
    tmp_path = str(tmp_path)
    file_name = os.path.join(tmp_path, "random_data.txt")
    file_contents = str([random.random() for _ in range(1000)])
    write_file(file_name, file_contents)
    assert open(file_name, 'r').read() == file_contents
