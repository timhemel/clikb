import datetime
from clikb.base_kanban_plugin import BaseKanbanPlugin

class KanbanPlugin(BaseKanbanPlugin):

    def add_status_change(self, editor, item, status):
        now = datetime.datetime.now()
        status_changes = item.get('_status_changes', [])
        status_changes.append({
            'status': status, 'date': now})
        item['_status_changes'] = status_changes
        editor.set_item(item)

    def add_save(self, editor):
        item = editor.get_item()
        status_changes = []
        current_status = item.get('status')
        self.add_status_change(editor, item, current_status)

    def edit_save(self, editor):
        item = editor.get_item()
        status_changes = item.get('_status_changes', [])
        current_status = item.get('status')
        if len(status_changes) > 0 and \
            status_changes[-1]['status'] == current_status:
                pass
        else:
            self.add_status_change(editor, item, current_status)

