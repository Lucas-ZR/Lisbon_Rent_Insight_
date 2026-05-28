from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def lisboa_ajuda_page1():
    return (FIXTURES / "lisboa_ajuda_page1.html").read_text(encoding="utf-8")


@pytest.fixture
def lisboa_ajuda_page2():
    return (FIXTURES / "lisboa_ajuda_pagina2.html").read_text(encoding="utf-8")


@pytest.fixture
def empty_page():
    return (FIXTURES / "empty.html").read_text(encoding="utf-8")
