# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import datetime
import inspect
import json
import unittest

import orjson_pydantic

SIMPLE_TYPES = (1, 1.0, -1, None, "str", True, False)


def default(obj):
    return str(obj)


class ApiTests(unittest.TestCase):
    def test_loads_trailing(self):
        """
        loads() handles trailing whitespace
        """
        self.assertEqual(orjson_pydantic.loads("{}\n\t "), {})

    def test_loads_trailing_invalid(self):
        """
        loads() handles trailing invalid
        """
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, "{}\n\t a")

    def test_simple_json(self):
        """
        dumps() equivalent to json on simple types
        """
        for obj in SIMPLE_TYPES:
            self.assertEqual(orjson_pydantic.dumps(obj), json.dumps(obj).encode("utf-8"))

    def test_simple_round_trip(self):
        """
        dumps(), loads() round trip on simple types
        """
        for obj in SIMPLE_TYPES:
            self.assertEqual(orjson_pydantic.loads(orjson_pydantic.dumps(obj)), obj)

    def test_loads_type(self):
        """
        loads() invalid type
        """
        for val in (1, 3.14, [], {}, None):
            self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, val)

    def test_loads_recursion(self):
        """
        loads() recursion limit
        """
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, "[" * (1024 * 1024))

    def test_version(self):
        """
        __version__
        """
        self.assertRegex(orjson.__version__, r"^\d+\.\d+(\.\d+)?$")

    def test_valueerror(self):
        """
        orjson_pydantic.JSONDecodeError is a subclass of ValueError
        """
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, "{")
        self.assertRaises(ValueError, orjson_pydantic.loads, "{")

    def test_option_not_int(self):
        """
        dumps() option not int or None
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(True, option=True)

    def test_option_invalid_int(self):
        """
        dumps() option invalid 64-bit number
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(True, option=9223372036854775809)

    def test_option_range_low(self):
        """
        dumps() option out of range low
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(True, option=-1)

    def test_option_range_high(self):
        """
        dumps() option out of range high
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(True, option=1 << 13)

    def test_opts_multiple(self):
        """
        dumps() multiple option
        """
        self.assertEqual(
            orjson_pydantic.dumps(
                [1, datetime.datetime(2000, 1, 1, 2, 3, 4)],
                option=orjson_pydantic.OPT_STRICT_INTEGER | orjson_pydantic.OPT_NAIVE_UTC,
            ),
            b'[1,"2000-01-01T02:03:04+00:00"]',
        )

    def test_default_positional(self):
        """
        dumps() positional arg
        """
        with self.assertRaises(TypeError):
            orjson_pydantic.dumps(__obj={})
        with self.assertRaises(TypeError):
            orjson_pydantic.dumps(zxc={})

    def test_default_unknown_kwarg(self):
        """
        dumps() unknown kwarg
        """
        with self.assertRaises(TypeError):
            orjson_pydantic.dumps({}, zxc=default)

    def test_default_empty_kwarg(self):
        """
        dumps() empty kwarg
        """
        self.assertEqual(orjson_pydantic.dumps(None, **{}), b"null")

    def test_default_twice(self):
        """
        dumps() default twice
        """
        with self.assertRaises(TypeError):
            orjson_pydantic.dumps({}, default, default=default)

    def test_option_twice(self):
        """
        dumps() option twice
        """
        with self.assertRaises(TypeError):
            orjson_pydantic.dumps({}, None, orjson_pydantic.OPT_NAIVE_UTC, option=orjson_pydantic.OPT_NAIVE_UTC)

    def test_option_mixed(self):
        """
        dumps() option one arg, one kwarg
        """

        class Custom:
            def __str__(self):
                return "zxc"

        self.assertEqual(
            orjson_pydantic.dumps(
                [Custom(), datetime.datetime(2000, 1, 1, 2, 3, 4)],
                default,
                option=orjson_pydantic.OPT_NAIVE_UTC,
            ),
            b'["zxc","2000-01-01T02:03:04+00:00"]',
        )

    def test_dumps_signature(self):
        """
        dumps() valid __text_signature__
        """
        self.assertEqual(
            str(inspect.signature(orjson_pydantic.dumps)), "(obj, /, default=None, option=None)"
        )
        inspect.signature(orjson_pydantic.dumps).bind("str")
        inspect.signature(orjson_pydantic.dumps).bind("str", default=default, option=1)

    def test_loads_signature(self):
        """
        loads() valid __text_signature__
        """
        self.assertEqual(str(inspect.signature(orjson_pydantic.loads)), "(obj, /)")
        inspect.signature(orjson_pydantic.loads).bind("[]")

    def test_dumps_module_str(self):
        """
        orjson_pydantic.dumps.__module__ is a str
        """
        self.assertEqual(orjson_pydantic.dumps.__module__, "orjson")

    def test_loads_module_str(self):
        """
        orjson_pydantic.loads.__module__ is a str
        """
        self.assertEqual(orjson_pydantic.loads.__module__, "orjson")

    def test_bytes_buffer(self):
        """
        dumps() trigger buffer growing where length is greater than growth
        """
        a = "a" * 900
        b = "b" * 4096
        c = "c" * 4096 * 4096
        self.assertEqual(
            orjson_pydantic.dumps([a, b, c]), f'["{a}","{b}","{c}"]'.encode("utf-8")
        )
