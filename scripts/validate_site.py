#!/usr/bin/env python3
"""Validate every public page of the Axon support site before a push.

Standard library only. Run from anywhere:  python3 scripts/validate_site.py
Exit code 0 = every check passed; 1 = at least one failure (listed).

Public page = any .html file outside cockpit/ and signin/ that is not marked noindex.
For each public page it checks: one h1, title, meta description, canonical
(absolute, matching the page's own address), the Smart App Banner, valid
JSON-LD (Article + FAQPage on guides, FAQ questions visible on the page),
dates that agree (visible date = dateModified = sitemap lastmod), related
links, internal links that resolve, word count, page weight, the mobile
viewport, and banned words (medical-claim words, the founder's name,
non-USD prices). Site-wide it checks the sitemap lists exactly the public
pages, every guide is within two clicks of the home page and one click of
the guides index, every guide has links from other guides, the cockpit and the
AI sign-in page stay noindex with no banner, the sign-in page keeps its
content policy (scripts from this site only, connections to Axon's server
only, no framing script removed) and loads no tracker or storage, and the
Search Console tag is still there.
"""

import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://jaygosalia4.github.io/axon-support/"
APP_ID = "6765889625"
BANNER = f"app-id={APP_ID}"
VERIFICATION = "jQhoEPfLZvFM6E8T0clcdeWSMnvbtUtgvo2PqbN_13c"
PRIVATE_DIRS = ("cockpit", "signin")  # out of search: the dashboard, and the AI sign-in page (Oct 2026)

TITLE_MAX = 70
DESC_MIN, DESC_MAX = 70, 170
MAX_HTML_BYTES = 100_000
MIN_WORDS = {"guide": 600, "ai": 400, "hub": 100}
MIN_RELATED = 3
MIN_GUIDE_INBOUND = 2

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}

# Medical-claim words. A word is allowed only as a disclaimer: a negation
# within the four words before it, in the same clause ("not a diagnosis",
# "don't diagnose", "None of these scores diagnose").
NEGATIONS = {"not", "no", "never", "none", "nor", "without", "don't", "doesn't",
             "isn't", "aren't", "won't", "can't", "cannot", "neither"}
CLAUSE_BREAK = re.compile(r"[.;:!?,()\u2014\u2013]|\s-\s|\b(but|yet|although|though|however)\b", re.I)
CONDITIONS = (r"illness(es)?|diseases?|conditions?|disorders?|insomnia|apnoea|apnea|"
              r"depression|anxiety|symptoms?|injur(y|ies)|infections?|afib|arrhythmias?|"
              r"flu|covid|blood pressure|hypertension|diabetes|cancer")
MEDICAL_PATTERNS = [
    ("diagnose", re.compile(r"\bdiagnos(e|es|ed|ing|is|tic|tics)\b", re.I)),
    ("cure", re.compile(r"\bcur(e|es|ed|ing)\b", re.I)),
    ("heal", re.compile(r"\bheal(s|ed|ing)?\b", re.I)),
    ("treatment", re.compile(r"\btreatments?\b", re.I)),
    # "treat" is fine only as the idiom "treat X as Y" or "treated differently".
    ("treat", re.compile(r"\btreat(s|ed|ing)?\b(?!\s+differently)(?!(\s+[\w'\u2019-]+){0,5}\s+as\b)", re.I)),
    ("prevent <condition>", re.compile(
        r"\bprevent(s|ed|ing)?\s+(\w+\s+){0,3}?(" + CONDITIONS + r")\b", re.I)),
    ("detect <condition>", re.compile(
        r"\b(detect|spot|predict)(s|ed|ing)?\s+(\w+\s+){0,3}?(" + CONDITIONS + r")\b", re.I)),
    ("medical device", re.compile(r"\bmedical[- ](device|grade)\b", re.I)),
    ("clinically proven", re.compile(r"\bclinically[- ](proven|validated|tested)\b", re.I)),
    ("FDA approved", re.compile(r"\bFDA[- ](approved|cleared)\b", re.I)),
]
# Decision D-07: no founder name anywhere in a public page's source
# (text, attributes, comments). The GitHub handle in the site's own
# addresses (jaygosalia4.github.io, github.com/jaygosalia4) is stripped first.
SITE_HANDLE = re.compile(r"jaygosalia4", re.I)
FOUNDER = re.compile(r"(jay|gosalia)", re.I)
SCANNED_ATTRS = ("alt", "title", "aria-label", "content", "placeholder")
NON_USD = re.compile(r"[£€₹¥]|\b(GBP|EUR|INR|AUD|CAD)\b")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metas = []          # attr dicts
        self.links = []          # <link> attr dicts
        self.hrefs = []          # <a href>
        self.ids = set()
        self.h1 = []
        self.jsonld = []         # raw strings
        self.text = []           # visible text chunks
        self.related_hrefs = []
        self.attr_text = []      # alt/title/aria-label/... values
        self.sources_text = []   # text inside the Sources list (citations)
        self.head_metas = []     # metas seen inside <head>
        self.lang = None
        self._in_head = False
        self._sources_depth = None
        self._stack = []
        self._in = {"title": 0, "script": 0, "style": 0, "h1": 0}
        self._jsonld_buf = None
        self._h1_buf = None
        self._related_depth = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "head":
            self._in_head = True
        elif tag == "body":
            self._in_head = False
        for k in SCANNED_ATTRS:
            if a.get(k) and not (tag == "meta" and k == "content"):
                self.attr_text.append(a[k])
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "meta":
            self.metas.append(a)
            if self._in_head:
                self.head_metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
            if self._related_depth is not None:
                self.related_hrefs.append(a["href"])
        if tag in ("meta", "link", "br", "img", "input", "hr"):
            return
        self._stack.append(tag)
        classes = (a.get("class") or "").split()
        if "related" in classes and self._related_depth is None:
            self._related_depth = len(self._stack)
        if "sources" in classes and self._sources_depth is None:
            self._sources_depth = len(self._stack)
        if tag in self._in:
            self._in[tag] += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self._jsonld_buf = []
        if tag == "h1":
            self._h1_buf = []

    def handle_endtag(self, tag):
        if tag in ("meta", "link", "br", "img", "input", "hr"):
            return
        if tag == "head":
            self._in_head = False
        if tag in self._in and self._in[tag]:
            self._in[tag] -= 1
        if tag == "script" and self._jsonld_buf is not None:
            self.jsonld.append("".join(self._jsonld_buf))
            self._jsonld_buf = None
        if tag == "h1" and self._h1_buf is not None:
            self.h1.append(" ".join("".join(self._h1_buf).split()))
            self._h1_buf = None
        if self._stack and self._stack[-1] == tag:
            if self._related_depth == len(self._stack):
                self._related_depth = None
            if self._sources_depth == len(self._stack):
                self._sources_depth = None
            self._stack.pop()

    def handle_data(self, data):
        if self._jsonld_buf is not None:
            self._jsonld_buf.append(data)
            return
        if self._in["title"]:
            self.title += data
            return
        if self._in["script"] or self._in["style"]:
            return
        if self._h1_buf is not None:
            self._h1_buf.append(data)
        self.text.append(data)
        if self._sources_depth is not None:
            self.sources_text.append(data)

    def meta(self, key, value):
        return [m.get("content", "") for m in self.metas if m.get(key) == value]

    def visible_text(self):
        return " ".join(" ".join(self.text).split())

    def prose_text(self):
        """Visible text minus the Sources list: cited titles are other
        people's words (a paper on HRV in anxiety treatment is fine to cite)."""
        text = self.visible_text()
        for chunk in self.sources_text:
            chunk = " ".join(chunk.split())
            if chunk:
                text = text.replace(chunk, " ", 1)
        return text


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def url_for(relpath):
    if relpath == "index.html":
        return BASE
    if relpath.endswith("/index.html"):
        return BASE + relpath[: -len("index.html")]
    return BASE + relpath


def file_for(url):
    """Map a URL on this site to a repo file, or None if it is off-site."""
    url = url.split("#")[0].split("?")[0]
    if not url.startswith(BASE):
        return None
    p = url[len(BASE):]
    if p == "" or p.endswith("/"):
        p += "index.html"
    return p


def kind_of(relpath):
    if relpath.startswith("guides/") and relpath != "guides/index.html":
        return "guide"
    if relpath.startswith("ai/"):
        return "ai"
    return "hub"


def walk_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from walk_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_strings(v)


def graph_items(data):
    items = []
    for d in data if isinstance(data, list) else [data]:
        if isinstance(d, dict) and "@graph" in d:
            items.extend(d["@graph"])
        else:
            items.append(d)
    return items


def medical_hits(text):
    matches = sorted({(m.start(), m.end(), label) for label, pat in MEDICAL_PATTERNS for m in pat.finditer(text)})
    hits, negated_end = [], None
    for start, end, label in matches:
        # A word listed after a negated one keeps the negation:
        # "does not diagnose, treat or cure".
        if negated_end is not None and re.fullmatch(r"\s*(,|,?\s*(or|and|nor))\s*", text[negated_end:start]):
            negated_end = end
            continue
        clause = CLAUSE_BREAK.split(text[max(0, start - 120):start])[-1]
        before = [w.replace("\u2019", "'") for w in re.findall(r"[\w'\u2019]+", clause.lower())[-4:]]
        if NEGATIONS.intersection(before):
            negated_end = end
            continue
        negated_end = None
        hits.append(f'{label}: "…{text[max(0, start - 40):end + 20]}…"')
    return hits


def same_words(s):
    """Compare FAQ text the way a reader sees it: curly and straight quotes alike."""
    return " ".join(s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"').split())


def visible_date(text):
    """The page's "Updated 16 September 2026" / "Published ..." line.
    Returns (iso_date or None, raw phrase or None)."""
    m = re.search(r"\b(?:last )?(?:updated|published)\b[^·<]{0,40}", text, re.I)
    if not m:
        return None, None
    d = re.match(r"(?:last )?(?:updated|published) (\d{1,2}) (" + "|".join(MONTHS) + r") (\d{4})\b",
                 m.group(0), re.I)
    if not d:
        return None, m.group(0).strip()
    month = MONTHS[d.group(2).capitalize()]
    return datetime.date(int(d.group(3)), month, int(d.group(1))).isoformat(), m.group(0).strip()


def main():
    failures = []
    today = datetime.date.today()

    html_files = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("scripts", "node_modules")]
        for f in files:
            if f.endswith(".html"):
                html_files.append(rel(os.path.join(d, f)))
    html_files.sort()

    pages = {}
    for r in html_files:
        try:
            with open(os.path.join(ROOT, r), encoding="utf-8") as fh:
                raw = fh.read()
        except UnicodeDecodeError as e:
            failures.append(f"{r}: not valid UTF-8 ({e})")
            continue
        p = Page()
        p.feed(raw)
        p.raw = raw
        p.size = len(raw.encode("utf-8"))
        pages[r] = p

    def fail(page, msg):
        failures.append(f"{page}: {msg}")

    # --- private pages: cockpit stays out of search and has no banner
    public = []
    for r, p in pages.items():
        robots = " ".join(p.meta("name", "robots")).lower()
        private = r.split("/")[0] in PRIVATE_DIRS
        if private:
            if "noindex" not in robots:
                fail(r, "private page has lost its noindex tag")
            if p.meta("name", "apple-itunes-app"):
                fail(r, "private page must not carry the Smart App Banner")
            continue
        if "noindex" in robots:
            fail(r, "public page is noindex (or move it under cockpit/)")
            continue
        public.append(r)

    # --- sitemap
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    lastmod = {}
    try:
        sm_urls = ET.parse(os.path.join(ROOT, "sitemap.xml")).getroot().findall("s:url", ns)
    except (OSError, ET.ParseError) as e:
        failures.append(f"sitemap.xml: cannot be read ({e})")
        sm_urls = []
    for u in sm_urls:
        loc = u.findtext("s:loc", default="", namespaces=ns).strip()
        lm = u.findtext("s:lastmod", default="", namespaces=ns).strip()
        f = file_for(loc)
        if f is None or f not in pages:
            failures.append(f"sitemap.xml: {loc} does not match a page in the repo")
            continue
        if loc != url_for(f):
            failures.append(f"sitemap.xml: {loc} should be written as its canonical {url_for(f)}")
        if f in lastmod:
            failures.append(f"sitemap.xml: {loc} is listed twice")
        try:
            d = datetime.date.fromisoformat(lm)
            if d > today:
                failures.append(f"sitemap.xml: {loc} lastmod {lm} is in the future")
        except ValueError:
            failures.append(f"sitemap.xml: {loc} lastmod '{lm}' is not a YYYY-MM-DD date")
        lastmod[f] = lm
    for r in public:
        if r not in lastmod:
            fail(r, "public page missing from sitemap.xml")
    for f in lastmod:
        if f not in public:
            failures.append(f"sitemap.xml: lists {f}, which is not a public page")

    # --- home page specifics
    home = pages.get("index.html")
    if home is None or VERIFICATION not in " ".join(home.meta("name", "google-site-verification")):
        fail("index.html", "Google Search Console verification tag is missing or changed")

    # --- per page
    graph = {}
    guide_related = {}
    for r in public:
        p = pages[r]
        kind = kind_of(r)
        url = url_for(r)
        text = p.visible_text()

        if p.lang != "en":
            fail(r, '<html lang="en"> missing')
        if not any("width=device-width" in c for c in p.meta("name", "viewport")):
            fail(r, "mobile viewport meta missing")
        if len(p.h1) != 1 or not p.h1[0]:
            fail(r, f"needs exactly one non-empty h1 (found {len(p.h1)})")
        title = " ".join(p.title.split())
        if not title:
            fail(r, "title missing")
        elif len(title) > TITLE_MAX:
            fail(r, f"title is {len(title)} chars (max {TITLE_MAX}): {title}")
        descs = p.meta("name", "description")
        if len(descs) != 1:
            fail(r, f"needs exactly one meta description (found {len(descs)})")
        elif not DESC_MIN <= len(descs[0]) <= DESC_MAX:
            fail(r, f"description is {len(descs[0])} chars (want {DESC_MIN}–{DESC_MAX})")
        canon = [l.get("href") for l in p.links if l.get("rel") == "canonical"]
        if len(canon) != 1:
            fail(r, f"needs exactly one canonical link (found {len(canon)})")
        elif canon[0] != url:
            fail(r, f"canonical {canon[0]} should be {url}")
        og_url = p.meta("property", "og:url")
        if og_url and og_url != [url]:
            fail(r, f"og:url {og_url} should be the canonical {url}")
        banners = p.meta("name", "apple-itunes-app")
        head_banners = [m.get("content", "") for m in p.head_metas if m.get("name") == "apple-itunes-app"]
        if len(banners) != 1 or not re.fullmatch(re.escape(BANNER) + r"(\s*,.*)?", banners[0].strip()):
            fail(r, f'Smart App Banner should be exactly one <meta name="apple-itunes-app" content="{BANNER}"> (found {banners})')
        elif len(head_banners) != 1:
            fail(r, "Smart App Banner must sit inside <head>")
        for href in p.hrefs:
            m = re.search(r"apps\.apple\.com/(?:[a-z]{2}/)?app/(?:apple-store|axon[^/]*)/id(\d+)", href)
            if m and m.group(1) != APP_ID:
                fail(r, f"Axon App Store link uses id{m.group(1)}, banner uses id{APP_ID}")
        if p.size > MAX_HTML_BYTES:
            fail(r, f"page weighs {p.size} bytes (max {MAX_HTML_BYTES})")

        words = len(re.findall(r"[A-Za-z0-9][\w'’-]*", text))
        if words < MIN_WORDS[kind]:
            fail(r, f"{words} words (min {MIN_WORDS[kind]} for a {kind} page)")

        # JSON-LD
        ld_types, ld_strings, article, faq = set(), [], None, None
        for blob in p.jsonld:
            try:
                data = json.loads(blob)
            except json.JSONDecodeError as e:
                fail(r, f"JSON-LD does not parse: {e}")
                continue
            for it in graph_items(data):
                t = it.get("@type") if isinstance(it, dict) else None
                ld_types.add(t)
                if t == "Article":
                    article = it
                elif t == "FAQPage":
                    faq = it
            ld_strings.extend(walk_strings(data))
        if kind in ("guide", "ai"):
            for need in ("Article", "FAQPage"):
                if need not in ld_types:
                    fail(r, f"JSON-LD has no {need}")
        if article:
            for k in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "mainEntityOfPage"):
                if not article.get(k):
                    fail(r, f"Article JSON-LD missing {k}")
            for who in ("author", "publisher"):
                if isinstance(article.get(who), dict) and article[who].get("@type") != "Organization":
                    fail(r, f"Article {who} must be the Organization 'Axon', not a person")
            if article.get("mainEntityOfPage") and article["mainEntityOfPage"] != url:
                fail(r, f"Article mainEntityOfPage should be {url}")
            dm, dp = str(article.get("dateModified", "")), str(article.get("datePublished", ""))
            for k, v in (("datePublished", dp), ("dateModified", dm)):
                if v and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    fail(r, f"Article {k} '{v}' is not a YYYY-MM-DD date")
            if r in lastmod and dm and lastmod[r] != dm:
                fail(r, f"sitemap lastmod {lastmod[r]} != JSON-LD dateModified {dm}")
            if dp > dm:
                fail(r, "datePublished is after dateModified")
        if kind in ("guide", "ai"):
            vd, phrase = visible_date(text)
            if phrase is None:
                fail(r, 'no visible "Updated D Month YYYY" (or "Published …") line')
            elif vd is None:
                fail(r, f'visible date "{phrase}" should read like "Updated 16 September 2026"')
            elif article and vd != str(article.get("dateModified", "")):
                fail(r, f"visible date {vd} != JSON-LD dateModified {article.get('dateModified')}")
        if faq:
            entries = faq.get("mainEntity", [])
            entries = [entries] if isinstance(entries, dict) else entries if isinstance(entries, list) else []
            entries = [e for e in entries if isinstance(e, dict)]
            if not entries:
                fail(r, "FAQPage has no questions")
            for e in entries:
                q = str(e.get("name", ""))
                if not q or same_words(q) not in same_words(text):
                    fail(r, f'FAQ question not visible on the page: "{q}"')
                ans = e.get("acceptedAnswer")
                if not (isinstance(ans, dict) and ans.get("text")):
                    fail(r, f'FAQ question has no answer text: "{q}"')

        # Words that must never appear
        meta_text = " ".join([title] + descs + p.meta("property", "og:title") + p.meta("property", "og:description"))
        for where, blob in (("page", p.prose_text()), ("meta", meta_text), ("attributes", " · ".join(p.attr_text)),
                            ("JSON-LD", " · ".join(ld_strings))):
            for hit in medical_hits(blob):
                fail(r, f"medical-claim wording in {where} — {hit}")
        for where, blob in (("page", text), ("meta", meta_text), ("JSON-LD", " · ".join(ld_strings))):
            for m in NON_USD.finditer(blob):
                fail(r, f'non-USD currency in {where}: "…{blob[max(0, m.start() - 30):m.end() + 30]}…"')
        source = SITE_HANDLE.sub("", p.raw)
        for m in FOUNDER.finditer(source):
            line = source.count("\n", 0, m.start()) + 1
            fail(r, f'founder name in the page source, line {line}: "…{source[max(0, m.start() - 30):m.end() + 30].strip()}…"')

        # Internal links resolve; build the link graph
        out = set()
        for href in p.hrefs:
            if href.startswith(("mailto:", "tel:")):
                continue
            absu = urljoin(url, href)
            target = file_for(absu)
            if target is None:
                continue
            frag = urlsplit(absu).fragment
            if target not in pages:
                if not os.path.isfile(os.path.join(ROOT, target)):
                    fail(r, f"broken internal link {href}")
                continue
            if frag and frag not in pages[target].ids:
                fail(r, f"link {href} points at a missing #{frag}")
            if target != r:
                out.add(target)
        graph[r] = out

        if kind == "guide":
            related = set()
            for href in p.related_hrefs:
                t = file_for(urljoin(url, href))
                if t and kind_of(t) == "guide" and t != r:
                    related.add(t)
            guide_related[r] = related
            if len(related) < MIN_RELATED:
                fail(r, f"Related guides box links {len(related)} other guides (min {MIN_RELATED})")

    # --- site structure: click depth and guide-to-guide links
    def depth_from(start):
        seen, frontier, d = {start: 0}, [start], 0
        while frontier:
            d += 1
            nxt = []
            for n in frontier:
                for t in graph.get(n, ()):
                    if t not in seen:
                        seen[t] = d
                        nxt.append(t)
            frontier = nxt
        return seen

    from_home = depth_from("index.html")
    from_index = depth_from("guides/index.html")
    guides = [r for r in public if kind_of(r) == "guide"]
    for r in public:
        if from_home.get(r, 99) > 2:
            fail(r, f"{from_home.get(r, 'no')} clicks from the home page (max 2)")
    for r in guides:
        if from_index.get(r, 99) > 1:
            fail(r, "not linked directly from the guides index")
        inbound = sum(1 for g in guides if g != r and r in graph.get(g, ()))
        if inbound < MIN_GUIDE_INBOUND:
            fail(r, f"only {inbound} other guides link here (min {MIN_GUIDE_INBOUND})")

    # --- the AI sign-in page: a one-time code is typed here, so nothing else may run on it
    signin = pages.get("signin/index.html")
    if signin is None:
        failures.append("signin/index.html: missing")
    else:
        csp = " ".join(signin.raw and re.findall(r'http-equiv="Content-Security-Policy" content="([^"]+)"', signin.raw))
        for part in ("default-src 'none'", "script-src 'self'", "connect-src https://qnpnvdainbakygnnktrn.supabase.co;", "form-action 'none'", "base-uri 'none'"):
            if part not in csp:
                fail("signin/index.html", f"content policy lost {part!r}")
        if re.search(r"<script[^>]+src=\"(https?:)?//", signin.raw):
            fail("signin/index.html", "loads a script from another site")
        if 'name="referrer" content="no-referrer"' not in signin.raw:
            fail("signin/index.html", "lost its no-referrer policy")
        try:
            with open(os.path.join(ROOT, "signin", "signin.js"), encoding="utf-8") as fh:
                js = fh.read()
        except OSError:
            js = ""
            failures.append("signin/signin.js: missing")
        for banned, why in (("localStorage", "storage"), ("sessionStorage", "storage"), ("document.cookie", "cookies"),
                            ("gtag", "a tracker"), ("posthog", "a tracker"), ("innerHTML =", "HTML from data")):
            if banned in js and not (banned == "innerHTML =" and 'document.documentElement.innerHTML = ""' in js and js.count("innerHTML") == 1):
                fail("signin/signin.js", f"uses {why} ({banned})")
        if "window.top !== window.self" not in js:
            fail("signin/signin.js", "lost its frame check")

    # --- report
    print(f"Axon support site — {len(public)} public pages, {len(pages) - len(public)} private (cockpit, signin)")
    print(f"{'page':<62}{'words':>6}{'KB':>6}{'clicks':>7}  lastmod")
    for r in public:
        p = pages[r]
        words = len(re.findall(r"[A-Za-z0-9][\w'’-]*", p.visible_text()))
        print(f"{r:<62}{words:>6}{p.size / 1024:>6.1f}{from_home.get(r, '-'):>7}  {lastmod.get(r, '-')}")
    if failures:
        print(f"\nFAIL — {len(failures)} problem(s):")
        for f in failures:
            print("  ✗", f)
        return 1
    print("\nPASS — every check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
