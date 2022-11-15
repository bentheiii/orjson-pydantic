# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import unittest

import orjson_pydantic

from .util import read_fixture_obj


class AppendNewlineTests(unittest.TestCase):
    def test_dumps_newline(self):
        """
        dumps() OPT_APPEND_NEWLINE
        """
        self.assertEqual(orjson_pydantic.dumps([], option=orjson_pydantic.OPT_APPEND_NEWLINE), b"[]\n")

    def test_twitter_newline(self):
        """
        loads(),dumps() twitter.json OPT_APPEND_NEWLINE
        """
        val = read_fixture_obj("twitter.json.xz")
        self.assertEqual(
            orjson_pydantic.loads(orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_APPEND_NEWLINE)), val
        )

    def test_canada(self):
        """
        loads(), dumps() canada.json OPT_APPEND_NEWLINE
        """
        val = read_fixture_obj("canada.json.xz")
        self.assertEqual(
            orjson_pydantic.loads(orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_APPEND_NEWLINE)), val
        )

    def test_citm_catalog_newline(self):
        """
        loads(), dumps() citm_catalog.json OPT_APPEND_NEWLINE
        """
        val = read_fixture_obj("citm_catalog.json.xz")
        self.assertEqual(
            orjson_pydantic.loads(orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_APPEND_NEWLINE)), val
        )

    def test_github_newline(self):
        """
        loads(), dumps() github.json OPT_APPEND_NEWLINE
        """
        val = read_fixture_obj("github.json.xz")
        self.assertEqual(
            orjson_pydantic.loads(orjson_pydantic.dumps(val, option=orjson_pydantic.OPT_APPEND_NEWLINE)), val
        )
