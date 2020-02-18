import itertools
import shutil
from collections import defaultdict

class KanbanBoardBaseRenderer:

    def __init__(self, app):
        self.app = app
        self.board = app.kanban_store.get_board()
        self.show_statuses = self.board.get('show_statuses', [])

    def group_by_status(self):
        items = self.app.kanban_store.items()
        l = [ [ item for item in items if item.get('status') == k ] for k in self.show_statuses ]
        rows = itertools.zip_longest(*l)
        return rows

    def render(self, rows):
        pass


class KanbanBoardConsoleRenderer(KanbanBoardBaseRenderer):

    def __init__(self, app, field_format):
        KanbanBoardBaseRenderer.__init__(self, app)
        self.field_format_name = field_format
        try:
            self.fieldfmt = self.app.get_show_field_format(self.field_format_name)
        except KeyError:
            self.app.error("Unknown field format: %s" % self.field_format_name)
        width, height = shutil.get_terminal_size() # TODO: ask click
        self.column_width = width // len(self.show_statuses)

    def _render_head(self):
        row_text1 = " ".join([ self._render_head_field1(s) for s in self.show_statuses ])
        row_text2 = " ".join([ self._render_head_field2(s) for s in self.show_statuses ])
        return row_text1 + "\n" + row_text2 + "\n\n"

    def _render_head_field1(self, s):
        t = "│ " + s + " " * self.column_width
        return t[:self.column_width - 1]

    def _render_head_field2(self, s):
        t = "┕━" + "━" * (len(s)+1) + " " * self.column_width
        return t[:self.column_width - 1]

    def _render_row(self, row):
        return " ".join([self._render_field(f) for f in row])

    def _render_field_content(self, field):
        d = defaultdict( lambda : '?' )
        d.update(field)
        return self.fieldfmt % d

    def _render_field(self, field):
        if field is not None:
            fieldtext = "├╴" + self._render_field_content(field)
        else:
            fieldtext = ""
        fieldtext += " " * (self.column_width-1)
        return fieldtext[:self.column_width-1]

    def render(self, rows):
        lines = [ self._render_head() ]
        lines += [ self._render_row(r) +"\n" for r in rows ]
        return "".join(lines)


