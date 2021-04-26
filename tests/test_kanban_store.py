import unittest
import pathlib

from kanban_directory_store import KanbanDirectoryStore

class TestKanbanStore(unittest.TestCase):

    def setUp(self):
        pass

    def _get_test_file(self, fn):
        return pathlib.Path(__file__).parent / "data" / fn

    def _remove_test_dir(self, path, rmdir=True):
        try:
            for fn in path.iterdir():
                fn.unlink()
            if rmdir:
                path.rmdir()
        except FileNotFoundError:
            pass

    # empty store
    def test_empty_store(self):
        k = KanbanDirectoryStore()
        self.assertEqual(k.items(), [])

    # load from file
    def test_load_store(self):
        k = KanbanDirectoryStore()
        k.load(self._get_test_file("test_store1"))
        self.assertEqual(len(k.items()), 3)
        self.assertEqual([x['id'] for x in k.items()], [0,2,3])

    # load from empty store
    def test_load_empty_store(self):
        k = KanbanDirectoryStore()
        k.load(self._get_test_file("test_store_empty"))
        self.assertEqual(len(k.items()), 0)
        self.assertEqual([x['id'] for x in k.items()], [])


    # add item
    def test_add_item(self):
        k = KanbanDirectoryStore()
        k.add_item({'descr':"a small test item"})
        self.assertEqual(len(k.items()), 1)
        self.assertEqual(k.items()[0].get('descr'), "a small test item")
        self.assertEqual(k.items()[0].get('id'), 0)

    # add item, save, then load
    def test_add_item_save_then_load(self):
        self._remove_test_dir(self._get_test_file("test_store2"))
        k = KanbanDirectoryStore()
        k.add_item({'descr':"a small test item"})
        k.save(self._get_test_file("test_store2"))
        k = KanbanDirectoryStore()
        k.load(self._get_test_file("test_store2"))
        self.assertEqual(len(k.items()), 1)
        self.assertEqual(k.items()[0].get('descr'), "a small test item")
        self.assertEqual(k.items()[0].get('id'), 0)

    # save kbstore without path should fail
    def test_save_without_path(self):
        k = KanbanDirectoryStore()
        k.add_item({'descr':"a small test item"})
        with self.assertRaises(Exception) as e:
            k.save()

    # test plugin hooks when adding

    # edit item
    def test_edit_item(self):
        k = KanbanDirectoryStore()
        k.add_item({'descr':"a small test item"})
        item = k.get_item(0)
        k.set_item(0, {'descr':"an edited item"})
        self.assertEqual(k.items()[0].get('descr'), "an edited item")

    # edit item, save, then load
    def test_edit_item_save_load(self):
        self._remove_test_dir(self._get_test_file("test_store2"))
        k = KanbanDirectoryStore()
        k.add_item({'descr':"a small test item"})
        k.add_item({'descr':"a second test item"})
        k.set_item(1, {'descr':"an edited item"})
        k.save(self._get_test_file("test_store2"))
        k = KanbanDirectoryStore()
        k.load(self._get_test_file("test_store2"))
        self.assertEqual(k.items()[1].get('descr'), "an edited item")
        self.assertEqual(k.items()[1].get('id'), 1)

    # test locking

    # test load kanban board
    def test_load_kanban_board(self):
        k = KanbanDirectoryStore()
        k.load(self._get_test_file("test_store1"))
        b = k.get_board()
        self.assertEqual(b['show_statuses'], ['READY', 'DOING', 'DONE'])
        self.assertEqual(b['plugins'], ['testplugin'])

if __name__=="__main__":
    unittest.main()

