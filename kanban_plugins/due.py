import datetime
from BaseKanbanPlugin import BaseKanbanPlugin

class KanbanPlugin(BaseKanbanPlugin):

    def due_delta(self, item):
        today = datetime.date.today()
        due = item.get('due')
        if due:
            if type(due) != datetime.date:
                date_format = self.kanban_store.get_board().get('date_format', '%Y-%m-%d')
                try:
                    due = datetime.datetime.strptime(due, date_format)
                except ValueError:
                    due = today
            delta = due - today
            return delta
        return None

    def due_days(self, item):
        delta = self.due_delta(item)
        if delta is not None:
            return delta.days
        return None

    def due_text(self, item):
        if item.get('due_days') is not None:
            text_fmt = self.kanban_store.get_plugin_conf('due').get('due_text', {}).get('text', '')
            return text_fmt % item
        return ''

    def due_icon(self, item):
        due_days = item.get('due_days')
        if due_days is not None:
            if 0 < due_days <= 7:
                return "🕚"
            if due_days == 0:
                return "🔔"
            if due_days < 0:
                return "🔥"
        return ''
        # 💣 💥  📅 🔔 🔥 🕑 🕚 🕰 🗓 ⌚ ⌛ ⏰ ⏱ ⏲ ⏳

    def show_pre(self, renderer):
        renderer.add_computed_field("due_days", self.due_days)
        renderer.add_computed_field("due_text", self.due_text)
        renderer.add_computed_field("due_icon", self.due_icon)

    def set_default_fields(self, editor):
        defaults = self.kanban_store.get_board().get('default_fields', {})
        editor.insert_edit_fields("Due date", [
            ('due', defaults.get('due', '')),
            ])

    def edit_pre(self, editor):
        self.set_default_fields(editor)

    def add_pre(self, editor):
        self.set_default_fields(editor)

