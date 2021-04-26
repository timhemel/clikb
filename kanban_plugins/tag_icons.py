
from base_kanban_plugin import BaseKanbanPlugin


class KanbanPlugin(BaseKanbanPlugin):

    def tags_icons(self, item):
        tag_icons = self.kanban_store.get_plugin_conf('tag_icons')
        tags = item.get('tags',[])
        tags = [ tag_icons.get(t, t) for t in tags ]
        return " ".join(tags)

    def show_pre(self, renderer):
        renderer.add_computed_field("tags", self.tags_icons)

    def set_default_fields(self, editor):
        defaults = self.kanban_store.get_board().get('default_fields', {})
        editor.insert_edit_fields("Tags", [
            ('tags', defaults.get('tags', [])),
            ])

    def edit_pre(self, editor):
        self.set_default_fields(editor)

    def add_pre(self, editor):
        self.set_default_fields(editor)


