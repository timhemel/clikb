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
import pathlib

import click

class DefaultCmdGroup(click.Group):

    def resolve_command(self, ctx, args):
        cmd_name, cmd, args = click.Group.resolve_command(self, ctx, args)
        if cmd_name.isnumeric():
            args = [cmd_name] + args
            cmd_name = cmd.name
        return cmd_name, cmd, args

    def get_command(self, ctx, cmd_name):
        cmd = click.Group.get_command(self, ctx, cmd_name)
        if cmd is not None:
            return cmd
        else:
            c = click.Group.get_command(self, ctx, 'edit')
            return c

KANBAN_STORE_ENVVAR='KANBAN_STORE'

def kanbanstore_defined(command_ctx):
    return command_ctx.parent.params['kanban_store'] is not None

def check_kanbanstore_defined(command_ctx):
    if not kanbanstore_defined(command_ctx):
        command_ctx.fail("Kanban store undefined, please set %s or use --kanban-store" % KANBAN_STORE_ENVVAR)

def parse_keyvalues(keyvalues, default_key):
    key_values = [ a.split('=',maxsplit=1) for a in keyvalues ]

    d = {}
    for i, kv in enumerate(key_values):
        if len(kv) == 1:
            if i == 0:
                key = default_key
                value = kv[0]
            else:
                raise ValueError("non-first edit argument needs to have key=value format")
        else:
            key, value = kv
        d[key] = value
    return d


@click.group(cls=DefaultCmdGroup, invoke_without_command=False)
# -d is needed for all arguments, except init
@click.option('-d', '--kanban-store', envvar=KANBAN_STORE_ENVVAR, type=click.Path())
@click.pass_context
def app(ctx, kanban_store):
    ctx.obj = KanbanApp(ctx)

@app.command()
@click.option('--template', type=click.Path())
@click.argument('kanban-board-dir', type=click.Path())
@click.pass_context
def init(ctx, template, kanban_board_dir):
    board_dir = pathlib.Path(kanban_board_dir)
    board_file = board_dir / "board.kbb"
    if board_file.exists():
        ctx.fail("Directory already initialized.")
    try:
        board_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    with open(board_file, "w") as f:
        f.write("""
# extra plugins to load
plugins:
- testplugin
# statuses to show on the board
show_statuses:
- READY
- DOING
- DONE
# default values for fields
default_fields:
  description: hello
  status: READY
# views to display the fields
show_field_format:
  default: '%(id)3d %(description)s'
  test: '%(id)3d %(tag)-3s %(description)s'
""")

@app.command()
@click.option('--field-format', default='default')
@click.pass_context
def show(ctx, field_format):
    check_kanbanstore_defined(ctx)
    ctx.obj.initialize()
    plugins = ctx.obj.plugins()
    # TODO: choose renderer
    renderer = KanbanBoardConsoleRenderer(ctx.obj, field_format)
    for p in plugins:
        p.show_pre(renderer)
    for p in plugins:
        p.show_do(renderer)
    for p in plugins:
        p.show_post(renderer)


@app.command()
@click.pass_context
def list(ctx):
    check_kanbanstore_defined(ctx)
    ctx.obj.initialize()
    plugins = ctx.obj.plugins()
    for p in plugins:
        p.list_pre()
    for p in plugins:
        p.list_do()
    for p in plugins:
        p.list_post()

@app.command()
@click.argument('keyvalues', nargs=-1, required=False)
@click.pass_context
def add(ctx, keyvalues):
    check_kanbanstore_defined(ctx)
    ctx.obj.initialize()
    try:
        d = parse_keyvalues(keyvalues, default_key='description')
    except ValueError as e:
        ctx.fail(e.args[0])
    editor = KanbanItemEditor(ctx.obj, None, d)
    plugins = ctx.obj.plugins()
    for p in plugins:
        p.add_pre(editor)
    for p in plugins:
        p.add_edit(editor)
    for p in plugins:
        p.add_save(editor)
    for p in plugins:
        p.add_post(editor)


@app.command()
@click.argument('item-id', type=int)
@click.argument('keyvalues', nargs=-1, required=False)
@click.pass_context
def edit(ctx, item_id, keyvalues):
    check_kanbanstore_defined(ctx)
    ctx.obj.initialize()
    try:
        d = parse_keyvalues(keyvalues, default_key='status')
    except ValueError as e:
        ctx.fail(e.args[0])
    editor = KanbanItemEditor(ctx.obj, item_id, d)
    plugins = ctx.obj.plugins()
    for p in plugins:
        p.edit_pre(editor)
    for p in plugins:
        p.edit_edit(editor)
    for p in plugins:
        p.edit_save(editor)
    for p in plugins:
        p.edit_post(editor)

class KanbanApp:

    def __init__(self, parent_ctx):
        self.parent_ctx = parent_ctx

    def initialize(self):
        self._load_kanban_store()
        self._load_plugins()

    def plugins(self):
        return self._plugins

    def error(self, msg):
        self.parent_ctx.fail(msg)

    def _load_kanban_store(self):
        kanbanstore_dir = pathlib.Path(self.parent_ctx.params['kanban_store'])
        self.kanban_store = KanbanDirectoryStore()
        self.kanban_store.load(kanbanstore_dir)

    def _load_plugin(self, app, plugin_name):
        m = importlib.import_module("kanban_plugins.%s" % plugin_name)
        return m.KanbanPlugin(app)

    def _load_plugins(self):
        self._plugins = []
        for p in self.kanban_store.get_board()['plugins'] + ['main']:
            plugin = self._load_plugin(self, p)
            self._plugins.append(plugin)

    def get_show_field_format(self, fmtname):
        return self.kanban_store.get_board().get('show_field_format')[fmtname]


if __name__=="__main__":
    app()
