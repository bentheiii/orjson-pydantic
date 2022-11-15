# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import unittest
import uuid

import orjson_pydantic


class UUIDTests(unittest.TestCase):
    def test_uuid_immutable(self):
        """
        UUID objects are immutable
        """
        val = uuid.uuid4()
        with self.assertRaises(TypeError):
            val.int = 1
        with self.assertRaises(TypeError):
            val.int = None

    def test_uuid_int(self):
        """
        UUID.int is a 128-bit integer
        """
        val = uuid.UUID("7202d115-7ff3-4c81-a7c1-2a1f067b1ece")
        self.assertIsInstance(val.int, int)
        self.assertTrue(val.int >= 2 ** 64)
        self.assertTrue(val.int < 2 ** 128)
        self.assertEqual(val.int, 151546616840194781678008611711208857294)

    def test_uuid_overflow(self):
        """
        UUID.int can't trigger errors in _PyLong_AsByteArray
        """
        with self.assertRaises(ValueError):
            uuid.UUID(int=2 ** 128)
        with self.assertRaises(ValueError):
            uuid.UUID(int=-1)

    def test_uuid_subclass(self):
        """
        UUID subclasses are not serialized
        """

        class AUUID(uuid.UUID):
            pass

        with self.assertRaises(orjson_pydantic.JSONEncodeError):
            orjson_pydantic.dumps(AUUID("{12345678-1234-5678-1234-567812345678}"))

    def test_serializes_withopt(self):
        """
        dumps() accepts deprecated OPT_SERIALIZE_UUID
        """
        self.assertEqual(
            orjson_pydantic.dumps(
                uuid.UUID("7202d115-7ff3-4c81-a7c1-2a1f067b1ece"),
                option=orjson_pydantic.OPT_SERIALIZE_UUID,
            ),
            b'"7202d115-7ff3-4c81-a7c1-2a1f067b1ece"',
        )

    def test_nil_uuid(self):
        self.assertEqual(
            orjson_pydantic.dumps(uuid.UUID("00000000-0000-0000-0000-000000000000")),
            b'"00000000-0000-0000-0000-000000000000"',
        )

    def test_all_ways_to_create_uuid_behave_equivalently(self):
        # Note that according to the docstring for the uuid.UUID class, all the
        # forms below are equivalent -- they end up with the same value for
        # `self.int`, which is all that really matters
        uuids = [
            uuid.UUID("{12345678-1234-5678-1234-567812345678}"),
            uuid.UUID("12345678123456781234567812345678"),
            uuid.UUID("urn:uuid:12345678-1234-5678-1234-567812345678"),
            uuid.UUID(bytes=b"\x12\x34\x56\x78" * 4),
            uuid.UUID(
                bytes_le=b"\x78\x56\x34\x12\x34\x12\x78\x56"
                + b"\x12\x34\x56\x78\x12\x34\x56\x78"
            ),
            uuid.UUID(fields=(0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678)),
            uuid.UUID(int=0x12345678123456781234567812345678),
        ]
        result = orjson_pydantic.dumps(uuids)
        canonical_uuids = ['"%s"' % str(u) for u in uuids]
        serialized = ("[%s]" % ",".join(canonical_uuids)).encode("utf8")
        self.assertEqual(result, serialized)

    def test_serializes_correctly_with_leading_zeroes(self):
        instance = uuid.UUID(int=0x00345678123456781234567812345678)
        self.assertEqual(
            orjson_pydantic.dumps(instance),
            ('"%s"' % str(instance)).encode("utf8"),
        )

    def test_all_uuid_creation_functions_create_serializable_uuids(self):
        uuids = (
            uuid.uuid1(),
            uuid.uuid3(uuid.NAMESPACE_DNS, "python.org"),
            uuid.uuid4(),
            uuid.uuid5(uuid.NAMESPACE_DNS, "python.org"),
        )
        for val in uuids:
            self.assertEqual(
                orjson_pydantic.dumps(val),
                f'"{val}"'.encode("utf-8"),
            )
