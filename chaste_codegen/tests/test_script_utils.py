import logging
import os
import random

from chaste_codegen._script_utils import write_file


# Show more logging output
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_svae_reload(tmp_path):
    """ Check save_np_to_file works as expected """
    file_name = os.path.join(tmp_path, "random data.txt")
    file_contents = str([random.random() for _ in range(1000)])
    write_file(file_name, file_contents)
    assert open(file_name, 'r').read() == file_contents
