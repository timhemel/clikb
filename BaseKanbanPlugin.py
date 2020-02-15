
class BaseKanbanPlugin:

    def __init__(self, kanban_app):
        self.kanban_app = kanban_app
        self.kanban_store = kanban_app.kanban_store

    def get_command_parsers(self):
        return {}

    def get_command_handlers(self):
        return {}

    def list_pre(self):
        pass

    def list_do(self):
        pass

    def list_post(self):
        pass

    def show_pre(self, shower):
        pass

    def show_do(self, shower):
        pass

    def show_post(self, shower):
        pass

    def edit_pre(self, editor):
        pass

    def edit_edit(self, editor):
        pass

    def edit_save(self, editor):
        pass

    def edit_post(self, editor):
        pass

    def add_pre(self, editor):
        pass

    def add_edit(self, editor):
        pass

    def add_save(self, editor):
        pass

    def add_post(self, editor):
        pass

