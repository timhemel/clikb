import itertools
import shutil
from collections import defaultdict

class KanbanBoardBaseRenderer:

    def __init__(self, app, board):
        self.app = app
        self.board = board

    def group_by_status(self):
        items = self.app.kanban_store.items()
        show_statuses = self.board.get('show_statuses', [])
        l = [ [ item for item in items if item.get('status') == k ] for k in show_statuses ]
        rows = itertools.zip_longest(*l)
        return rows

    def render(self, rows):
        pass


class KanbanBoardConsoleRenderer(KanbanBoardBaseRenderer):

    def _render_head(self):
        show_statuses = self.board.get('show_statuses', [])
        row_text1 = " ".join([ self._render_head_field1(s) for s in show_statuses ])
        row_text2 = " ".join([ self._render_head_field2(s) for s in show_statuses ])
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
        width, height = shutil.get_terminal_size()
        show_statuses = self.board.get('show_statuses', [])
        self.column_width = width // len(show_statuses)
        fmtname = self.app.cmd_args.field_format
        try:
            self.fieldfmt = self.board.get('show_field_format')[fmtname]
        except KeyError:
            self.app.error("Unknown field format: %s" % fmtname)
        lines = [ self._render_head() ]
        lines += [ self._render_row(r) +"\n" for r in rows ]
        return "".join(lines)


