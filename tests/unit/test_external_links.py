from unittest.mock import MagicMock

from ckanext.nhm.lib.external_links import get_sites, RankedTemplateSite, Link


class TestGetSites:
    def test_no_collection_code_does_not_fail(self):
        # just call the function and if it raises an exception then it has failed the
        # test
        get_sites({})
        get_sites({"collectionCode": None})

    def test_collection_codes_return_sites(self):
        for code in ["BOT", "MIN", "PAL", "ZOO", "BMNH(E)"]:
            assert len(get_sites({"collectionCode": code})) > 0

    def test_invalid_collection_code_returns_no_sites(self):
        assert len(get_sites({"collectionCode": "bananas"})) == 0


class TestRankedTemplateSite:
    def test_has_rank_data(self):
        template = "beans/{}"
        templated = RankedTemplateSite(MagicMock(), MagicMock(), template)

        record = {
            "kingdom": "a kingdom",
            "family": "a family",
        }
        links = templated.get_links(record)
        assert len(links) == 2
        assert links[0] == Link("a kingdom", template.format("a kingdom"))
        assert links[1] == Link("a family", template.format("a family"))

    def test_no_rank_data(self):
        template = "beans/{}"
        templated = RankedTemplateSite(MagicMock(), MagicMock(), template)

        record = {}
        links = templated.get_links(record)
        assert len(links) == 0
