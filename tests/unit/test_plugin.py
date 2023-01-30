from pathlib import Path

from ckanext.nhm.plugin import NHMPlugin


def test_download_modify_templates():
    plugin = NHMPlugin()

    original_plain = 'original plain'
    original_html = 'original html'

    base = (
        Path(__file__).parent.parent.parent
        / 'ckanext'
        / 'nhm'
        / 'src'
        / 'download_emails'
    )
    with (base / 'start.txt').open() as f:
        plain_start = f.read().strip()
    with (base / 'start.html').open() as f:
        html_start = f.read().strip()
    with (base / 'end.txt').open() as f:
        plain_end = f.read().strip()
    with (base / 'end.html').open() as f:
        html_end = f.read().strip()
    with (base / 'error.txt').open() as f:
        plain_error = f.read().strip()
    with (base / 'error.html').open() as f:
        html_error = f.read().strip()

    (
        plain_start_modified,
        html_start_modified,
    ) = plugin.download_modify_notifier_start_templates(original_plain, original_html)
    assert plain_start_modified != original_plain
    assert html_start_modified != original_html
    assert plain_start_modified == plain_start
    assert html_start_modified == html_start

    (
        plain_end_modified,
        html_end_modified,
    ) = plugin.download_modify_notifier_end_templates(original_plain, original_html)
    assert plain_end_modified != original_plain
    assert html_end_modified != original_html
    assert plain_end_modified == plain_end
    assert html_end_modified == html_end

    (
        plain_error_modified,
        html_error_modified,
    ) = plugin.download_modify_notifier_error_templates(original_plain, original_html)
    assert plain_error_modified != original_plain
    assert html_error_modified != original_html
    assert plain_error_modified == plain_error
    assert html_error_modified == html_error
