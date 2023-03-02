import pickle


def serialize_magic(obj, path_to_file='tmp.dat'):
    with open(path_to_file, 'wb') as file_to_store:
        pickle.dump(obj, file_to_store, protocol=pickle.HIGHEST_PROTOCOL)


def deserialize_magic(path_to_file='tmp.dat'):
    with open(path_to_file, 'rb') as file_to_load:
        return pickle.load(file_to_load)
