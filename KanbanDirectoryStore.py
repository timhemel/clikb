import pathlib
import yaml

class KanbanDirectoryStore:

    def __init__(self):
        self._items = []
        self.kbstore_path = None
        self.max_idx = -1
        self.board = {}

    def load(self, path):
        self._items = [ x[1] for x in sorted([ (fn, self._load_item(fn)) for fn in filter(lambda p: p.suffix == '.kbi', path.iterdir()) ]) ]
        if self._items != []:
            self.max_idx = max( [ x['id'] for x in self._items ] )
        self.board = self._load_board(path / "board.kbb")

    def save(self, path=None):
        if not path:
            if self.kbstore_path is not None:
                path = self.kbstore_path
            else:
                raise Exception("No kbstore path")

        # if self.kbstore_path is None: self.kbstore_path = path

        self._create_kbstore_directory(path)

        for idx,item in enumerate(self._items):
            self._save_item(path, idx, item)

        self._save_board(path)

    def _create_kbstore_directory(self, path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def _save_item(self, path, idx, item):
        fn = pathlib.Path(path) / ("%05d.kbi" % idx)
        with open(fn, "w") as f:
            d = item.copy()
            try:
                del d['id']
            except KeyError:
                pass
            yaml.safe_dump(d, stream=f, default_flow_style=False)

    def _load_item(self, full_path):
        idx = int(full_path.stem)

        with open(full_path, "r") as f:
            d = yaml.safe_load(f)
            d['id'] = idx
            return d

    def _save_board(self, path):
        fn = pathlib.Path(path) / "board.kbb"
        with open(fn, "w") as f:
            yaml.safe_dump(self.board, stream=f, default_flow_style=False)


    def _load_board(self, full_path):
        with open(full_path, "r") as f:
            d = yaml.safe_load(f)
            return d


    def add_item(self, kwargs):
        self._items.append( kwargs )
        self.max_idx += 1
        self._items[-1]['id'] = self.max_idx

    def items(self):
        return self._items

    def get_item(self, idx):
        return [ i for i in self._items if i['id'] == idx ][0]

    def set_item(self, idx, keyvalues):
        item_index = [ k for k,i in enumerate(self._items) if i['id'] == idx ][0]
        self._items[item_index] = keyvalues
        self._items[item_index]['id'] = idx

    def edit_item(self, idx, d):
        try:
            item = self.get_item(idx)
            item.update(d)
        except IndexError:
            pass

    def get_board(self):
        return self.board

