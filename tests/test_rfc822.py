# SPDX-License-Identifier: MIT

import textwrap

import pytest

import pep621


@pytest.mark.parametrize(
    ('items', 'data'),
    [
        # empty
        ([], ''),
        # simple
        (
            [
                ('Foo', 'Bar'),
            ],
            'Foo: Bar\n',
        ),
        (
            [
                ('Foo', 'Bar'),
                ('Foo2', 'Bar2'),
            ],
            '''\
            Foo: Bar
            Foo2: Bar2
            ''',
        ),
        # None
        (
            [
                ('Item', None),
            ],
            '',
        ),
        # order
        (
            [
                ('ItemA', 'ValueA'),
                ('ItemB', 'ValueB'),
                ('ItemC', 'ValueC'),
            ],
            '''\
            ItemA: ValueA
            ItemB: ValueB
            ItemC: ValueC
            ''',
        ),
        (
            [
                ('ItemB', 'ValueB'),
                ('ItemC', 'ValueC'),
                ('ItemA', 'ValueA'),
            ],
            '''\
            ItemB: ValueB
            ItemC: ValueC
            ItemA: ValueA
            ''',
        ),
        # multiple keys
        (
            [
                ('ItemA', 'ValueA1'),
                ('ItemB', 'ValueB'),
                ('ItemC', 'ValueC'),
                ('ItemA', 'ValueA2'),
            ],
            '''\
            ItemA: ValueA1
            ItemA: ValueA2
            ItemB: ValueB
            ItemC: ValueC
            ''',
        ),
    ],
)
def test_headers(items, data):
    message = pep621.RFC822Message()

    for name, value in items:
        message[name] = value

    data = textwrap.dedent(data)
    assert str(message) == data
    assert bytes(message) == data.encode()


def test_body():
    message = pep621.RFC822Message()

    message['ItemA'] = 'ValueA'
    message['ItemB'] = 'ValueB'
    message['ItemC'] = 'ValueC'

    message.body = textwrap.dedent('''
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
        Fusce hendrerit massa libero, sit amet pulvinar magna tempor quis.
    ''')

    assert str(message) == textwrap.dedent('''\
        ItemA: ValueA
        ItemB: ValueB
        ItemC: ValueC


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
        Fusce hendrerit massa libero, sit amet pulvinar magna tempor quis.
    ''')
