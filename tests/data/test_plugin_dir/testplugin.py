from clikb.base_kanban_plugin import BaseKanbanPlugin

class KanbanPlugin(BaseKanbanPlugin):
    pass

    def pre_list(self):
        print("prelist")

    def show_pre(self, renderer):
        # print(dir(self.kanban_store))
        # print(self.kanban_store.items())
        pass
