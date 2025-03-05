import collections
from netpyne.batchtools import RS
from netpyne import specs
from batchtk.runtk import update_config
import collections
def validate(element, container): # is validation important?
    try:
        match container:
            case list(): #container is a list, check validity of index
                assert int(element) < len(container)
            case dict(): #container is a dictionary, check validity of key
                assert element in container
            case _: #invalid container type
                assert element in container
                #raise AttributeError("container type is not supported, cfg attributes support dictionary and "
                #                     "list objects, container {} is of type {}".format(container, type(container)))
    except Exception as e:
        raise AttributeError("error when validating {} within container {}: {}".format(element, container, e))
    return True #element is valid, return True for boolean

def update_items(d, u, force_match = False):
    for k, v in u.items():
        try:
            force_match and validate(k, d)
            if isinstance(v, collections.abc.Mapping): #TODO this will currently break on lists of dicts
                d[k] = update_items(d.get(k), v, force_match)
            else:
                d[k] = v
        except Exception as e:
            raise AttributeError("Error when calling update_items with force_match, item {} does not exist".format(k))
    return d

#RS = get_class()

class Runner_SimConfig(specs.simConfig.SimConfig):
    def __init__(self, *args, **kwargs):
        specs.simConfig.SimConfig.__init__(self, *args, **kwargs)
        self._runner = RS()

    def update(self, simConfigDict=None, force_match=False):  # intended to take `cfg` instance as self
        """
        Updates the SimConfig instance with mappings to the runner, called from a SimConfig instance

        Parameters
        ----------
        self - specs (NetpyneRunner) SimConfig instance
        simConfigDict - optional dictionary to update SimConfig instance (defaults to None)
                      - to be called during initial function call only

        Returns
        -------
        None (updates SimConfig instance in place)
        """
        if simConfigDict:
            update_items(self, simConfigDict, force_match)
        update_config(self.__dict__, **self._runner.mappings)

        #for assign_path, value in self.mappings.items():
        #    try:
        #        set_map(self, assign_path, value)
        #    except Exception as e:
        #        raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))
    def test_mappings(self, mappings):
        """
        Tests mappings for validity

        Parameters
        ----------
        mappings - dictionary of mappings to test

        Returns
        -------
        bool - True if mappings are valid, False otherwise
        """
        for assign_path, value in mappings.items():
            try:
                set_map(self, assign_path, value, force_match=True)
                print("successfully assigned: cfg.{} with value: {}".format(assign_path, value))
            except Exception as e:
                raise Exception("failed on mapping: cfg.{} with value: {}\n{}".format(assign_path, value, e))
        return True

    def get_mappings(self):
        return self._runner.mappings
