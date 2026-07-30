# Modernization & Learning TODO

A guided, hands-on checklist for turning `idealista_scrape` into a showcase of
modern, idiomatic Python. Every item is tied to **real code in this repo** and
explains the **why**, not just the **what** — the goal is to *learn the patterns*,
then apply them here.

**Legend**
- Priority: **P1** (do first / high impact) · **P2** (solid wins) · **P3** (advanced / stretch)
- Effort: **S** (<30 min) · **M** (~1–2 h) · **L** (half day+)
- `concept` tags point at the Python feature you're practising.

**How to use this doc:** work top-to-bottom within a section; check boxes as you go.
The [Suggested learning order](#suggested-learning-order) at the bottom sequences
the sections into a path. Each "before → after" is a *sketch*, not copy-paste —
type it yourself, that's the point.

---

## 0. What's already good (build on it, don't rewrite)

- ✅ `DatabaseManager` is a genuine **context manager** (`__enter__`/`__exit__`) — `src/db/init.py:12`. We'll *improve* it, not replace it.
- ✅ `src/` layout + editable install (`[tool.setuptools.packages.find]`) — proper packaging.
- ✅ Tests use **pytest fixtures**, `pathlib.Path`, and `pytest.raises` — `tests/conftest.py`, `tests/test_parser.py`.
- ✅ Comprehensions over manual loops in the parser.

The gaps below are *learning opportunities*, not failures.

---

## 1. Quick wins & smells `cleanup`

Low-risk cleanups. Knock these out first to warm up.

- [ ] **Remove unused import** `import random` — `src/scraper/parser.py:3` (ruff `F401`). **P1·S**
- [ ] **Split multi-import line** `import json, tempfile` → two lines — `src/scraper/browser.py:4` (ruff `E401`). **P1·S**
- [ ] **Fix the typo'd constant** `LISBON_FREGUESUAS` → `LISBON_FREGUESIAS` — `src/scraper/constants.py:5` (and its two usages in `urls.py`). **P1·S**
- [ ] **Fix the stray paren** in the error message `"Invalid page)"` — `src/scraper/parser.py:29`. **P1·S**
- [ ] **Fix the broken fixture path bug** — `capture_fixtures.py:6` builds `tests/fixtures/test/fixtures` (`Path(__file__).parent` is *already* `tests/fixtures`, then it appends `"test"/"fixtures"` again). Should be just `Path(__file__).parent`. **P1·S**
- [ ] **Name the magic numbers**: `30` listings/page — `parser.py:17`; backoff `3 * (1 + attempt)` — `main.py:22`; `driver_version=147` — `main.py:62`. Promote to named constants. **P1·S**
- [ ] **Schema/type mismatch (real bug)**: `tags` is a Python `list` in the parser but the column is `tags VARCHAR` while `detail` is `VARCHAR[]` — `src/db/init.py:24` vs `:54`. Decide the type and make both ends agree. **P1·S**
- [ ] **Dead-ish code**: `get_page` (`browser.py:54`) is only used by the fixture-capture script; `smart_get_page` is the real one. Keep them deliberately separate or consolidate. **P2·S**

---

## 2. Project hygiene & tooling `tooling`

Modern Python projects are defined as much by their *tooling* as their code.

- [ ] **Add explicit `__init__.py`** to `src/scraper/` and `src/db/`, or commit to namespace packages on purpose. Right now imports work by accident of the egg-info. Also **rename `src/db/init.py`** → `src/db/database.py` (a module literally named `init.py` reads like `__init__.py` and is confusing). **P1·S** `packaging`
- [ ] **Configure ruff properly.** It's installed but running on defaults (only caught 2 trivial things). Add a real ruleset to `pyproject.toml`: **P1·S** `tooling`
  ```toml
  [tool.ruff]
  target-version = "py311"
  line-length = 100

  [tool.ruff.lint]
  select = ["E", "F", "I", "UP", "B", "SIM", "TCH", "RUF", "PTH"]
  # I=isort, UP=pyupgrade, B=bugbear, SIM=simplify, TCH=type-checking, PTH=use-pathlib
  ```
  Then `uv run ruff check --fix` and `uv run ruff format`.
- [ ] **Add a type checker.** Install `mypy` (or `pyright`/`ty`) as a dev dep and add config. This is the tool that makes Section 3 pay off. **P1·S** `typing`
  ```toml
  [tool.mypy]
  python_version = "3.11"
  strict = true
  ```
- [ ] **Add `pre-commit`** running ruff + mypy on every commit. Industry-standard hygiene. **P2·M** `tooling`
- [ ] **Fill in `pyproject.toml` metadata**: `description` is still "Add your description here". **P3·S**

---

## 3. Add typing everywhere `typing`

The single highest-leverage change. **No function in the codebase has type hints.**
Types are documentation the computer checks for you.

- [ ] **Add `from __future__ import annotations`** at the top of each module so you can use modern syntax (`list[str]`, `X | None`) freely and defer evaluation. **P1·S**
- [ ] **Annotate every function** parameter and return. Start with the pure ones — `src/scraper/urls.py` is trivial and a perfect warm-up:
  ```python
  def make_page_urls(pages: int, freguesia_url: str) -> list[str]: ...
  def get_freguesia(url: str) -> str: ...
  def make_base_urls() -> list[str]: ...
  ```
- [ ] **Use `X | None`, not bare defaults that hide `None`.** `smart_get_page(driver, url, wait=None, timeout=10)` (`browser.py:60`) — `wait` is really a `bool`; type it `wait: bool = False`. `timeout: int = 10`. **P1·S** `PEP 604`
- [ ] **`typing.Final` for constants** — `constants.py`. Signals "do not reassign" and the checker enforces it: **P2·S** `Final`
  ```python
  from typing import Final
  BASE_URL: Final = "https://www.idealista.pt/arrendar-casas"
  LISTINGS_PER_PAGE: Final = 30
  LISBON_FREGUESIAS: Final[tuple[str, ...]] = ("ajuda", "alcantara", ...)  # tuple = immutable
  ```
- [ ] **`typing.Self` (3.11+)** for `DatabaseManager.__enter__` so callers get the precise type back: `def __enter__(self) -> Self:`. **P2·S** `Self`
- [ ] **Learn the typing spectrum on the listing dict.** Before jumping to dataclasses/Pydantic, write the intermediate form so you *feel* the difference — a `TypedDict` gives the dict keys types without changing any runtime behaviour: **P2·M** `TypedDict`
  ```python
  from typing import TypedDict
  class ListingDict(TypedDict):
      id: str; price: str; title: str
      detail: list[str]; tags: list[str]; freguesia: str
  ```
  Then `parse_listings(...) -> list[ListingDict]`. (Section 4 replaces this with a real object — but do this step to understand *why* you'd want to.)

---

## 4. Data modeling: dicts → dataclasses → Pydantic `dataclass` `pydantic`

The listing is passed around as a **stringly-typed dict** (`parser.py:64`, written in
`db/init.py:48`, asserted by key in `test_parser.py:28`). This is *the* place to learn
value objects.

### 4a. `@dataclass` — the standard-library value object
- [ ] **Model the raw scrape result** as a frozen dataclass. You get `__init__`, `__repr__`, `__eq__` for free (those are the dunders a dataclass *generates*): **P1·M** `dataclass` `__repr__` `__eq__`
  ```python
  from dataclasses import dataclass, field

  @dataclass(slots=True, frozen=True)   # slots=faster/less memory; frozen=immutable
  class RawListing:
      id: str
      price: str
      title: str
      freguesia: str
      detail: tuple[str, ...] = field(default_factory=tuple)
      tags: tuple[str, ...] = field(default_factory=tuple)
  ```
  Learn these knobs: `slots=True`, `frozen=True`, `kw_only=True`, `field(default_factory=...)`
  (never use a mutable default like `[]` directly — understand *why* `default_factory` exists).
  > Note: `frozen=True` only makes the object hashable if **all** fields are hashable — that's why `detail`/`tags` are `tuple`, not `list`. A great gotcha to internalize.
- [ ] **`__post_init__` for cheap validation** in the plain-dataclass world (contrast with Pydantic validators in 4b): **P2·S** `__post_init__`
  ```python
  def __post_init__(self) -> None:
      if not self.id:
          raise ValueError("listing id is required")
  ```
- [ ] Update `parse_listings` to build `RawListing` objects and `write_listings` to read attributes (`row.id`) instead of `row["id"]`. Update the test assertion accordingly. **P1·M**

### 4b. Pydantic v2 — validation & parsing at the boundary
You asked specifically for Pydantic. The killer use case here: **price/rooms/sqm are
currently parsed in SQL** (`stg_cleaned_listings.sql` does `REGEXP_REPLACE`). Pydantic
lets you validate and coerce *at ingestion*, so bad data never reaches the DB.

- [ ] **Add `pydantic` (v2) as a dependency** and model the clean listing: **P1·L** `pydantic` `field_validator` `computed_field`
  ```python
  import re
  from pydantic import BaseModel, field_validator, computed_field

  class Listing(BaseModel):
      id: str
      price_raw: str
      title: str
      freguesia: str
      detail: list[str] = []
      tags: list[str] = []

      @field_validator("id", "title")
      @classmethod
      def _not_blank(cls, v: str) -> str:
          if not v.strip():
              raise ValueError("must not be blank")
          return v

      @computed_field            # serialized like a real field
      @property
      def price_eur(self) -> int | None:
          digits = re.sub(r"[^0-9]", "", self.price_raw)
          return int(digits) if digits else None
  ```
  Concepts to practise: `field_validator` (note the `@classmethod` + decorator order),
  `model_validator(mode="after")` for cross-field rules, `computed_field`, and
  `model_dump()` for turning it back into a dict to insert.
- [ ] **Decide the boundary**: validate in Python (Pydantic) *or* in dbt — not both. Moving rooms/sqm/price parsing into the model is a great exercise; document the trade-off (fail-fast at ingestion vs. flexible/re-runnable in SQL). **P2·M**
- [ ] **Compare dataclass vs Pydantic** in a short note in this file once you've done both: when is the stdlib enough, when do you reach for Pydantic? (Spoiler: untrusted/external input → Pydantic.) **P3·S**

---

## 5. Configuration with `pydantic-settings` `pydantic` `config`

Config is read via scattered `os.getenv` calls with **no validation** —
`main.py:45–54`. If `database_name` is missing you get a silent `None` that explodes
later. Inconsistent casing too (`database_name` vs `PROXY_USERNAME`).

- [ ] **Centralize config in a typed Settings object.** This is the idiomatic 2020s pattern: **P1·M** `BaseSettings`
  ```python
  from pydantic import SecretStr
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")

      database_name: str
      schema_name: str
      motherduck_token: SecretStr
      proxy_username: str | None = None
      password: SecretStr | None = None
      domain_name: str | None = None
      port: int | None = None
  ```
  Then `settings = Settings()` once in `main()` and pass it down. Missing/invalid env →
  immediate, descriptive error. Learn `SecretStr` (keeps secrets out of logs/`repr`) and
  `env_file`.
- [ ] **Group the proxy fields** into their own nested model / dataclass (`ProxyConfig`) and pass *one* object to `setup_driver` instead of 5 loose params. **P2·S**

---

## 6. Enums & Literals `enum` `Literal`

Job status is the bare strings `"success"`/`"failure"` (`main.py:27,33`). A typo
(`"sucess"`) would silently corrupt `get_already_scraped`'s filter.

- [ ] **Use `enum.StrEnum` (3.11+)** — behaves like a `str` (works directly in SQL params) but is a closed set: **P2·S** `StrEnum`
  ```python
  from enum import StrEnum
  class JobStatus(StrEnum):
      SUCCESS = "success"
      FAILURE = "failure"
  ```
- [ ] **Alternative to learn**: `Literal["success", "failure"]` as a lightweight type-only constraint — compare it with the enum and note when each fits. **P3·S** `Literal`

---

## 7. Context managers & resource safety `contextlib` `with`

Several leaked resources here — prime context-manager territory.

- [ ] **The Selenium driver is never closed.** `setup_driver` returns a driver (`main.py:60`) that's never `.quit()`-ed — a leaked browser process on every run, including on exceptions. Wrap it: **P1·M** `contextmanager` `__enter__`/`__exit__`
  ```python
  from contextlib import contextmanager

  @contextmanager
  def chrome_driver(config: ProxyConfig | None = None):
      driver = _build_driver(config)
      try:
          yield driver
      finally:
          driver.quit()          # runs even if the body raises

  # usage:
  with chrome_driver(proxy) as driver:
      ...
  ```
  Learn both styles: the `@contextmanager` generator (above) *and* the class form with
  `__enter__`/`__exit__` (you already have one in `DatabaseManager` — compare them).
- [ ] **Leaked file handles** in `setup_driver` (`browser.py:34,36`): `json.dump(..., open(...))` and `open(...).write(...)` never close. Use `with open(...) as f:`. **P1·S** `with`
- [ ] **Leaked temp dir**: `tempfile.mkdtemp()` (`browser.py:24`) is never removed. Use `tempfile.TemporaryDirectory()` as a context manager, or register cleanup. **P2·S** `tempfile`
- [ ] **Fix `__exit__` signature** in `DatabaseManager` (`db/init.py:15`): `def __exit__(self, *args)` works but hides intent. Use the real signature and learn what the return value means (truthy → *suppress* the exception): **P2·S** `__exit__`
  ```python
  def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
      self.con.close()
      return False   # don't swallow exceptions
  ```
- [ ] **`contextlib.ExitStack`** in `main()` to manage the driver *and* db together cleanly; **`contextlib.suppress(...)`** to replace any `try/except: pass`. **P3·M** `ExitStack` `suppress`

---

## 8. Decorators `decorators` `functools`

- [ ] **Replace the hand-rolled retry** in `scrape_url` (`main.py:14–23`) with a reusable
  decorator — the canonical "write your own decorator" exercise. Note `functools.wraps`
  (preserves the wrapped function's name/docstring) and that it raises instead of
  returning the `(None, None)` sentinel: **P1·M** `functools.wraps`
  ```python
  import functools, logging, time
  from collections.abc import Callable

  def retry(times: int = 3, *, exceptions: tuple[type[Exception], ...] = (Exception,),
            backoff: float = 3.0):
      def decorator(fn: Callable):
          @functools.wraps(fn)
          def wrapper(*args, **kwargs):
              for attempt in range(times):
                  try:
                      return fn(*args, **kwargs)
                  except exceptions as exc:
                      logging.warning("attempt %d/%d failed: %s", attempt + 1, times, exc)
                      time.sleep(backoff * (attempt + 1))
              raise   # exhausted retries → propagate the last error
          return wrapper
      return decorator
  ```
  Then compare with the **`tenacity`** library (don't reinvent in prod — but write it once to learn).
- [ ] **`functools.cached_property`** — e.g. cache a derived value on Settings, or memoize
  `get_already_scraped`. Learn how it differs from `@property` + manual caching. **P2·S** `cached_property`
- [ ] **`functools.lru_cache`** on a pure function (e.g. `make_base_urls`) — understand
  when caching a pure function is safe. **P3·S** `lru_cache`
- [ ] **Built-in method decorators**: refactor `setup_driver`/proxy-extension building into
  a small class and practise `@staticmethod`, `@classmethod` (e.g. `Driver.from_settings(...)`),
  and `@property`. **P3·M**

---

## 9. Dunder / magic methods `dunder`

You've already met several via dataclasses (`__init__`, `__repr__`, `__eq__`) and context
managers (`__enter__`, `__exit__`). Round out the mental model:

- [ ] **`__repr__`** — add a readable one to `DatabaseManager` (`<DatabaseManager db.schema>`) so debugging/logging is pleasant. **P2·S** `__repr__`
- [ ] **`__iter__` / `__len__`** — make `parse_listings` return a small `ListingPage` object
  that is iterable and has a length, instead of a bare list. Teaches the iterator protocol. **P3·M** `__iter__` `__len__`
- [ ] **`__hash__` / `__eq__`** — understand how `frozen=True` dataclasses get these, and
  why that lets you put `RawListing` in a `set` to dedupe scraped listings. **P2·S** `__hash__`
- [ ] **`__call__`** — if you build the retry/driver as a *class* instead of a function,
  implementing `__call__` makes the instance callable. Good contrast with the closure form. **P3·S** `__call__`

---

## 10. Error handling `exceptions`

- [ ] **Define a custom exception hierarchy** instead of raising bare `ValueError`
  (`parser.py:13,29`). Lets callers catch *your* errors precisely: **P1·S**
  ```python
  class ScraperError(Exception): ...
  class PageStructureError(ScraperError): ...   # raised by get_listings/get_page_count
  ```
- [ ] **Don't swallow errors silently.** `scrape_url` catches and returns `(None, None)`
  with no log (`main.py:21`). At minimum log it; better, let the retry decorator (Section 8)
  own this and raise on final failure. **P1·S**
- [ ] **Stretch — a `Result`-style return.** Explore returning a typed
  `Ok | Err` union (or `tuple[Listing, None] | tuple[None, Error]`) instead of `None`
  sentinels, and narrow it with an `if`/`match`. Compare with the exception approach. **P3·M** `match`

---

## 11. Logging `logging`

- [ ] **Replace every `print(...)`** (`main.py:27`, `:75`, `:85`; `process`) with the
  `logging` module. Configure once in `main()`; use `logger = logging.getLogger(__name__)`
  per module. Learn levels (`debug`/`info`/`warning`/`error`) and **lazy `%`-formatting**
  (`logger.info("Processing %s", url)` — not f-strings, so the string is only built if the
  level is active). **P1·M**

---

## 12. Testing — broaden & deepen `pytest`

Only `parser.py` is tested. Pure functions are sitting there untested.

- [ ] **Test `urls.py`** — pure, zero-dependency, trivial to cover (`make_page_urls`,
  `get_freguesia`, `make_base_urls`). **P1·S**
- [ ] **`@pytest.mark.parametrize`** — turn the price/rooms/sqm parsing (once it's in
  Pydantic, Section 4b) into a table of `(raw, expected)` cases. The core pytest pattern to learn. **P1·M** `parametrize`
  ```python
  @pytest.mark.parametrize("raw, expected", [
      ("1.200 €", 1200), ("950 €/mês", 950), ("", None),
  ])
  def test_price_eur(raw, expected):
      assert Listing(id="1", price_raw=raw, title="t", freguesia="ajuda").price_eur == expected
  ```
- [ ] **Test the DB layer with in-memory DuckDB** — `duckdb.connect(":memory:")`, create
  the schema, round-trip a listing. Learn fixtures with teardown (`yield`). **P2·M**
- [ ] **`monkeypatch` / `unittest.mock`** — test `scrape_url`/retry without a real browser
  by mocking `smart_get_page`. Teaches isolating I/O. **P2·M** `mock`
- [ ] **`pytest.raises(..., match="...")`** — tighten existing tests to assert the *message*,
  and assert against your new custom exceptions. **P2·S**
- [ ] **Coverage** — add `pytest-cov`, run `--cov=src`, aim to see (not chase 100%) where the gaps are. **P2·S**
- [ ] **Property-based testing with `hypothesis`** — generate random price strings and assert
  `price_eur` never raises / is always `>= 0 or None`. A modern testing superpower. **P3·M** `hypothesis`
- [ ] **Decouple tests from the data shape**: `test_parser.py:28` asserts exact dict keys —
  this will break the moment you move to a dataclass. Assert on attributes/behaviour instead. **P1·S**

---

## 13. Structural / advanced patterns `protocol` `generators` `match`

Reach for these once the above is comfortable.

- [ ] **`typing.Protocol` for testability** — `parse_*` and `scrape_url` depend on a concrete
  Selenium driver. Define a structural interface so a fake can be substituted in tests
  (duck typing, checked statically): **P3·M** `Protocol`
  ```python
  from typing import Protocol
  class PageFetcher(Protocol):
      def get(self, url: str) -> None: ...
      @property
      def page_source(self) -> str: ...
  ```
- [ ] **Generators / `yield`** — make `parse_listings` *yield* listings (`Iterator[Listing]`)
  instead of building a list, so large pages stream. Learn `collections.abc.Iterator`. **P3·M** `generators`
- [ ] **`match` statement (3.10+)** — use structural pattern matching for job-status handling
  or the `Result` union in Section 10. **P3·S** `match`
- [ ] **`pathlib` over `os`** — `main.py` mixes `os.getenv`; ensure any path work uses
  `pathlib` (ruff `PTH` rules will flag this). **P3·S** `pathlib`
- [ ] **`enumerate` / `itertools`** — small readability wins in the `main()` scrape loop. **P3·S**
- [ ] **`__all__`** — declare public API in each module's `__init__.py` once they exist. **P3·S**

---

## Suggested learning order

A path that builds concepts on each other rather than jumping around:

1. **§1 + §2** — clean up, wire up ruff + mypy (so every later step gets checked). 🔴
2. **§3** — add typing everywhere (mypy now has something to verify). 🔴
3. **§7 + §11 + §10** — context managers, logging, custom exceptions (fix the real resource leaks). 🔴
4. **§4a → §4b** — dataclass first, then Pydantic (feel the progression). 🔴
5. **§5 + §6** — pydantic-settings config + StrEnum status. 🟡
6. **§8 + §9** — decorators and the remaining dunders. 🟡
7. **§12** — broaden tests against the now-typed, validated code. 🟡
8. **§13** — Protocols, generators, `match` as a capstone. 🟢

---

## Concept → where-to-apply cheat sheet

| Concept | Practise it on | File |
| --- | --- | --- |
| Type hints, `X \| None`, `Final`, `Self` | every function | all `src/` modules |
| `TypedDict` | the listing dict (intermediate step) | `parser.py` |
| `@dataclass` (`frozen`, `slots`, `field`) | `RawListing` value object | `parser.py` |
| Pydantic `BaseModel`, `field_validator`, `computed_field` | clean `Listing` w/ price/rooms parse | new `models.py` |
| `pydantic-settings` `BaseSettings`, `SecretStr` | app + proxy config | `main.py` |
| `enum.StrEnum`, `Literal` | job status | `main.py` / `db` |
| `@contextmanager`, `__enter__/__exit__`, `ExitStack`, `TemporaryDirectory` | driver, temp dir, file handles | `browser.py`, `main.py` |
| Custom decorator, `functools.wraps`, `cached_property`, `lru_cache` | retry, caching | `main.py`, `urls.py` |
| Dunders `__repr__`, `__iter__`, `__len__`, `__hash__`, `__call__` | `DatabaseManager`, listing page | `db/`, `parser.py` |
| Custom exception hierarchy | parse failures | `parser.py` |
| `logging` (lazy `%` fmt) | replace all `print` | `main.py` |
| `parametrize`, `monkeypatch`/`mock`, in-memory DuckDB, `hypothesis` | parsing, retry, DB | `tests/` |
| `Protocol`, generators, `match` | fetcher interface, streaming parse | `parser.py`, `main.py` |

---

*Generated as a learning roadmap — each item is meant to be implemented by hand, with a
quick read of the relevant docs, so the pattern sticks. Tick the boxes as you go.*
