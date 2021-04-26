import pathlib
import pytest

from clikb.kanban_directory_store import KanbanDirectoryStore

@pytest.fixture
def test_file():
    def get(fn):
        return pathlib.Path(__file__).parent / 'data' / fn
    return get

# empty store
def test_empty_store():
    k = KanbanDirectoryStore()
    assert k.items() == []

# load from file
def test_load_store(test_file):
    k = KanbanDirectoryStore()
    k.load(test_file("test_store1"))
    assert len(k.items()) == 3
    assert [x['id'] for x in k.items()] == [0,2,3]

# load from empty store
def test_load_empty_store(test_file):
    k = KanbanDirectoryStore()
    k.load(test_file("test_store_empty"))
    assert k.items() == []

# add item
def test_add_item():
    k = KanbanDirectoryStore()
    k.add_item({'descr':"a small test item"})
    assert len(k.items()) == 1
    assert k.items()[0].get('descr') == "a small test item"
    assert k.items()[0].get('id') == 0

# add item, save, then load
def test_add_item_save_then_load(tmpdir):
    k = KanbanDirectoryStore()
    k.add_item({'descr':"a small test item"})
    k.save(pathlib.Path(tmpdir) / 'test_store2')
    k = KanbanDirectoryStore()
    k.load(pathlib.Path(tmpdir) / 'test_store2')
    assert len(k.items()) == 1
    assert k.items()[0].get('descr') == "a small test item"
    assert k.items()[0].get('id') == 0

# save kbstore without path should fail
def test_save_without_path():
    k = KanbanDirectoryStore()
    k.add_item({'descr':"a small test item"})
    with pytest.raises(Exception) as e:
        k.save()

# test plugin hooks when adding

# edit item
def test_edit_item():
    k = KanbanDirectoryStore()
    k.add_item({'descr':"a small test item"})
    item = k.get_item(0)
    k.set_item(0, {'descr':"an edited item"})
    assert k.items()[0].get('descr') == "an edited item"

# edit item, save, then load
def test_edit_item_save_load(tmpdir):
    # self._remove_test_dir(self._get_test_file("test_store2"))
    k = KanbanDirectoryStore()
    k.add_item({'descr':"a small test item"})
    k.add_item({'descr':"a second test item"})
    k.set_item(1, {'descr':"an edited item"})
    k.save(pathlib.Path(tmpdir) / 'test_store2')
    k = KanbanDirectoryStore()
    k.load(pathlib.Path(tmpdir) / 'test_store2')
    assert k.items()[1].get('descr') == "an edited item"
    assert k.items()[1].get('id') == 1

# test locking

# test load kanban board
def test_load_kanban_board(test_file):
    k = KanbanDirectoryStore()
    k.load(test_file("test_store1"))
    b = k.get_board()
    assert b['show_statuses'] == ['READY', 'DOING', 'DONE']
    assert b['plugins'] == ['testplugin']


