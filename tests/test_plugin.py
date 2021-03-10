from pathlib import Path

from ckanext.nhm.plugin import NHMPlugin


def test_download_modify_email_templates():
    plugin = NHMPlugin()

    original_plain = 'original plain'
    original_html = 'original html'

    base = Path(__file__).parent.parent / 'ckanext' / 'nhm' / 'src' / 'download_emails'
    with (base / 'body.txt').open() as f:
        plain_contents = f.read().strip()
    with (base / 'body.html').open() as f:
        html_contents = f.read().strip()

    plain, html = plugin.download_modify_email_templates(original_plain, original_html)

    assert plain != original_plain
    assert html != original_html
    assert plain == plain_contents
    assert html == html_contents
