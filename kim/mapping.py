from collections import OrderedDict

from .exceptions import MappingError


class Mapping(object):
    """:class:`kim.mapping.Mapping` is a factory for generating data
    structures in KIM.

    Mappings consitst of a collection of key value pairs
    where the key dictates the desired ouput field name and the value is an
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

    Limiting the fields added to a mapping
    --------------------------------------
    When mappings are declared you may optionally limit the fields added
    by using the `only` and `exclude` params passed the a mapping
    instance.

    >>> mapping = Mapping(only=['field_a'])
    >>> mapping = Mapping(exclude=['field_b'])

    Its prefered to only specify one of the parameters at a time.
    The fields defined must be unqiue in each option or a
    :class:`kim.exceptions.MappingError` exception will be raised.

    """

    collection = OrderedDict

    def __init__(self, only=None, exclude=None, **mappings):
        """:class:`kim.mapping.Mapping` constructor.

        :param mapping: field name and field key value pairs.
        :param only: specify an iterable of field_names that may ONLY
                     appear in the mapping.
        :param exclude: specify an iterable of field_names that may MUST
                        not appear in the mapping

        :raises: :class:`kim.exceptions.MappingError`
        """
        self.only = only or list()
        self.only = set(self.only)

        self.exclude = exclude or list()
        self.exclude = set(self.exclude)

        if any(self.only & self.exclude):
            raise MappingError('only and exclude mappings '
                               'must not contain duplicate fields')

        self._mapping = self.collection()
        for field_name, field in mappings.iteritems():
            self.add(field_name, field)

    def mapped(self):
        """Returns the dict like object containing all the
        properties defined in this mapping.

        :rtype: `self.collection`
        :returns: collection of mapped properties
        """
        return self._mapping

    def _add_mapping(self, field_name, field):
        """Stores a mapping by field_name: field in the mapping
        collection class

        :param field_name str: named of this mapped property
        :param field: obj implementing the field interface

        :raises: None
        :returns: None

        """
        self._mapping[field_name] = field

    def add(self, field_name, field):
        """Add a new property to mapping ensuring field_name is
        permitted inside of this mapping.

        :param field_name str: named of this mapped property
        :param field: obj implementing the field interface

        :raises: None
        :returns: None
        """

        if ((self.only and field_name not in self.only) or
                (self.exclude and field_name in self.exclude)):
            return

        self._add_mapping(field_name, field)
