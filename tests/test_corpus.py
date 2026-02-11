"""Tests for corpus integrity and gold standard infrastructure."""

import json
from pathlib import Path

import pytest

CORPUS_PATH = Path("data/corpus/corpus_500.json")
SCREENING_PATH = Path("data/gold_standard/screening_labels.json")
EXTRACTION_PATH = Path("data/gold_standard/extraction_labels.json")
STATS_PATH = Path("data/gold_standard/corpus_stats.json")


@pytest.fixture
def corpus():
    with open(CORPUS_PATH) as f:
        return json.load(f)


@pytest.fixture
def screening_labels():
    with open(SCREENING_PATH) as f:
        return json.load(f)


@pytest.fixture
def extraction_labels():
    with open(EXTRACTION_PATH) as f:
        return json.load(f)


class TestCorpusIntegrity:
    """Verify corpus meets study design requirements."""

    def test_total_size(self, corpus):
        assert len(corpus["corpus"]) == 500

    def test_composition(self, corpus):
        categories = {}
        for art in corpus["corpus"]:
            cat = art["gold_category"]
            categories[cat] = categories.get(cat, 0) + 1
        assert categories["include"] == 100
        assert categories["exclude"] == 100
        assert categories["ambiguous"] == 300

    def test_unique_pmids(self, corpus):
        pmids = [a["pmid"] for a in corpus["corpus"]]
        assert len(pmids) == len(set(pmids)), "Duplicate PMIDs found"

    def test_unique_corpus_ids(self, corpus):
        ids = [a["corpus_id"] for a in corpus["corpus"]]
        assert len(ids) == len(set(ids)), "Duplicate corpus IDs found"

    def test_corpus_id_format(self, corpus):
        for art in corpus["corpus"]:
            assert art["corpus_id"].startswith("ABS-")
            num = int(art["corpus_id"].split("-")[1])
            assert 1 <= num <= 500

    def test_all_have_abstracts(self, corpus):
        for art in corpus["corpus"]:
            assert art["abstract"].strip(), f"{art['corpus_id']} has empty abstract"

    def test_all_have_titles(self, corpus):
        for art in corpus["corpus"]:
            assert art["title"].strip(), f"{art['corpus_id']} has empty title"

    def test_all_have_pmid(self, corpus):
        for art in corpus["corpus"]:
            assert art["pmid"].isdigit(), f"{art['corpus_id']} has invalid PMID"

    def test_content_hashes_unique(self, corpus):
        hashes = [a["content_hash"] for a in corpus["corpus"]]
        assert len(hashes) == len(set(hashes)), "Duplicate content hashes"

    def test_metadata_present(self, corpus):
        meta = corpus["metadata"]
        assert meta["total"] == 500
        assert meta["composition"]["include"] == 100
        assert meta["composition"]["exclude"] == 100
        assert meta["composition"]["ambiguous"] == 300

    def test_include_articles_have_high_scores(self, corpus):
        for art in corpus["corpus"]:
            if art["gold_category"] == "include":
                assert art["classification"]["inclusion_score"] >= 4

    def test_exclude_articles_have_reasons(self, corpus):
        for art in corpus["corpus"]:
            if art["gold_category"] == "exclude":
                reasons = art["classification"]["exclusion_reasons"]
                assert len(reasons) > 0, f"{art['corpus_id']} excluded without reason"


class TestScreeningLabels:
    """Verify screening gold standard structure."""

    def test_total_matches_corpus(self, screening_labels):
        assert screening_labels["metadata"]["total"] == 500

    def test_all_have_labels(self, screening_labels):
        for label in screening_labels["labels"]:
            assert label["heuristic_label"] in ("include", "exclude", "ambiguous")

    def test_review_count(self, screening_labels):
        needs_review = sum(
            1 for l in screening_labels["labels"] if l["needs_human_review"]
        )
        assert needs_review == 300  # ambiguous need review

    def test_auto_labeled_count(self, screening_labels):
        auto = sum(
            1 for l in screening_labels["labels"] if not l["needs_human_review"]
        )
        assert auto == 200  # include + exclude


class TestExtractionLabels:
    """Verify extraction gold standard structure."""

    def test_only_includes(self, extraction_labels):
        assert extraction_labels["metadata"]["total"] == 100

    def test_template_structure(self, extraction_labels):
        for tmpl in extraction_labels["templates"]:
            assert "extraction" in tmpl
            assert "estimates" in tmpl["extraction"]
            assert len(tmpl["extraction"]["estimates"]) >= 1
            est = tmpl["extraction"]["estimates"][0]
            assert "effect_measure" in est
            assert "effect_estimate" in est
            assert "ci_lower" in est
            assert "ci_upper" in est
