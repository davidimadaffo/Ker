"""Tests for the chanvre report PDF generator."""
import builtins
import os

import pytest

import road_safety.runners.chanvre_report as cr
import road_safety.main as main_mod


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestReportContent:
    def test_report_content_is_non_empty(self):
        assert len(cr.REPORT_CONTENT) > 0

    def test_all_items_have_heading_and_level(self):
        for item in cr.REPORT_CONTENT:
            assert "heading" in item
            assert "level" in item
            assert isinstance(item["heading"], str)
            assert isinstance(item["level"], int)
            assert 0 <= item["level"] <= 3

    def test_introduction_is_present(self):
        headings = [item["heading"] for item in cr.REPORT_CONTENT]
        assert any("INTRODUCTION" in h for h in headings)

    def test_chapitre_i_is_present(self):
        headings = [item["heading"] for item in cr.REPORT_CONTENT]
        assert any("CHAPITRE I" in h for h in headings)

    def test_chapitre_ii_is_present(self):
        headings = [item["heading"] for item in cr.REPORT_CONTENT]
        assert any("CHAPITRE II" in h for h in headings)

    def test_conclusion_is_present(self):
        headings = [item["heading"] for item in cr.REPORT_CONTENT]
        assert any("CONCLUSION" in h for h in headings)

    def test_bibliographie_is_present(self):
        headings = [item["heading"] for item in cr.REPORT_CONTENT]
        assert any("BIBLIOGRAPHIE" in h for h in headings)

    def test_hypotheses_in_body(self):
        bodies = [item.get("body") or "" for item in cr.REPORT_CONTENT]
        combined = " ".join(bodies)
        assert "H1" in combined
        assert "H2" in combined
        assert "H3" in combined

    def test_no_non_latin1_characters_in_headings(self):
        """All heading strings must be encodable as Latin-1 (fpdf core fonts)."""
        for item in cr.REPORT_CONTENT:
            heading = item["heading"]
            try:
                heading.encode("latin-1")
            except UnicodeEncodeError as exc:
                pytest.fail(f"Non-Latin-1 character in heading '{heading}': {exc}")

    def test_no_non_latin1_characters_in_bodies(self):
        """All body strings must be encodable as Latin-1 (fpdf core fonts)."""
        for item in cr.REPORT_CONTENT:
            body = item.get("body")
            if body is None:
                continue
            try:
                body.encode("latin-1")
            except UnicodeEncodeError as exc:
                pytest.fail(f"Non-Latin-1 character in body: {exc}")


# ---------------------------------------------------------------------------
# generate_report()
# ---------------------------------------------------------------------------


class TestGenerateReport:
    def test_generates_pdf_file(self, tmp_path):
        out = tmp_path / "test_chanvre.pdf"
        result = cr.generate_report(str(out))
        assert result == str(out.resolve())
        assert out.exists()
        assert out.stat().st_size > 1000

    def test_pdf_starts_with_magic_bytes(self, tmp_path):
        out = tmp_path / "chanvre.pdf"
        cr.generate_report(str(out))
        with open(out, "rb") as f:
            header = f.read(4)
        assert header == b"%PDF"

    def test_default_filename(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = cr.generate_report()
        assert result.endswith("rapport_chanvre.pdf")
        assert os.path.exists(result)

    def test_custom_output_path(self, tmp_path):
        custom = tmp_path / "custom_output.pdf"
        result = cr.generate_report(str(custom))
        assert os.path.exists(result)

    def test_returns_absolute_path(self, tmp_path):
        out = tmp_path / "chanvre.pdf"
        result = cr.generate_report(str(out))
        assert os.path.isabs(result)


# ---------------------------------------------------------------------------
# run_chanvre_report()
# ---------------------------------------------------------------------------


class TestRunChanvreReport:
    def test_run_with_explicit_path(self, tmp_path, capsys):
        out = str(tmp_path / "report.pdf")
        cr.run_chanvre_report(out)
        captured = capsys.readouterr()
        assert "Rapport généré" in captured.out
        assert os.path.exists(out)

    def test_run_interactive_default_path(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        # User presses Enter to accept the default filename
        monkeypatch.setattr(builtins, "input", lambda _: "")
        cr.run_chanvre_report(None)
        captured = capsys.readouterr()
        assert "Rapport généré" in captured.out

    def test_run_interactive_custom_path(self, tmp_path, monkeypatch, capsys):
        custom = str(tmp_path / "custom.pdf")
        monkeypatch.setattr(builtins, "input", lambda _: custom)
        cr.run_chanvre_report(None)
        assert os.path.exists(custom)


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


class TestMainChanvreReport:
    def test_main_chanvre_report_command(self, tmp_path, monkeypatch):
        out = str(tmp_path / "rapport.pdf")
        monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "chanvre-report", out])

        called = {"report": 0}

        def fake_run(path):
            called["report"] += 1
            assert path == out

        monkeypatch.setattr(main_mod, "run_chanvre_report", fake_run)
        rc = main_mod.main()
        assert rc == 0
        assert called["report"] == 1

    def test_main_chanvre_report_no_path(self, monkeypatch):
        monkeypatch.setattr(main_mod.sys, "argv", ["road-safety", "chanvre-report"])

        called = {"report": 0}

        def fake_run(path):
            called["report"] += 1
            assert path is None

        monkeypatch.setattr(main_mod, "run_chanvre_report", fake_run)
        rc = main_mod.main()
        assert rc == 0
        assert called["report"] == 1

    def test_main_usage_updated(self, monkeypatch, capsys):
        monkeypatch.setattr(main_mod.sys, "argv", ["road-safety"])
        main_mod.main()
        out = capsys.readouterr().out
        assert "chanvre-report" in out


# ---------------------------------------------------------------------------
# ChanvrePDF internals
# ---------------------------------------------------------------------------


class TestChanvrePDF:
    def test_chanvre_pdf_instantiable(self):
        pdf = cr.ChanvrePDF(orientation="P", unit="mm", format="A4")
        assert pdf is not None

    def test_title_page_adds_page(self):
        pdf = cr.ChanvrePDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.set_margins(left=20, top=20, right=20)
        pdf.add_title_page()
        assert pdf.page_no() == 1

    def test_toc_adds_second_page(self):
        pdf = cr.ChanvrePDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.set_margins(left=20, top=20, right=20)
        pdf.add_title_page()
        pdf.add_toc()
        assert pdf.page_no() >= 2
