import yaml
import tempfile
import subprocess
import os

class KanbanItemEditor:
    def __init__(self, app, item_id, keyvalues):
        self.app = app
        self.item_id = item_id
        self.keyvalues = keyvalues
        self.interactive = self.keyvalues == {}
        self.editor_fields = []
        self.item = None

    def insert_edit_fields(self, title, items, pos=None):
        if pos is None:
            pos = len(self.editor_fields)
        self.editor_fields.insert(pos, (title, items))

    def set_item(self, d):
        self.item = d

    def edit_item(self):

        if self.interactive is True:
            editor_template = self._create_editor_template(self.item)
            self._save_template_file(editor_template)
            self._launch_editor()
            if self.edit_changed:
                with open(self.editor_file, "r") as f:
                    try:
                        d = yaml.safe_load(f)
                        try:
                            del d['id']
                        except KeyError:
                            pass
                        self.item = d
                    except Exception:
                        self._delete_template_file()
                        self.app.error("Error parsing content")
            self._delete_template_file()
        else:
            try:
                del self.keyvalues['id']
            except KeyError:
                pass
            self.item.update(self.keyvalues)

    def save_item(self, kanban_store):
        if self.item_id is None:
            self.app.kanban_store.add_item(self.item)
        else:
            self.app.kanban_store.set_item(self.item_id, self.item)
        self.app.kanban_store.save(self.app.args.kanban_store)

    def _create_editor_template(self, item):
        editor_values = {}
        for section, fields in self.editor_fields:
            editor_values.update(dict(fields))
        editor_values.update(item)

        template_lines = []
        for section, fields in self.editor_fields:
            template_lines.append('# %s\n' % section)
            for f,v in fields:
                template_lines.append(yaml.safe_dump({f : editor_values[f]}, default_flow_style=False))

        for section, fields in self.editor_fields:
            for f,v in fields:
                try:
                    del editor_values[f]
                except KeyError:
                    pass

        if editor_values != {}:
            template_lines.append('# Unused\n')
        for k,v in editor_values.items():
            template_lines.append(yaml.safe_dump({k : v}, default_flow_style=False))

        return "".join(template_lines)

    def _save_template_file(self, editor_template):
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            self.editor_file = f.name
            f.write(editor_template)

    def _launch_editor(self):
        editor_file_status = os.stat(self.editor_file)
        editor_cmd = os.environ['EDITOR']
        proc = subprocess.run([ editor_cmd, self.editor_file ])
        self.edit_changed = proc.returncode == 0 and editor_file_status != os.stat(self.editor_file)

    def _delete_template_file(self):
        os.unlink(self.editor_file)


