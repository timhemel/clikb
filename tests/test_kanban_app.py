import pytest
import pathlib
from clikb.cli import KanbanApp

@pytest.fixture
def test_file():
    def get(fn):
        return pathlib.Path(__file__).parent / 'data' / fn
    return get

class MockContext:
    params = {}

@pytest.fixture
def app_context():
    def make(**kwargs):
        c = MockContext()
        c.params = kwargs
        return c
    return make


def test_active_plugins(test_file, app_context):
    store_path = test_file('test_store1')
    plugin_dir = test_file('test_plugin_dir')
    a = KanbanApp(app_context(kanban_store=store_path, kanban_plugin_path=[plugin_dir]))
    a.initialize()
    # assert that plugins are loaded, main and test_plugin
    assert [p.__module__ for p in a.plugins() ] == [ 'testplugin', 'main' ]

