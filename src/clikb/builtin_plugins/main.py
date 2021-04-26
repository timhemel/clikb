
from base_kanban_plugin import BaseKanbanPlugin

class KanbanPlugin(BaseKanbanPlugin):

    def list_do(self):
        for item in self.kanban_store.items():
            try:
                print("%(id)d\t%(description)s" % item)
            except KeyError:
                pass

    def set_default_fields(self, editor):
        defaults = self.kanban_store.get_board().get('default_fields', {})
        editor.insert_edit_fields( "Main fields", defaults.items(), pos=0 )

    def edit_pre(self, editor):
        self.set_default_fields(editor)

    def edit_edit(self, editor):
        try:
            item = self.kanban_store.get_item(editor.item_id).copy()
        except IndexError:
            self.kanban_app.error("No such item: %d" % editor.item_id)
        try:
            del item['id']
        except KeyError:
            pass

        editor.set_item(item)
        editor.edit_item()

    def edit_save(self, editor):
        editor.save_item(self.kanban_store)

    def add_pre(self, editor):
        self.set_default_fields(editor)
        defaults = self.kanban_store.get_board().get('default_fields', {})
        editor.set_item(defaults)

    def add_edit(self, editor):
        editor.edit_item()

    def add_save(self, editor):
        editor.save_item(self.kanban_store)

    def show_do(self, renderer):
        rows = renderer.group_by_status()
        renderer.render(rows)

