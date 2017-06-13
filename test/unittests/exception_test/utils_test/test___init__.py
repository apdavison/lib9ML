import unittest
from nineml.utils.__init__ import (
    LocationMgr, _dispatch_error_func, expect_single,
    invert_dictionary, flatten_first_level, safe_dict, ensure_iterable,
    ensure_valid_identifier)
from nineml.utils.testing.comprehensive import instances_of_all_types
from nineml.exceptions import NineMLRuntimeError


class TestExceptions(unittest.TestCase):

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test__dispatch_error_func_ninemlruntimeerror(self):
        """
        line #: 35
        message: error_func

        context:
        --------
def _dispatch_error_func(error_func, default_error=NineMLRuntimeError()):
    \"\"\"Internal function for dispatching errors.

    This was seperated out because it happens in a lot of utility functions
    \"\"\"

    if error_func:
        if isinstance(error_func, Exception):
            raise error_func
        elif isinstance(error_func, basestring):
        """

        self.assertRaises(
            NineMLRuntimeError,
            _dispatch_error_func,
            error_func=None,
            default_error=NineMLRuntimeError())

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test__dispatch_error_func_ninemlruntimeerror2(self):
        """
        line #: 43
        message: default_error

        context:
        --------
def _dispatch_error_func(error_func, default_error=NineMLRuntimeError()):
    \"\"\"Internal function for dispatching errors.

    This was seperated out because it happens in a lot of utility functions
    \"\"\"

    if error_func:
        if isinstance(error_func, Exception):
            raise error_func
        elif isinstance(error_func, basestring):
            raise NineMLRuntimeError(error_func)
        else:
            error_func()
            internal_error('error_func failed to raise Exception')
    else:
        if isinstance(default_error, Exception):
            raise default_error
        elif isinstance(default_error, basestring):
        """

        self.assertRaises(
            NineMLRuntimeError,
            _dispatch_error_func,
            error_func=None,
            default_error=NineMLRuntimeError())

    def test_expect_single_ninemlruntimeerror(self):
        """
        line #: 98
        message: Object not iterable
        """
        self.assertRaises(
            NineMLRuntimeError,
            expect_single,
            lst=[])
        self.assertRaises(
            NineMLRuntimeError,
            expect_single,
            lst=[1, 2])
        self.assertRaises(
            NineMLRuntimeError,
            expect_single,
            lst=1)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_expect_single_ninemlruntimeerror2(self):
        """
        line #: 102
        message: err

        context:
        --------
def expect_single(lst, error_func=None):
    \"\"\"Retrieve a single element from an iterable.

    This function tests whether an iterable contains just a single element and
    if so returns that element. Otherwise it raises an Exception.

    :param lst: An iterable

    :param error_func: An exception object or a callable. ``error_func`` will
        be raised or called in case there is not exactly one element in
        ``lst``. If ``error_func`` is ``None``, a ``NineMLRuntimeError``
        exception will be raised.

    :rtype: the element in the list, ``lst[0]``, provided ``len(lst)==1``

    >>> expect_single( ['hello'] )
    'hello'

    >>> expect_single( [1] )
    1

    >>> expect_single( [] ) #doctest: +SKIP
    NineMLRuntimeError: expect_single() recieved an iterable of length: 0

    >>> expect_single( [None,None] ) #doctest: +SKIP
    NineMLRuntimeError: expect_single() recieved an iterable of length: 2

    >>> expect_single( [], lambda: raise_exception( RuntimeError('Aggh') ) #doctest: +SKIP  # @IgnorePep8
    RuntimeError: Aggh

    >>> #Slightly more tersly:
    >>> expect_single( [], RuntimeError('Aggh') ) #doctest: +SKIP
    RuntimeError: Aggh

    \"\"\"

    if not _is_iterable(lst):
        raise NineMLRuntimeError('Object not iterable')
    if issubclass(lst.__class__, (dict)):
        err = "Dictionary passed to expect_single. This could be ambiguous"
        err += "\nIf this is what you intended, please explicity pass '.keys' "
        """

        self.assertRaises(
            NineMLRuntimeError,
            expect_single,
            lst=None,
            error_func=None)


    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_invert_dictionary_ninemlruntimeerror(self):
        """
        line #: 324
        message: err

        context:
        --------
def invert_dictionary(dct):
    \"\"\"Takes a dictionary mapping (keys => values) and returns a
    new dictionary mapping (values => keys).
    i.e. given a dictionary::

        {k1:v1, k2:v2, k3:v3, ...}

    it returns a dictionary::

        {v1:k1, v2:k2, v3:k3, ...}

    It checks to make sure that no values are duplicated before converting.
    \"\"\"

    for v in dct.values():
        if not _is_hashable(v):
            err = "Can't invert a dictionary containing unhashable keys"
        """

        self.assertRaises(
            NineMLRuntimeError,
            invert_dictionary,
            dct=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_flatten_first_level_ninemlruntimeerror(self):
        """
        line #: 343
        message: err

        context:
        --------
def flatten_first_level(nested_list):
    \"\"\"Flattens the first level of an iterable, i.e.

        >>> flatten_first_level( [ ['This','is'],['a','short'],['phrase'] ] ) #doctest: +NORMALIZE_WHITESPACE
        ['This', 'is', 'a', 'short', 'phrase']

        >>> flatten_first_level( [ [1,2],[3,4,5],[6] ] ) #doctest: +NORMALIZE_WHITESPACE
        [1,2,3,4,5,6]

    \"\"\"
    if isinstance(nested_list, basestring):
        err = "Shouldn't pass a string to flatten_first_level."
        err += "Use list(str) instead"
        """

        self.assertRaises(
            NineMLRuntimeError,
            flatten_first_level,
            nested_list=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_flatten_first_level_ninemlruntimeerror2(self):
        """
        line #: 347
        message: err

        context:
        --------
def flatten_first_level(nested_list):
    \"\"\"Flattens the first level of an iterable, i.e.

        >>> flatten_first_level( [ ['This','is'],['a','short'],['phrase'] ] ) #doctest: +NORMALIZE_WHITESPACE
        ['This', 'is', 'a', 'short', 'phrase']

        >>> flatten_first_level( [ [1,2],[3,4,5],[6] ] ) #doctest: +NORMALIZE_WHITESPACE
        [1,2,3,4,5,6]

    \"\"\"
    if isinstance(nested_list, basestring):
        err = "Shouldn't pass a string to flatten_first_level."
        err += "Use list(str) instead"
        raise NineMLRuntimeError(err)

    if not _is_iterable(nested_list):
        err = 'flatten_first_level() expects an iterable'
        """

        self.assertRaises(
            NineMLRuntimeError,
            flatten_first_level,
            nested_list=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_flatten_first_level_ninemlruntimeerror3(self):
        """
        line #: 352
        message: err

        context:
        --------
def flatten_first_level(nested_list):
    \"\"\"Flattens the first level of an iterable, i.e.

        >>> flatten_first_level( [ ['This','is'],['a','short'],['phrase'] ] ) #doctest: +NORMALIZE_WHITESPACE
        ['This', 'is', 'a', 'short', 'phrase']

        >>> flatten_first_level( [ [1,2],[3,4,5],[6] ] ) #doctest: +NORMALIZE_WHITESPACE
        [1,2,3,4,5,6]

    \"\"\"
    if isinstance(nested_list, basestring):
        err = "Shouldn't pass a string to flatten_first_level."
        err += "Use list(str) instead"
        raise NineMLRuntimeError(err)

    if not _is_iterable(nested_list):
        err = 'flatten_first_level() expects an iterable'
        raise NineMLRuntimeError(err)

    for nl in nested_list:
        if not _is_iterable(nl):
            err = 'flatten_first_level() expects all arguments to be iterable'
        """

        self.assertRaises(
            NineMLRuntimeError,
            flatten_first_level,
            nested_list=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_safe_dict_ninemlruntimeerror(self):
        """
        line #: 447
        message: err

        context:
        --------
def safe_dict(vals):
    \"\"\" Create a dict, like dict(), but ensure no duplicate keys are given!
    [Python silently allows dict( [(1:True),(1:None)] ) !!\"\"\"
    d = {}
    for k, v in vals:
        if k in vals:
            err = 'safe_dict() failed with duplicated keys: %s' % k
        """

        self.assertRaises(
            NineMLRuntimeError,
            safe_dict,
            vals=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_safe_dict_ninemlruntimeerror2(self):
        """
        line #: 450
        message: Duplicate keys given

        context:
        --------
def safe_dict(vals):
    \"\"\" Create a dict, like dict(), but ensure no duplicate keys are given!
    [Python silently allows dict( [(1:True),(1:None)] ) !!\"\"\"
    d = {}
    for k, v in vals:
        if k in vals:
            err = 'safe_dict() failed with duplicated keys: %s' % k
            raise NineMLRuntimeError(err)
        d[k] = v
    if len(vals) != len(d):
        """

        self.assertRaises(
            NineMLRuntimeError,
            safe_dict,
            vals=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_ensure_iterable_typeerror(self):
        """
        line #: 456
        message: Expected a list, got a dictionary ({})

        context:
        --------
def ensure_iterable(expected_list):
    if isinstance(expected_list, dict):
        """

        self.assertRaises(
            TypeError,
            ensure_iterable,
            expected_list=None)

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_ensure_valid_identifier_ninemlruntimeerror(self):
        """
        line #: 500
        message: Invalid identifier '{}'. Identifiers must start with an alphabetic character, only contain alphnumeric and underscore characters, and end with a alphanumeric character i.e. not start or end with an underscore

        context:
        --------
def ensure_valid_identifier(name):
    if valid_identifier_re.match(name) is None:
        """

        self.assertRaises(
            NineMLRuntimeError,
            ensure_valid_identifier,
            name=None)


class TestLocationMgrExceptions(unittest.TestCase):

    @unittest.skip('Skipping autogenerated unittest skeleton')
    def test_getTmpDir_ninemlruntimeerror(self):
        """
        line #: 405
        message: BinOp(left=Str(s='tmp_dir does not exist:%s'), op=Mod(), right=Attribute(value=Name(id='cls', ctx=Load()), attr='tmp_dir', ctx=Load()))

        context:
        --------
    def getTmpDir(cls):
        if not exists(cls.temp_dir):
        """

        self.assertRaises(
            NineMLRuntimeError,
            LocationMgr.getTmpDir)

