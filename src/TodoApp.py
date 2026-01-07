from flet import Text, TextField, FloatingActionButton, Checkbox, Button
# Layout
from flet import Column, Row

import flet as ft
# Colors
from flet import Colors

class View(Column):
    def __init__(self, data, delete_task):
        super().__init__()
        
        self.delete_task = delete_task
        
        self.data = Checkbox(label=data, expand=True)
        display_view = Row(controls=[
            self.data,
            Button(text="Edit", on_click=self.edit),
            Button(text="Delete", on_click=lambda e: self.delete_task(self))
        ])
        
        self.t = TextField(value=data, expand=True)
        self.edit_view = Row(visible=False, controls=[
            self.t,
            Button(text="Save", on_click=self.save)
        ])
        
        self.controls = [
            display_view,
            self.edit_view
        ]
    
    def edit(self, e):
        self.edit_view.visible = True
        self.update()
        
    def save(self, e):
        self.data.label = self.t.value
        self.edit_view.visible = False
        self.update()

class TodoApp(Column):
    def __init__(self):
        super().__init__(width=600)
        self.new_task = TextField(hint_text="Helloworld", expand=True)
        self.add_button = FloatingActionButton(
            icon=ft.Icons.ADD, on_click=self.fab_pressed, bgcolor=Colors.LIME_300
        )
        
        self.task_view = Column()
        
        self.controls = [
            Row(controls=[
                self.new_task,
                self.add_button
            ]),
            self.task_view
        ]
    
    def fab_pressed(self, e):
        data = self.new_task.value
        if data == "":
            return 0
        self.task_view.controls.append(
            View(data=data, delete_task=self.delete_task)
        )
        self.new_task.value = ""
        self.update()
        
    def delete_task(self, task):
        self.task_view.controls.remove(task)
        self.update()