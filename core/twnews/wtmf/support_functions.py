import pickle
import os
from twnews import defaults


def dump(object, filename, dirname=defaults.TMP_FILE_DIRECTORY, prefix=''):
    filepath = os.path.join(dirname, prefix+filename)

    with open(filepath, 'wb') as file:
        pickle.dump(object, file)


def load(filename, dirname=defaults.TMP_FILE_DIRECTORY, prefix=''):
    filepath = os.path.join(dirname, prefix+filename)

    if exists(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)
    return None


def memo_process(func, filename, dirname=defaults.TMP_FILE_DIRECTORY, try_to_load=False, prefix=''):
    if try_to_load and exists(filename, dirname, prefix=prefix):
        return load(filename, dirname, prefix=prefix)
    result = func()
    dump(result, filename, dirname, prefix=prefix)
    return result


def exists(filename, dirname=defaults.TMP_FILE_DIRECTORY, prefix=''):
    filepath = os.path.join(dirname, prefix+filename)

    return os.path.exists(filepath)