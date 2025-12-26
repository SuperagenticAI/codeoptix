"""Custom HTML accessibility analyzer - no external dependencies."""

from html.parser import HTMLParser
from pathlib import Path

from codeoptix.linters.base import BaseLinter, LinterIssue, LinterResult, Severity


class HTMLAccessibilityParser(HTMLParser):
    """HTML parser for accessibility analysis."""

    def __init__(self):
        """Initialize parser."""
        super().__init__()
        self.issues = []
        self.current_tag: str | None = None
        self.current_attrs: dict[str, str] = {}
        self.has_main = False
        self.has_nav = False
        self.images_without_alt: list[tuple[int, int]] = []
        self.headings_order: list[tuple[tuple[int, int], int, int]] = []
        self.last_heading_level = 0
        self.html_lang: str | None = None
        self.heading_tags_seen: list[tuple[str, tuple[int, int]]] = []
        self.links_missing_text: list[tuple[int, int, dict[str, str]]] = []
        self.buttons_missing_text: list[tuple[int, int, dict[str, str]]] = []
        self.inputs_missing_label: list[tuple[int, int, dict[str, str]]] = []
        self.labels_by_for: dict[str, tuple[int, int]] = {}
        self.current_data_buffer: list[str] = []
        self.focus_outline_suppressed = False
        self.suspicious_tabindex: list[tuple[int, int, dict[str, str]]] = []
        self.aria_role_issues: list[tuple[int, int, str, str]] = []

    def handle_starttag(self, tag, attrs):
        """Handle start tag."""
        self.current_tag = tag
        self.current_attrs = {k: v for (k, v) in attrs}
        self.current_data_buffer = []

        # Document root and language
        if tag == "html":
            lang = self.current_attrs.get("lang") or self.current_attrs.get("xml:lang")
            if lang:
                self.html_lang = lang.strip()

        # Semantic HTML landmarks
        if tag == "main":
            self.has_main = True
        elif tag == "nav":
            self.has_nav = True

        # Check images
        if tag == "img":
            alt = self.current_attrs.get("alt")
            if alt is None or alt.strip() == "":
                self.images_without_alt.append(self.getpos())

        # Headings and order
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(tag[1])
            self.heading_tags_seen.append((tag, self.getpos()))
            if self.last_heading_level and level > self.last_heading_level + 1:
                self.headings_order.append((self.getpos(), level, self.last_heading_level))
            self.last_heading_level = level

        # Labels
        if tag == "label":
            label_for = self.current_attrs.get("for")
            if label_for:
                self.labels_by_for[label_for] = self.getpos()

        # Inputs that should have labels
        if tag == "input" and self.current_attrs.get("type") not in [
            "hidden",
            "submit",
            "button",
            "image",
        ]:
            input_id = self.current_attrs.get("id")
            if not input_id or input_id not in self.labels_by_for:
                # We will also check aria-label/labelledby via attributes
                self.inputs_missing_label.append(
                    (self.getpos()[0], self.getpos()[1], dict(self.current_attrs))
                )

        # Links and buttons: record for later text/aria checks
        if tag == "a":
            href = self.current_attrs.get("href")
            if href:
                # Will decide missing text after data collected
                self.links_missing_text.append(
                    (self.getpos()[0], self.getpos()[1], dict(self.current_attrs))
                )

        if tag == "button":
            self.buttons_missing_text.append(
                (self.getpos()[0], self.getpos()[1], dict(self.current_attrs))
            )

        # Tabindex heuristics
        tabindex = self.current_attrs.get("tabindex")
        if tabindex is not None:
            try:
                tabindex_val = int(tabindex)
                if tabindex_val > 0 or tabindex_val < -1:
                    self.suspicious_tabindex.append(
                        (self.getpos()[0], self.getpos()[1], dict(self.current_attrs))
                    )
            except ValueError:
                self.suspicious_tabindex.append(
                    (self.getpos()[0], self.getpos()[1], dict(self.current_attrs))
                )

        # Simple ARIA/role checks
        role = self.current_attrs.get("role")
        if role:
            # Example: role="button" on non-interactive element
            if role == "button" and tag not in ("button", "a", "input"):
                self.aria_role_issues.append((self.getpos()[0], self.getpos()[1], tag, role))

    def handle_data(self, data):
        """Handle text data."""
        if self.current_tag:
            self.current_data_buffer.append(data)

    def handle_endtag(self, tag):
        """Handle end tag, used to decide on text content for links/buttons."""
        # Consolidate buffered text
        text_content = "".join(self.current_data_buffer or []).strip()

        if tag == "a":
            if self.links_missing_text:
                _line, _col, attrs = self.links_missing_text[-1]
                # Only flag as missing if no text AND no aria-label
                if not text_content and not attrs.get("aria-label"):
                    # Keep as-is; will be converted to issues later
                    pass
                else:
                    # Remove last entry if it actually had content
                    self.links_missing_text.pop()

        if tag == "button":
            if self.buttons_missing_text:
                _line, _col, attrs = self.buttons_missing_text[-1]
                if text_content or attrs.get("aria-label"):
                    # Button has accessible name; drop from missing list
                    self.buttons_missing_text.pop()

        self.current_tag = None
        self.current_attrs = {}
        self.current_data_buffer = []


class HTMLAccessibilityLinter(BaseLinter):
    """Custom HTML accessibility analyzer - no external dependencies."""

    def __init__(self, config: dict | None = None):
        """Initialize HTML accessibility linter."""
        super().__init__(config)
        self.name = "html-accessibility"

    def is_available(self) -> bool:
        """Always available - pure Python, no dependencies."""
        return True

    def run(self, path: str, files: list[str] | None = None) -> LinterResult:
        """Run HTML accessibility analysis."""
        import time

        start_time = time.time()

        path_obj = Path(path)
        if not path_obj.exists():
            return LinterResult(
                linter=self.name,
                success=False,
                issues=[],
                errors=[f"Path not found: {path}"],
                execution_time=0.0,
            )

        # Find HTML files
        html_files = []
        if path_obj.is_file() and path_obj.suffix in [".html", ".htm"]:
            html_files = [path_obj]
        elif path_obj.is_dir():
            if files:
                html_files = [Path(f) for f in files if Path(f).suffix in [".html", ".htm"]]
            else:
                html_files = list(path_obj.rglob("*.html")) + list(path_obj.rglob("*.htm"))

        if not html_files:
            return LinterResult(
                linter=self.name,
                success=True,
                issues=[],
                errors=["No HTML files found"],
                execution_time=0.0,
            )

        all_issues = []

        for html_file in html_files:
            try:
                with open(html_file, encoding="utf-8") as f:
                    html_content = f.read()

                # Parse HTML
                parser = HTMLAccessibilityParser()
                parser.feed(html_content)

                # Generate issues
                file_issues = self._generate_issues(html_file, parser)
                all_issues.extend(file_issues)

            except Exception as e:
                all_issues.append(
                    LinterIssue(
                        linter=self.name,
                        severity=Severity.MEDIUM,
                        message=f"Failed to parse HTML: {e!s}",
                        file=str(html_file),
                    )
                )

        execution_time = time.time() - start_time

        return LinterResult(
            linter=self.name,
            success=len(all_issues) == 0,
            issues=all_issues,
            errors=[],
            execution_time=execution_time,
        )

    def _generate_issues(
        self, html_file: Path, parser: HTMLAccessibilityParser
    ) -> list[LinterIssue]:
        """Generate accessibility issues from parser results."""
        issues = []

        # Language of page (WCAG 3.1.1)
        if parser.html_lang is None:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Missing lang attribute on <html> element",
                    file=str(html_file),
                    rule_id="A11Y-MISSING-LANG",
                )
            )

        # Semantic HTML landmarks (WCAG 1.3.1 / 2.4.1)
        if not parser.has_main:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Missing <main> element for main content",
                    file=str(html_file),
                    rule_id="A11Y-MISSING-MAIN",
                )
            )

        # Check images without alt text
        for pos in parser.images_without_alt:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.HIGH,
                    message="Image missing alt text or empty alt text",
                    file=str(html_file),
                    line=pos[0],
                    rule_id="A11Y-MISSING-ALT",
                )
            )

        # Check heading order (WCAG 1.3.1)
        for pos, level, last_level in parser.headings_order:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message=f"Heading level {level} skipped (previous was {last_level})",
                    file=str(html_file),
                    line=pos[0],
                    rule_id="A11Y-HEADING-ORDER",
                )
            )

        # Basic heading presence (at least one h1)
        has_h1 = any(tag == "h1" for tag, _pos in parser.heading_tags_seen)
        if not has_h1:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Missing top-level <h1> heading",
                    file=str(html_file),
                    rule_id="A11Y-MISSING-H1",
                )
            )

        # Links without accessible name (WCAG 2.4.4 / 4.1.2)
        for line, _col, attrs in parser.links_missing_text:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Link has no accessible name (no text or aria-label)",
                    file=str(html_file),
                    line=line,
                    rule_id="A11Y-LINK-NO-NAME",
                )
            )

        # Buttons without accessible name (WCAG 4.1.2)
        for line, _col, attrs in parser.buttons_missing_text:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Button has no accessible name (no text or aria-label)",
                    file=str(html_file),
                    line=line,
                    rule_id="A11Y-BUTTON-NO-NAME",
                )
            )

        # Inputs without labels (WCAG 1.3.1 / 3.3.2)
        for line, _col, attrs in parser.inputs_missing_label:
            # If aria-label or aria-labelledby exists, treat as labeled
            if attrs.get("aria-label") or attrs.get("aria-labelledby"):
                continue
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.MEDIUM,
                    message="Form control has no associated label or aria-label",
                    file=str(html_file),
                    line=line,
                    rule_id="A11Y-FORM-NO-LABEL",
                )
            )

        # Tabindex misuse (WCAG 2.1.1 / 2.4.3)
        for line, _col, attrs in parser.suspicious_tabindex:
            tabindex_val = attrs.get("tabindex")
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.LOW,
                    message=f"Suspicious tabindex value '{tabindex_val}' (consider 0 or -1)",
                    file=str(html_file),
                    line=line,
                    rule_id="A11Y-TABINDEX-SUSPICIOUS",
                )
            )

        # Simple ARIA role issues
        for line, _col, tag, role in parser.aria_role_issues:
            issues.append(
                LinterIssue(
                    linter=self.name,
                    severity=Severity.LOW,
                    message=f"Suspicious ARIA role usage: role='{role}' on <{tag}>",
                    file=str(html_file),
                    line=line,
                    rule_id="A11Y-ARIA-ROLE-MISMATCH",
                )
            )

        return issues
