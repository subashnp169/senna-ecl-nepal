"""Convert the ECL user guide markdown to PDF using fpdf2."""

from __future__ import annotations

import os
import re
from fpdf import FPDF

SRC = os.path.join(os.path.dirname(__file__), "..", "docs", "user-guide", "ecl-guide.md")
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "user-guide", "ecl-guide.pdf")


class GuidePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf", uni=True)
        self.add_font("Arial", "B", "C:/Windows/Fonts/arialbd.ttf", uni=True)
        self.add_font("Arial", "I", "C:/Windows/Fonts/ariali.ttf", uni=True)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_title("SENNA ECL Nepal - User Guide")
        self.set_author("SENNA ECL")
        self.add_page()
        self.set_font("Arial", size=10.5)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"SENNA ECL Nepal - User Guide | Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def title_block(self, text):
        self.set_font("Arial", "B", 16)
        self.set_text_color(31, 56, 100)
        self.multi_cell(0, 9, text)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def heading(self, text, level):
        sizes = {1: 14, 2: 12, 3: 11}
        self.ln(4)
        self.set_font("Arial", "B", sizes.get(level, 11))
        self.set_text_color(31, 56, 100)
        self.multi_cell(0, 7, text)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def paragraph(self, text):
        self.set_font("Arial", size=10.5)
        # handle bold **text**
        self._rich_text(text)
        self.ln(3)

    def bullet(self, text, indent=5):
        self.set_font("Arial", size=10.5)
        x = self.get_x()
        self.set_x(x + indent)
        self.cell(4, 5, "-")
        self._rich_text(text, inline=True)
        self.ln(2)
        self.set_x(x)

    def numbered(self, num, text):
        self.set_font("Arial", size=10.5)
        x = self.get_x()
        self.cell(8, 5, f"{num}.")
        self._rich_text(text, inline=True)
        self.ln(2)
        self.set_x(x)

    def table(self, rows):
        if not rows:
            return
        ncols = len(rows[0])
        widths = [self.w - 20] * ncols
        # distribute widths roughly equally
        avail = self.w - 20
        widths = [avail / ncols] * ncols
        self.set_font("Arial", "B", 9)
        # header
        for i, cell in enumerate(rows[0]):
            self.cell(widths[i], 6, str(cell)[:40], border=1, fill=True)
        self.ln()
        self.set_font("Arial", size=9)
        for row in rows[1:]:
            for i, cell in enumerate(row):
                self.cell(widths[i], 6, str(cell)[:40], border=1)
            self.ln()
        self.ln(2)

    def code(self, text):
        self.add_font("Consolas", "", "C:/Windows/Fonts/consola.ttf", uni=True)
        self.set_font("Consolas", size=9)
        self.set_fill_color(240, 240, 240)
        for line in text.split("\n"):
            self.cell(0, 5, line, fill=True)
            self.ln()
        self.set_fill_color(255, 255, 255)
        self.ln(2)

    def hr(self):
        self.ln(2)
        y = self.get_y()
        self.line(10, y, self.w - 10, y)
        self.ln(4)

    def _rich_text(self, text, inline=False):
        # simple bold handling
        parts = re.split(r"(\*\*[^*]+\*\*)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.set_font("Arial", "B", 10.5)
                self.write(5, part[2:-2])
                self.set_font("Arial", size=10.5)
            else:
                self.write(5, part)
        if not inline:
            self.ln()


def parse_md(text):
    lines = text.split("\n")
    i = 0
    # collect table rows
    def is_table_line(line):
        return line.strip().startswith("|") and line.strip().endswith("|")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,3})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            pdf.heading(m.group(2), level)
            i += 1
            continue

        # horizontal rule
        if stripped == "---" or stripped == "***":
            pdf.hr()
            i += 1
            continue

        # code block
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            pdf.code("\n".join(code_lines))
            i += 1
            continue

        # table
        if is_table_line(stripped):
            table_rows = []
            while i < len(lines) and is_table_line(lines[i].strip()):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                # skip separator rows (---)
                if not all(re.match(r"^[-:]+$", c) for c in row):
                    table_rows.append(row)
                i += 1
            pdf.table(table_rows)
            continue

        # bullet
        if stripped.startswith("- ") or stripped.startswith("* "):
            pdf.bullet(stripped[2:])
            i += 1
            continue

        # numbered list
        m = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if m:
            pdf.numbered(m.group(1), m.group(2))
            i += 1
            continue

        # blockquote
        if stripped.startswith(">"):
            pdf.paragraph(stripped.lstrip("> ").strip())
            i += 1
            continue

        # paragraph
        pdf.paragraph(stripped)
        i += 1


if __name__ == "__main__":
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    pdf = GuidePDF()
    # title from first heading
    first_line = text.split("\n")[0]
    if first_line.startswith("# "):
        pdf.title_block(first_line[2:])
        text = "\n".join(text.split("\n")[1:])
    parse_md(text)
    pdf.output(OUT)
    print("written", OUT)
