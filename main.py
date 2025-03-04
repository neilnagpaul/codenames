from collections import defaultdict
from functools import partial
from itertools import cycle
from random import sample
from typing import Callable, Tuple
from fastapi import FastAPI
from nicegui import app as niceapp, ui


with open("words") as f:
    words = f.read().splitlines()

colors = ["red"] * 9 + ["blue"] * 8 + ["gray"] * 7 + ["purple"]


class Word:
    def __init__(self, text, color):
        self.text = text
        self.color = color
        self.revealed = False

    @ui.refreshable_method
    def view(self, spymaster: ui.switch, on_click: Callable):
        btn = ui.button(
            self.text,
            color=(self.color + "-200" * (not self.revealed)
                   if spymaster.value or self.revealed else "white"),
            on_click=on_click
        )
        btn.props("padding=0")
        btn.tailwind.font_size("xs")


class Game:
    def __init__(self):
        self.turns = cycle(["blue", "red"])
        self.turn = next(self.turns)
        self.done = False
        self.board = [
            Word(word, color)
            for word, color in zip(sample(words, 25), sample(colors, 25))
        ]

    @ui.refreshable_method
    def view(self, spymaster: ui.switch):
        if not self.done:
            ui.toggle(["red", "blue"]).bind_value(self, "turn")

        grid = ui.grid()
        (grid.tailwind
            .grid_template_columns("5")
            .grid_auto_rows("fr")
            .gap("0.5")
            .width("full")
            .aspect_ratio("square")
         )
        (grid
            .style("grid-template-columns: repeat(5, minmax(0, 1fr))")
            .style("overflow-wrap: anywhere"))
        with grid:
            for word in self.board:
                word.view(spymaster, partial(self.reveal, word))

    def reveal(self, word: Word):
        if word.revealed or self.done:
            return
        else:
            word.revealed = True
            word.view.refresh()

        if word.color != self.turn:
            self.turn = next(self.turns)
        self.done = word.color == "purple" or not any(
            self.turn == other.color and not other.revealed
            for other in self.board
        )
        self.view.refresh()


@ui.page("/game/{code}")
def game(code: str):
    ui.context.client.storage["code"] = code
    clients, game = games[code]
    clients.add(ui.context.client)
    ui.query("body").classes("max-w-2xl mx-auto")
    game.view(
        ui.switch("spymaster", on_change=lambda: game.view.refresh()),
    )


@niceapp.on_disconnect
def on_disconnect(client):
    clients, _ = games[code := client.storage.get("code")]
    clients.discard(client)
    if not clients:
        del games[code]


ui.navigate.to(f"/game/{'-'.join(sample(words, 3))}")
games: dict[str, Tuple[set, Game]] = (defaultdict(lambda: (set(), Game())))

ui.run_with(app := FastAPI())
