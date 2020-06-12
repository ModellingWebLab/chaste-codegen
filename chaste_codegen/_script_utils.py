import os


def write_file(file_name, file_contents):
    """ Write a file into the given file name

    :param file_name: file name including path
    :param file_contents: a str with the contents of the file to be written
    """

    assert isinstance(file_name, str) and len(file_name) > 0, "Expecting a file path as string"
    assert isinstance(file_contents, str), "Contents should be a string"

    # Make sure the folder we are writing in exists
    path = os.path.dirname(file_name)
    if path != '':
        os.makedirs(path, exist_ok=True)

    # Write the file
    file = open(file_name, 'w')
    file.write(file_contents)
    file.close()
