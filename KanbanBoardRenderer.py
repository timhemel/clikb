import itertools
import shutil
from collections import defaultdict, OrderedDict
import csv
import io
import wcwidth

class KanbanBoardBaseRenderer:

    def __init__(self, app):
        self.app = app
        self.board = app.kanban_store.get_board()
        self.show_statuses = self.board.get('show_statuses', [])
        self.computed_fields = OrderedDict()

    def add_computed_field(self, key, value):
        self.computed_fields[key] = value

    def group_by_status(self):
        items = self.app.kanban_store.items()
        l = [ [ item for item in items if item.get('status') == k ] for k in self.show_statuses ]
        rows = itertools.zip_longest(*l)
        return rows

    def render(self, rows):
        pass


class BoardView:
    def __init__(self, num_columns):
        self.num_columns = num_columns
        self.clear()
    def clear(self):
        self.columns = [ [] for c in range(self.num_columns) ]
    def add_field(self, column, lines):
        self.columns[column] += lines
    def get_rows(self):
        rows = itertools.zip_longest(*self.columns)
        return rows
 
class KanbanBoardConsoleRenderer(KanbanBoardBaseRenderer):

    def __init__(self, app, field_fmt, out_file):
        KanbanBoardBaseRenderer.__init__(self, app)
        self.outfile = out_file
        self.fieldfmt = field_fmt
        width, height = shutil.get_terminal_size() # TODO: ask click
        self.column_width = width // len(self.show_statuses)
        self.board_view = BoardView(len(self.show_statuses))

    def _render_head(self):
        for i,s in enumerate(self.show_statuses):
            self.board_view.add_field(i, [
                self._render_head_field1(s),
                self._render_head_field2(s) ])

    def _render_head_field1(self, s):
        t = "│ " + s + " " * self.column_width
        return t[:self.column_width ]

    def _render_head_field2(self, s):
        t = "┕━" + "━" * (len(s)+1) + " " * self.column_width
        return t[:self.column_width ]

    def _pad_and_truncate(self, text):
        return (text + " " * (self.column_width))[:self.column_width] 
    def _render_field(self, field):
        d = defaultdict( lambda : '?' )
        d.update(field)
        for k,v in self.computed_fields.items():
            d[k] = v(d)

        return [ self._pad_and_truncate(f['text'] % d)
                for f in self.fieldfmt ]

    def _render_item(self, item):
        lines = self._render_field(item)
        try:
            col = self.column_lookup[item.get('status')]
            self.board_view.add_field(col, lines)
        except KeyError:
            pass

    def render(self, rows):
        self.board_view.clear()
        self.column_lookup = dict([ (v,i) for i,v in enumerate(self.show_statuses) ])
        items = self.app.kanban_store.items()
        self._render_head()
        for i in items:
            self._render_item(i)
        rows = self.board_view.get_rows()
        
        for row in rows:
            for f in row:
                if f is not None:
                    self.outfile.write(f)
                else:
                    self.outfile.write(' ' * self.column_width)
            self.outfile.write('\n')


class KanbanBoardCSVRenderer(KanbanBoardBaseRenderer):

    def __init__(self, app, field_fmt, out_file):
        KanbanBoardBaseRenderer.__init__(self, app)
        self.outfile = out_file
        self.fieldfmt = field_fmt

    def _render_field_content(self, field):
        d = defaultdict( lambda : '?' )
        d.update(field)
        return self.fieldfmt % d

    def _render_field(self, field):
        if field is not None:
            fieldtext = self._render_field_content(field)
        else:
            fieldtext = ""
        return fieldtext


    def render(self, rows):
        w = csv.writer(self.outfile)
        w.writerow(self.show_statuses)
        for r in rows:
            w.writerow( [ self._render_field(x) for x in r ])

