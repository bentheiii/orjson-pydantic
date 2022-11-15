# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import unittest

import orjson_pydantic

from .util import read_fixture_obj


class DictSortKeysTests(unittest.TestCase):
    # citm_catalog is already sorted
    def test_twitter_sorted(self):
        """
        twitter.json sorted
        """
        obj = read_fixture_obj("twitter.json.xz")
        self.assertNotEqual(list(obj.keys()), sorted(list(obj.keys())))
        serialized = orjson_pydantic.dumps(obj, option=orjson_pydantic.OPT_SORT_KEYS)
        val = orjson_pydantic.loads(serialized)
        self.assertEqual(list(val.keys()), sorted(list(val.keys())))

    def test_canada_sorted(self):
        """
        canada.json sorted
        """
        obj = read_fixture_obj("canada.json.xz")
        self.assertNotEqual(list(obj.keys()), sorted(list(obj.keys())))
        serialized = orjson_pydantic.dumps(obj, option=orjson_pydantic.OPT_SORT_KEYS)
        val = orjson_pydantic.loads(serialized)
        self.assertEqual(list(val.keys()), sorted(list(val.keys())))

    def test_github_sorted(self):
        """
        github.json sorted
        """
        obj = read_fixture_obj("github.json.xz")
        for each in obj:
            self.assertNotEqual(list(each.keys()), sorted(list(each.keys())))
        serialized = orjson_pydantic.dumps(obj, option=orjson_pydantic.OPT_SORT_KEYS)
        val = orjson_pydantic.loads(serialized)
        for each in val:
            self.assertEqual(list(each.keys()), sorted(list(each.keys())))

    def test_utf8_sorted(self):
        """
        UTF-8 sorted
        """
        obj = {"a": 1, "ä": 2, "A": 3}
        self.assertNotEqual(list(obj.keys()), sorted(list(obj.keys())))
        serialized = orjson_pydantic.dumps(obj, option=orjson_pydantic.OPT_SORT_KEYS)
        val = orjson_pydantic.loads(serialized)
        self.assertEqual(list(val.keys()), sorted(list(val.keys())))
