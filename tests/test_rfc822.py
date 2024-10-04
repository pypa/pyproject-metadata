# SPDX-License-Identifier: MIT

from __future__ import annotations

import email.message
import inspect
import re
import textwrap

import pytest

import pyproject_metadata
import pyproject_metadata.constants


@pytest.mark.parametrize(
    ("items", "data"),
    [
        pytest.param(
            [],
            "",
            id="empty",
        ),
        pytest.param(
            [
                ("Foo", "Bar"),
            ],
            "Foo: Bar\n",
            id="simple",
        ),
        pytest.param(
            [
                ("Foo", "Bar"),
                ("Foo2", "Bar2"),
            ],
            """\
            Foo: Bar
            Foo2: Bar2
            """,
            id="multiple",
        ),
        pytest.param(
            [
                ("Foo", "Unicøde"),
            ],
            "Foo: Unicøde\n",
            id="unicode",
        ),
        pytest.param(
            [
                ("Foo", "🕵️"),
            ],
            "Foo: 🕵️\n",
            id="emoji",
        ),
        pytest.param(
            [
                ("Item", None),
            ],
            "",
            id="none",
        ),
        pytest.param(
            [
                ("ItemA", "ValueA"),
                ("ItemB", "ValueB"),
                ("ItemC", "ValueC"),
            ],
            """\
            ItemA: ValueA
            ItemB: ValueB
            ItemC: ValueC
            """,
            id="order 1",
        ),
        pytest.param(
            [
                ("ItemB", "ValueB"),
                ("ItemC", "ValueC"),
                ("ItemA", "ValueA"),
            ],
            """\
            ItemB: ValueB
            ItemC: ValueC
            ItemA: ValueA
            """,
            id="order 2",
        ),
        pytest.param(
            [
                ("ItemA", "ValueA1"),
                ("ItemB", "ValueB"),
                ("ItemC", "ValueC"),
                ("ItemA", "ValueA2"),
            ],
            """\
            ItemA: ValueA1
            ItemB: ValueB
            ItemC: ValueC
            ItemA: ValueA2
            """,
            id="multiple keys",
        ),
        pytest.param(
            [
                ("ItemA", "ValueA"),
                ("ItemB", "ValueB1\nValueB2\nValueB3"),
                ("ItemC", "ValueC"),
            ],
            """\
            ItemA: ValueA
            ItemB: ValueB1
                   ValueB2
                   ValueB3
            ItemC: ValueC
            """,
            id="multiline",
        ),
    ],
)
def test_headers(
    items: list[tuple[str, None | str]], data: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    message = pyproject_metadata.RFC822Message()
    smart_message = pyproject_metadata._SmartMessageSetter(message)

    monkeypatch.setattr(
        pyproject_metadata.constants,
        "KNOWN_METADATA_FIELDS",
        {x.lower() for x, _ in items},
    )

    for name, value in items:
        smart_message[name] = value

    data = textwrap.dedent(data) + "\n"
    assert str(message) == data
    assert bytes(message) == data.encode()

    assert email.message_from_string(str(message)).items() == [
        (a, "\n       ".join(b.splitlines())) for a, b in items if b is not None
    ]


def test_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pyproject_metadata.constants,
        "KNOWN_METADATA_FIELDS",
        {"itema", "itemb", "itemc"},
    )
    message = pyproject_metadata.RFC822Message()

    message["ItemA"] = "ValueA"
    message["ItemB"] = "ValueB"
    message["ItemC"] = "ValueC"
    body = inspect.cleandoc("""
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris congue semper
        fermentum. Nunc vitae tempor ante. Aenean aliquet posuere lacus non faucibus.
        In porttitor congue luctus. Vivamus eu dignissim orci. Donec egestas mi ac
        ipsum volutpat, vel elementum sapien consectetur. Praesent dictum finibus
        fringilla. Sed vel feugiat leo. Nulla a pharetra augue, at tristique metus.

        Aliquam fermentum elit at risus sagittis, vel pretium augue congue. Donec leo
        risus, faucibus vel posuere efficitur, feugiat ut leo. Aliquam vestibulum vel
        dolor id elementum. Ut bibendum nunc interdum neque interdum, vel tincidunt
        lacus blandit. Ut volutpat sollicitudin dapibus. Integer vitae lacinia ex, eget
        finibus nulla. Donec sit amet ante in neque pulvinar faucibus sed nec justo.
        Fusce hendrerit massa libero, sit amet pulvinar magna tempor quis. ø
        """)
    headers = inspect.cleandoc("""
        ItemA: ValueA
        ItemB: ValueB
        ItemC: ValueC
        """)
    full = f"{headers}\n\n{body}"

    message.set_payload(textwrap.dedent(body))

    assert str(message) == full

    new_message = email.message_from_string(str(message))
    assert new_message.items() == message.items()
    assert new_message.get_payload() == message.get_payload()

    assert bytes(message) == full.encode("utf-8")


def test_unknown_field() -> None:
    message = pyproject_metadata.RFC822Message()
    with pytest.raises(
        pyproject_metadata.ConfigurationError,
        match=re.escape("Unknown field 'Unknown'"),
    ):
        message["Unknown"] = "Value"


def test_known_field() -> None:
    message = pyproject_metadata.RFC822Message()
    message["Platform"] = "Value"
    assert str(message) == "Platform: Value\n\n"


def test_convert_optional_dependencies() -> None:
    metadata = pyproject_metadata.StandardMetadata.from_pyproject(
        {
            "project": {
                "name": "example",
                "version": "0.1.0",
                "optional-dependencies": {
                    "test": [
                        'foo; os_name == "nt" or sys_platform == "win32"',
                        'bar; os_name == "posix" and sys_platform == "linux"',
                    ],
                },
            },
        }
    )
    message = metadata.as_rfc822()
    requires = message.get_all("Requires-Dist")
    assert requires == [
        'foo; (os_name == "nt" or sys_platform == "win32") and extra == "test"',
        'bar; os_name == "posix" and sys_platform == "linux" and extra == "test"',
    ]


def test_convert_author_email() -> None:
    metadata = pyproject_metadata.StandardMetadata.from_pyproject(
        {
            "project": {
                "name": "example",
                "version": "0.1.0",
                "authors": [
                    {
                        "name": "John Doe, Inc.",
                        "email": "johndoe@example.com",
                    },
                    {
                        "name": "Kate Doe, LLC.",
                        "email": "katedoe@example.com",
                    },
                ],
            },
        }
    )
    message = metadata.as_rfc822()
    assert message.get_all("Author-Email") == [
        '"John Doe, Inc." <johndoe@example.com>, "Kate Doe, LLC." <katedoe@example.com>'
    ]


def test_long_version() -> None:
    metadata = pyproject_metadata.StandardMetadata.from_pyproject(
        {
            "project": {
                "name": "example",
                "version": "0.0.0+super.duper.long.version.string.that.is.longer.than.sixty.seven.characters",
            }
        }
    )
    message = metadata.as_rfc822()
    assert (
        message.get("Version")
        == "0.0.0+super.duper.long.version.string.that.is.longer.than.sixty.seven.characters"
    )
    assert (
        bytes(message)
        == inspect.cleandoc("""
        Metadata-Version: 2.1
        Name: example
        Version: 0.0.0+super.duper.long.version.string.that.is.longer.than.sixty.seven.characters
    """).encode("utf-8")
        + b"\n\n"
    )
    assert (
        str(message)
        == inspect.cleandoc("""
        Metadata-Version: 2.1
        Name: example
        Version: 0.0.0+super.duper.long.version.string.that.is.longer.than.sixty.seven.characters
    """)
        + "\n\n"
    )
