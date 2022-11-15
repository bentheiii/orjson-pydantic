# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import io
import unittest

import pytest

try:
    import xxhash
except ImportError:
    xxhash = None

import orjson_pydantic


class TypeTests(unittest.TestCase):
    def test_fragment(self):
        """
        orjson_pydantic.JSONDecodeError on fragments
        """
        for val in ("n", "{", "[", "t"):
            self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, val)

    def test_invalid(self):
        """
        orjson_pydantic.JSONDecodeError on invalid
        """
        for val in ('{"age", 44}', "[31337,]", "[,31337]", "[]]", "[,]"):
            self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, val)

    def test_str(self):
        """
        str
        """
        for (obj, ref) in (("blah", b'"blah"'), ("東京", b'"\xe6\x9d\xb1\xe4\xba\xac"')):
            self.assertEqual(orjson_pydantic.dumps(obj), ref)
            self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_str_latin1(self):
        """
        str latin1
        """
        self.assertEqual(orjson_pydantic.loads(orjson_pydantic.dumps("üýþÿ")), "üýþÿ")

    def test_str_long(self):
        """
        str long
        """
        for obj in ("aaaa" * 1024, "üýþÿ" * 1024, "好" * 1024, "�" * 1024):
            self.assertEqual(orjson_pydantic.loads(orjson_pydantic.dumps(obj)), obj)

    def test_str_very_long(self):
        """
        str long enough to trigger overflow in bytecount
        """
        for obj in ("aaaa" * 20000, "üýþÿ" * 20000, "好" * 20000, "�" * 20000):
            self.assertEqual(orjson_pydantic.loads(orjson_pydantic.dumps(obj)), obj)

    def test_str_replacement(self):
        """
        str roundtrip �
        """
        self.assertEqual(orjson_pydantic.dumps("�"), b'"\xef\xbf\xbd"')
        self.assertEqual(orjson_pydantic.loads(b'"\xef\xbf\xbd"'), "�")

    def test_str_surrogates_loads(self):
        """
        str unicode surrogates loads()
        """
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, '"\ud800"')
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, '"\ud83d\ude80"')
        self.assertRaises(orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, '"\udcff"')
        self.assertRaises(
            orjson_pydantic.JSONDecodeError, orjson_pydantic.loads, b'"\xed\xa0\xbd\xed\xba\x80"'
        )  # \ud83d\ude80

    def test_str_surrogates_dumps(self):
        """
        str unicode surrogates dumps()
        """
        self.assertRaises(orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, "\ud800")
        self.assertRaises(orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, "\ud83d\ude80")
        self.assertRaises(orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, "\udcff")
        self.assertRaises(orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, {"\ud83d\ude80": None})
        self.assertRaises(
            orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, b"\xed\xa0\xbd\xed\xba\x80"
        )  # \ud83d\ude80

    @pytest.mark.skipif(
        xxhash is None, reason="xxhash install broken on win, python3.9, Azure"
    )
    def test_str_ascii(self):
        """
        str is ASCII but not compact
        """
        digest = xxhash.xxh32_hexdigest("12345")
        for _ in range(2):
            self.assertEqual(orjson_pydantic.dumps(digest), b'"b30d56b4"')

    def test_bytes_dumps(self):
        """
        bytes dumps not supported
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps([b"a"])

    def test_bytes_loads(self):
        """
        bytes loads
        """
        self.assertEqual(orjson_pydantic.loads(b"[]"), [])

    def test_bytearray_loads(self):
        """
        bytearray loads
        """
        arr = bytearray()
        arr.extend(b"[]")
        self.assertEqual(orjson_pydantic.loads(arr), [])

    def test_memoryview_loads(self):
        """
        memoryview loads
        """
        arr = bytearray()
        arr.extend(b"[]")
        self.assertEqual(orjson_pydantic.loads(memoryview(arr)), [])

    def test_bytesio_loads(self):
        """
        memoryview loads
        """
        arr = io.BytesIO(b"[]")
        self.assertEqual(orjson_pydantic.loads(arr.getbuffer()), [])

    def test_bool(self):
        """
        bool
        """
        for (obj, ref) in ((True, "true"), (False, "false")):
            self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
            self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_bool_true_array(self):
        """
        bool true array
        """
        obj = [True] * 256
        ref = ("[" + ("true," * 255) + "true]").encode("utf-8")
        self.assertEqual(orjson_pydantic.dumps(obj), ref)
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_bool_false_array(self):
        """
        bool false array
        """
        obj = [False] * 256
        ref = ("[" + ("false," * 255) + "false]").encode("utf-8")
        self.assertEqual(orjson_pydantic.dumps(obj), ref)
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_none(self):
        """
        null
        """
        obj = None
        ref = "null"
        self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_null_array(self):
        """
        null array
        """
        obj = [None] * 256
        ref = ("[" + ("null," * 255) + "null]").encode("utf-8")
        self.assertEqual(orjson_pydantic.dumps(obj), ref)
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_nan_dumps(self):
        """
        NaN serializes to null
        """
        self.assertEqual(orjson_pydantic.dumps(float("NaN")), b"null")

    def test_nan_loads(self):
        """
        NaN is not valid JSON
        """
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[NaN]")
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[nan]")

    def test_infinity_dumps(self):
        """
        Infinity serializes to null
        """
        self.assertEqual(orjson_pydantic.dumps(float("Infinity")), b"null")

    def test_infinity_loads(self):
        """
        Infinity, -Infinity is not valid JSON
        """
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[infinity]")
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[Infinity]")
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[-Infinity]")
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads("[-infinity]")

    def test_int_53(self):
        """
        int 53-bit
        """
        for val in (9007199254740991, -9007199254740991):
            self.assertEqual(orjson_pydantic.loads(str(val)), val)
            self.assertEqual(
                orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_STRICT_INTEGER),
                str(val).encode("utf-8"),
            )

    def test_int_53_exc(self):
        """
        int 53-bit exception on 64-bit
        """
        for val in (9007199254740992, -9007199254740992):
            with self.assertRaises(orjson_pydantic.JSONEncodeError):
                orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_STRICT_INTEGER)

    def test_int_53_exc_usize(self):
        """
        int 53-bit exception on 64-bit usize
        """
        for val in (9223372036854775808, 18446744073709551615):
            with self.assertRaises(orjson_pydantic.JSONEncodeError):
                orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_STRICT_INTEGER)

    def test_int_64(self):
        """
        int 64-bit
        """
        for val in (9223372036854775807, -9223372036854775807):
            self.assertEqual(orjson_pydantic.loads(str(val)), val)
            self.assertEqual(orjson_pydantic.dumps(val), str(val).encode("utf-8"))

    def test_uint_64(self):
        """
        uint 64-bit
        """
        for val in (0, 9223372036854775808, 18446744073709551615):
            self.assertEqual(orjson_pydantic.loads(str(val)), val)
            self.assertEqual(orjson_pydantic.dumps(val), str(val).encode("utf-8"))

    def test_int_128(self):
        """
        int 128-bit
        """
        for val in (18446744073709551616, -9223372036854775809):
            self.assertRaises(orjson_pydantic.JSONEncodeError, orjson_pydantic.dumps, val)

    def test_float(self):
        """
        float
        """
        self.assertEqual(-1.1234567893, orjson_pydantic.loads("-1.1234567893"))
        self.assertEqual(-1.234567893, orjson_pydantic.loads("-1.234567893"))
        self.assertEqual(-1.34567893, orjson_pydantic.loads("-1.34567893"))
        self.assertEqual(-1.4567893, orjson_pydantic.loads("-1.4567893"))
        self.assertEqual(-1.567893, orjson_pydantic.loads("-1.567893"))
        self.assertEqual(-1.67893, orjson_pydantic.loads("-1.67893"))
        self.assertEqual(-1.7893, orjson_pydantic.loads("-1.7893"))
        self.assertEqual(-1.893, orjson_pydantic.loads("-1.893"))
        self.assertEqual(-1.3, orjson_pydantic.loads("-1.3"))

        self.assertEqual(1.1234567893, orjson_pydantic.loads("1.1234567893"))
        self.assertEqual(1.234567893, orjson_pydantic.loads("1.234567893"))
        self.assertEqual(1.34567893, orjson_pydantic.loads("1.34567893"))
        self.assertEqual(1.4567893, orjson_pydantic.loads("1.4567893"))
        self.assertEqual(1.567893, orjson_pydantic.loads("1.567893"))
        self.assertEqual(1.67893, orjson_pydantic.loads("1.67893"))
        self.assertEqual(1.7893, orjson_pydantic.loads("1.7893"))
        self.assertEqual(1.893, orjson_pydantic.loads("1.893"))
        self.assertEqual(1.3, orjson_pydantic.loads("1.3"))

    def test_float_precision_loads(self):
        """
        float precision loads()
        """
        self.assertEqual(orjson_pydantic.loads("31.245270191439438"), 31.245270191439438)
        self.assertEqual(orjson_pydantic.loads("-31.245270191439438"), -31.245270191439438)
        self.assertEqual(orjson_pydantic.loads("121.48791951161945"), 121.48791951161945)
        self.assertEqual(orjson_pydantic.loads("-121.48791951161945"), -121.48791951161945)
        self.assertEqual(orjson_pydantic.loads("100.78399658203125"), 100.78399658203125)
        self.assertEqual(orjson_pydantic.loads("-100.78399658203125"), -100.78399658203125)

    def test_float_precision_dumps(self):
        """
        float precision dumps()
        """
        self.assertEqual(orjson_pydantic.dumps(31.245270191439438), b"31.245270191439438")
        self.assertEqual(orjson_pydantic.dumps(-31.245270191439438), b"-31.245270191439438")
        self.assertEqual(orjson_pydantic.dumps(121.48791951161945), b"121.48791951161945")
        self.assertEqual(orjson_pydantic.dumps(-121.48791951161945), b"-121.48791951161945")
        self.assertEqual(orjson_pydantic.dumps(100.78399658203125), b"100.78399658203125")
        self.assertEqual(orjson_pydantic.dumps(-100.78399658203125), b"-100.78399658203125")

    def test_float_edge(self):
        """
        float edge cases
        """
        self.assertEqual(orjson_pydantic.dumps(0.8701), b"0.8701")

        self.assertEqual(orjson_pydantic.loads("0.8701"), 0.8701)
        self.assertEqual(
            orjson_pydantic.loads("0.0000000000000000000000000000000000000000000000000123e50"),
            1.23,
        )
        self.assertEqual(orjson_pydantic.loads("0.4e5"), 40000.0)
        self.assertEqual(orjson_pydantic.loads("0.00e-00"), 0.0)
        self.assertEqual(orjson_pydantic.loads("0.4e-001"), 0.04)
        self.assertEqual(orjson_pydantic.loads("0.123456789e-12"), 1.23456789e-13)
        self.assertEqual(orjson_pydantic.loads("1.234567890E+34"), 1.23456789e34)
        self.assertEqual(orjson_pydantic.loads("23456789012E66"), 2.3456789012e76)

    def test_float_notation(self):
        """
        float notation
        """
        for val in ("1.337E40", "1.337e+40", "1337e40", "1.337E-4"):
            obj = orjson_pydantic.loads(val)
            self.assertEqual(obj, float(val))
            self.assertEqual(orjson_pydantic.dumps(val), ('"%s"' % val).encode("utf-8"))

    def test_list(self):
        """
        list
        """
        obj = ["a", "😊", True, {"b": 1.1}, 2]
        ref = '["a","😊",true,{"b":1.1},2]'
        self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_tuple(self):
        """
        tuple
        """
        obj = ("a", "😊", True, {"b": 1.1}, 2)
        ref = '["a","😊",true,{"b":1.1},2]'
        self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
        self.assertEqual(orjson_pydantic.loads(ref), list(obj))

    def test_dict(self):
        """
        dict
        """
        obj = {"key": "value"}
        ref = '{"key":"value"}'
        self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_dict_duplicate_loads(self):
        self.assertEqual(orjson_pydantic.loads(b'{"1":true,"1":false}'), {"1": False})

    def test_dict_large(self):
        """
        dict with >512 keys
        """
        obj = {"key_%s" % idx: "value" for idx in range(513)}
        self.assertEqual(len(obj), 513)
        self.assertEqual(orjson_pydantic.loads(orjson_pydantic.dumps(obj)), obj)

    def test_dict_large_keys(self):
        """
        dict with keys too large to cache
        """
        obj = {
            "keeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey": "value"
        }
        ref = '{"keeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey":"value"}'
        self.assertEqual(orjson_pydantic.dumps(obj), ref.encode("utf-8"))
        self.assertEqual(orjson_pydantic.loads(ref), obj)

    def test_dict_unicode(self):
        """
        dict unicode keys
        """
        obj = {"🐈": "value"}
        ref = b'{"\xf0\x9f\x90\x88":"value"}'
        self.assertEqual(orjson_pydantic.dumps(obj), ref)
        self.assertEqual(orjson_pydantic.loads(ref), obj)
        self.assertEqual(orjson_pydantic.loads(ref)["🐈"], "value")

    def test_dict_invalid_key_dumps(self):
        """
        dict invalid key dumps()
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps({1: "value"})
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps({b"key": "value"})

    def test_dict_invalid_key_loads(self):
        """
        dict invalid key loads()
        """
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads('{1:"value"}')
        with self.assertRaises(orjson_pydantic.JSONDecodeError):
            orjson_pydantic.loads('{{"a":true}:true}')

    def test_object(self):
        """
        object() dumps()
        """
        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(object())

    def test_dict_similar_keys(self):
        """
        loads() similar keys

        This was a regression in 3.4.2 caused by using
        the implementation in wy instead of wyhash.
        """
        self.assertEqual(
            orjson_pydantic.loads(
                '{"cf_status_firefox67": "---", "cf_status_firefox57": "verified"}'
            ),
            {"cf_status_firefox57": "verified", "cf_status_firefox67": "---"},
        )
