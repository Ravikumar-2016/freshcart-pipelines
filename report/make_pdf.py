"""Render report/report.html to a PDF with headless Edge and check the page limit.

    python report/make_pdf.py                       # draft: report/build/Pipelines_report_DRAFT.pdf
    python report/make_pdf.py 21CS1234_Ravi         # final: report/build/21CS1234_Ravi_Pipelines.pdf  (RollNo_Name)

{{GITLOG}} in report.html is replaced by the output of `git log --oneline`; {{NAME}} and {{ROLL}} by the arguments.
The body (everything before the element with id="appendix") must be at most 8 pages; the appendix (screenshots) is excluded.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def render(src_html, pdf):
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", f"--user-data-dir={HERE / 'build' / 'edgeprof'}",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", src_html.as_uri()],
                   check=True, capture_output=True, timeout=180)


def pages(pdf):
    return len(re.findall(rb"/Type\s*/Page[^s]", Path(pdf).read_bytes()))


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else None
    roll, _, name = (label or "").partition("_")
    build = HERE / "build"
    build.mkdir(exist_ok=True)
    gitlog = subprocess.run(["git", "log", "--oneline"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    text = (HERE / "report.html").read_text(encoding="utf-8")
    text = text.replace("{{GITLOG}}", html.escape(gitlog)).replace("{{ROLL}}", html.escape(roll or "[roll number]")) \
               .replace("{{NAME}}", html.escape(name.replace("_", " ") if name else "[name]"))
    full_html = HERE / "_render_full.html"
    body_html = HERE / "_render_body.html"
    full_html.write_text(text, encoding="utf-8")
    body_html.write_text(text.split('<div id="appendix"')[0] + "</body></html>", encoding="utf-8")
    out = (HERE / f"{label}_Pipelines.pdf") if label else (build / "Pipelines_report_DRAFT.pdf")
    tmp_body = build / "_body.pdf"
    render(body_html, tmp_body)
    render(full_html, out)
    body_pages, total = pages(tmp_body), pages(out)
    print(f"report body: {body_pages} pages (limit 8, appendix excluded); with screenshot appendix: {total} pages")
    print("written:", out)
    for tmp in (full_html, body_html, tmp_body):
        tmp.unlink(missing_ok=True)
    return 0 if body_pages <= 8 else 1


if __name__ == "__main__":
    sys.exit(main())
