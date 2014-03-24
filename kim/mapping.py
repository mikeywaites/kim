from collections import OrderedDict

from .exceptions import MappingError


class Mapping(object):
    """:class:`kim.mapping.Mapping` is a factory for generating data
    structures in kim.

    Mappings consitst of a collection key value pairs
    where a key dictates the desired ouput field name and the value is an
    object that defines the :class:`kim.fields.BaseField` interface.

    The default Mapping class in kim stores collections of mapped properties
    as an OrderedDict, other than that a mapping is roughly equivalent to the
    following

    >>> mapping = {'field_a': my_field}

    Creating mappings
    -----------------

    :class:`kim.mapping.Mapping` may be instantiated in several ways.  You
    may optinally proivide the constructor with **mappings which is a dict
    of 'field_name': field key value pairs, where field implements the field
    interface.

    >>> from kim.mapping import Mapping
    >>> mapping = Mapping(**{'field_one': field})

    One an instance of :class:`kim.mapping.Mapping` has been created you can
    also add fields using the :meth:`kim.mapping.Mapping.add` method.

    >>> from kim.mapping import Mapping
    >>> mapping = Mapping(**{'field_one': field})
    >>> mapping.add('field_two', other_field)

    Getting the mapped properties from a mapping.
    --------------------------------------------

    Once a mapped data structure has been instantiated you may call the
    :meth:`mapped` method to retrieve the mapped field_name/field key value
    pairs

    >>> from kim.mapping import Mapping
    >>> mapping = Mapping(**{'field_one': field})
    >>> mapping.mapped()
    >>> OrderedDict([('field_a', <field String>)])

    """

    collection = OrderedDict

    def __init__(self, **mappings):
        """:class:`kim.mapping.Mapping` constructor.

        :param mapping: field name and field key value pairs.

        """
        self._mapping = self.collection()
        for field_name, field in mappings.iteritems():
            self.add(field_name, field)

    def mapped(self):

        return self._mapping

    def add(self, field_name, field):

        self._mapping[field_name] = field
