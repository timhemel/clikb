#!/usr/bin/env python3

from KanbanDirectoryStore import KanbanDirectoryStore
from KanbanItemEditor import KanbanItemEditor
from KanbanBoardRenderer import KanbanBoardConsoleRenderer
from argparse import ArgumentParser
from pathlib import Path
import os
import configparser
import functools
import itertools
import csv
import sys
import importlib

class KanbanConfig:

    def __init__(self, cfgpath):
        self.config = configparser.ConfigParser()
        self.config.read(cfgpath)
        self.statuses = self.config.get('default', 'statuses').split(',')
    
    def get_store(self):
        store_path = Path(os.getenv('HOME','')) / '.kanban.csv'
        return KanbanDirectoryStore()

    def get_statuses(self):
        return self.statuses

    def get_show_statuses(self):
        return self.statuses

    def get_status_order(self, status):
        return self.statuses.index(status)


class KanbanApp:

    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('-d','--kanban-store', required=False, default=os.path.join(os.environ['HOME'], '.kanban_store'))

        parser.add_argument('command')
        self.args, rest = parser.parse_known_args()

        self._load_board()
        self._initialize_plugins_from_board()
        self._initialize_argument_parsers()
        self._initialize_command_handlers()

        if self.args.command.isnumeric():
            rest.insert(0, self.args.command)
            self.command = 'edit_implicit'
        else:
            self.command = self.args.command

        self.cmd_args = self.command_parsers[self.command].parse_args(rest)

    def error(self, msg):
        print("ERROR:", msg, file=sys.stderr)
        sys.exit(1)

    def register_plugin(self, plugin_name):
        plugin = self._load_plugin(plugin_name)
        self.plugins.append(plugin)

    def _load_plugin(self, plugin_name):
        # import plugins.plugin_name
        m = importlib.import_module("kanban_plugins.%s" % plugin_name)
        return m.KanbanPlugin(self)

    def _initialize_plugins_from_board(self):
        self.plugins = []
        for p in self.kanban_store.get_board()['plugins']:
            self.register_plugin(p)
        self.register_plugin('main')

    def _load_board(self):
        self.kanban_store = KanbanDirectoryStore()
        kbstore_path = Path(self.args.kanban_store)
        self.kanban_store.load(kbstore_path)

    def _initialize_argument_parsers(self):
        self.command_parsers = {
                'edit_implicit': self._make_parsers_edit_implicit(),
                'list': self._make_parsers_list(),
                'add': self._make_parsers_add(),
                'show': self._make_parsers_show(),
        }

    def _initialize_command_handlers(self):
        self.command_handlers = {
                'edit_implicit': self.edit,
                'list': self.list,
                'add': self.add,
                'show': self.show,
                # 'renum'
        }

    def _make_parsers_edit_implicit(self):
        parser = ArgumentParser()
        parser.add_argument("item_id", type=int)
        parser.add_argument("keyvalue", nargs="*")
        return parser

    def _make_parsers_list(self):
        parser = ArgumentParser()
        return parser

    def _make_parsers_show(self):
        parser = ArgumentParser()
        parser.add_argument('--field-format', default='default')
        # option for output format (e.g. text, csv)
        return parser

    def _make_parsers_add(self):
        parser = ArgumentParser()
        parser.add_argument("keyvalue", nargs="*")
        return parser

    def _parse_keyvalues(self, default_key):
        key_values = [ a.split('=',maxsplit=1) for a in self.cmd_args.keyvalue ]

        d = {}
        for i, kv in enumerate(key_values):
            if len(kv) == 1:
                if i == 0:
                    key = default_key
                    value = kv[0]
                else:
                    # error
                    raise Exception("non-first edit argument needs to have key=value format")
            else:
                key, value = kv
            d[key] = value
        return d

    def edit(self):
        d = self._parse_keyvalues('status')
        e = KanbanItemEditor(self, self.cmd_args.item_id, d)

        for p in self.plugins:
            p.edit_pre(e)
        for p in self.plugins:
            p.edit_edit(e)
        for p in self.plugins:
            p.edit_save(e)
        for p in self.plugins:
            p.edit_post(e)


    def run(self):
        try:
            cb = self.command_handlers[self.command]
            cb()
        except KeyError:
            pass

    def add(self):
        d = self._parse_keyvalues('description')
        editor = KanbanItemEditor(self, None, d)

        for p in self.plugins:
            p.add_pre(editor)
        for p in self.plugins:
            p.add_edit(editor)
        for p in self.plugins:
            p.add_save(editor)
        for p in self.plugins:
            p.add_post(editor)

    def show(self):
        # TODO: choose renderer
        renderer = KanbanBoardConsoleRenderer(self, self.kanban_store.get_board())
        for p in self.plugins:
            p.show_pre(renderer)
        for p in self.plugins:
            p.show_do(renderer)
        for p in self.plugins:
            p.show_post(renderer)

    def list(self):
        for p in self.plugins:
            p.list_pre()
        for p in self.plugins:
            p.list_do()
        for p in self.plugins:
            p.list_post()

    commands = {
            'list': list,
            'show': show,
    }


if __name__=="__main__":
    KanbanApp().run()
