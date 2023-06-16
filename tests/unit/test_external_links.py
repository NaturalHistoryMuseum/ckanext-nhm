from unittest.mock import MagicMock, patch

from requests.exceptions import SSLError, Timeout, HTTPError

from ckanext.nhm.lib.external_links import (
    get_sites,
    RankedTemplateSite,
    Link,
    P10K,
    GBIF,
)


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


class TestPhenome10kSite:
    def test_no_gbif_record(self):
        gbif_mock = MagicMock(return_value=None)
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            links = P10K.get_links({"occurrenceID": "x"})
            assert len(links) == 0

    def test_no_phenome10k_record(self):
        gbif_mock = MagicMock(return_value={"key": "x"})
        p10k_mock = MagicMock(return_value=None)
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            with patch(
                "ckanext.nhm.lib.external_links._get_phenome10k_record", p10k_mock
            ):
                links = P10K.get_links({"occurrenceID": "x"})
                assert len(links) == 0

    def test_with_records(self):
        gbif_mock = MagicMock(return_value={"key": "x"})
        p10k_mock = MagicMock(return_value={"scientific_name": "y", "url": "z"})
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            with patch(
                "ckanext.nhm.lib.external_links._get_phenome10k_record", p10k_mock
            ):
                links = P10K.get_links({"occurrenceID": "x"})
                assert len(links) == 1
                assert links[0].text == "y"
                assert links[0].url == "z"

    def test_catches_gbif_errors(self):
        gbif_mock = MagicMock(side_effect=Timeout())
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            links = P10K.get_links({"occurrenceID": "x"})
            assert len(links) == 0

    def test_catches_phenome10k_errors(self):
        gbif_mock = MagicMock(return_value={"key": "x"})
        p10k_mock = MagicMock(side_effect=SSLError())
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            with patch(
                "ckanext.nhm.lib.external_links._get_phenome10k_record", p10k_mock
            ):
                links = P10K.get_links({"occurrenceID": "x"})
                assert len(links) == 0


class TestGBIFSite:
    def test_record_not_found(self):
        gbif_mock = MagicMock(return_value=None)
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            links = GBIF.get_links({"occurrenceID": "x", "institutionCode": "y"})
            assert len(links) == 0

    def test_record_is_found(self):
        gbif_mock = MagicMock(
            return_value={
                "catalogNumber": "a",
                "key": "b",
                "scientificName": "c",
                "acceptedTaxonKey": "d",
            }
        )
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            links = GBIF.get_links({"occurrenceID": "x", "institutionCode": "y"})
            assert len(links) == 2
            assert links[0] == Link("a", "https://gbif.org/occurrence/b")
            assert links[1] == Link("c", "https://gbif.org/species/d")

    def test_record_institution_code_is_optional(self):
        gbif_mock = MagicMock(return_value=None)
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            GBIF.get_links({"occurrenceID": "x"})
        gbif_mock.assert_called_once_with("x", "NHMUK")

    def test_catches_gbif_errors(self):
        gbif_mock = MagicMock(side_effect=HTTPError())
        with patch("ckanext.nhm.lib.external_links._get_gbif_record", gbif_mock):
            links = GBIF.get_links({"occurrenceID": "x"})
            assert len(links) == 0
