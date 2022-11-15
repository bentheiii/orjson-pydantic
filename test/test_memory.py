# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import dataclasses
import datetime
import gc
import random
import unittest
from typing import List

try:
    import pytz
except ImportError:
    pytz = None  # type: ignore

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore
import orjson_pydantic
import pytest

try:
    import numpy
except ImportError:
    numpy = None  # type: ignore

FIXTURE = '{"a":[81891289, 8919812.190129012], "b": false, "c": null, "d": "東京"}'


def default(obj):
    return str(obj)


@dataclasses.dataclass
class Member:
    id: int
    active: bool


@dataclasses.dataclass
class Object:
    id: int
    updated_at: datetime.datetime
    name: str
    members: List[Member]


DATACLASS_FIXTURE = [
    Object(
        i,
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=random.randint(0, 10000)),
        str(i) * 3,
        [Member(j, True) for j in range(0, 10)],
    )
    for i in range(100000, 101000)
]

MAX_INCREASE = 1048576  # 1MiB


class Unsupported:
    pass


class MemoryTests(unittest.TestCase):
    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_loads(self):
        """
        loads() memory leak
        """
        proc = psutil.Process()
        gc.collect()
        val = orjson_pydantic.loads(FIXTURE)
        mem = proc.memory_info().rss
        for _ in range(10000):
            val = orjson_pydantic.loads(FIXTURE)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_loads_memoryview(self):
        """
        loads() memory leak using memoryview
        """
        proc = psutil.Process()
        gc.collect()
        fixture = FIXTURE.encode("utf-8")
        val = orjson_pydantic.loads(fixture)
        mem = proc.memory_info().rss
        for _ in range(10000):
            val = orjson_pydantic.loads(memoryview(fixture))
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_dumps(self):
        """
        dumps() memory leak
        """
        proc = psutil.Process()
        gc.collect()
        fixture = orjson_pydantic.loads(FIXTURE)
        val = orjson_pydantic.dumps(fixture)
        mem = proc.memory_info().rss
        for _ in range(10000):
            val = orjson_pydantic.dumps(fixture)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_loads_exc(self):
        """
        loads() memory leak exception without a GC pause
        """
        proc = psutil.Process()
        gc.disable()
        mem = proc.memory_info().rss
        n = 10000
        i = 0
        for _ in range(n):
            try:
                orjson_pydantic.loads("")
            except orjson_pydantic.JSONDecodeError:
                i += 1
        assert n == i
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)
        gc.enable()

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_dumps_exc(self):
        """
        dumps() memory leak exception without a GC pause
        """
        proc = psutil.Process()
        gc.disable()
        data = Unsupported()
        mem = proc.memory_info().rss
        n = 10000
        i = 0
        for _ in range(n):
            try:
                orjson_pydantic.dumps(data)
            except orjson_pydantic.JSONEncodeError:
                i += 1
        assert n == i
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)
        gc.enable()

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_dumps_default(self):
        """
        dumps() default memory leak
        """
        proc = psutil.Process()
        gc.collect()
        fixture = orjson_pydantic.loads(FIXTURE)

        class Custom:
            def __init__(self, name):
                self.name = name

            def __str__(self):
                return f"{self.__class__.__name__}({self.name})"

        fixture["custom"] = Custom("orjson")
        val = orjson_pydantic.dumps(fixture, default=default)
        mem = proc.memory_info().rss
        for _ in range(10000):
            val = orjson_pydantic.dumps(fixture, default=default)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_dumps_dataclass(self):
        """
        dumps() dataclass memory leak
        """
        proc = psutil.Process()
        gc.collect()
        val = orjson_pydantic.dumps(DATACLASS_FIXTURE)
        mem = proc.memory_info().rss
        for _ in range(100):
            val = orjson_pydantic.dumps(DATACLASS_FIXTURE)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None or pytz is None,
        reason="psutil install broken on win, python3.9, Azure",
    )
    def test_memory_dumps_pytz_tzinfo(self):
        """
        dumps() pytz tzinfo memory leak
        """
        proc = psutil.Process()
        gc.collect()
        dt = datetime.datetime.now()
        val = orjson_pydantic.dumps(pytz.UTC.localize(dt))
        mem = proc.memory_info().rss
        for _ in range(50000):
            val = orjson_pydantic.dumps(pytz.UTC.localize(dt))
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    def test_memory_loads_keys(self):
        """
        loads() memory leak with number of keys causing cache eviction
        """
        proc = psutil.Process()
        gc.collect()
        fixture = {"key_%s" % idx: "value" for idx in range(1024)}
        self.assertEqual(len(fixture), 1024)
        val = orjson_pydantic.dumps(fixture)
        loaded = orjson_pydantic.loads(val)
        mem = proc.memory_info().rss
        for _ in range(100):
            loaded = orjson_pydantic.loads(val)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)

    @pytest.mark.skipif(
        psutil is None, reason="psutil install broken on win, python3.9, Azure"
    )
    @pytest.mark.skipif(numpy is None, reason="numpy is not installed")
    def test_memory_dumps_numpy(self):
        """
        dumps() dataclass memory leak
        """
        proc = psutil.Process()
        gc.collect()
        fixture = numpy.random.rand(4, 4, 4)
        val = orjson_pydantic.dumps(fixture, option=orjson_pydantic.OPT_SERIALIZE_NUMPY)
        mem = proc.memory_info().rss
        for _ in range(100):
            val = orjson_pydantic.dumps(fixture, option=orjson_pydantic.OPT_SERIALIZE_NUMPY)
        gc.collect()
        self.assertTrue(proc.memory_info().rss <= mem + MAX_INCREASE)
