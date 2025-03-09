from collections import defaultdict
from functools import partial
from itertools import cycle
from random import sample
from typing import Tuple
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from nicegui import app as niceapp, ui


with open("words") as f:
    words = f.read().splitlines()

colors = ["red"] * 9 + ["blue"] * 8 + ["gray"] * 7 + ["purple"]


class Game:
    def __init__(self):
        self.turns = cycle(["red", "blue"])
        self.turn = next(self.turns)
        self.done = False
        self.board = {
            word: (color, False)
            for word, color in zip(sample(words, 25), sample(colors, 25))
        }

    @ui.refreshable_method
    def view(self, spymaster: ui.switch):
        def reveal(word: str):
            color, revealed = self.board[word]
            if revealed or self.done:
                return
            self.board[word] = color, True

            if color != self.turn:
                self.turn = next(self.turns)
            self.done = color == "purple" or not any(
                cell == (self.turn, False)
                for cell in self.board.values()
            )
            self.view.refresh()

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
            for word, (color, revealed) in self.board.items():
                btn = ui.button(
                    word,
                    color=(color + "-200" * (not revealed)
                           if spymaster.value or revealed else "white"),
                    on_click=partial(reveal, word)
                )
                btn.props("padding=0")
                btn.tailwind.font_size("xs")


@ui.page("/game/{code}")
def game(code: str):
    ui.context.client.storage["code"] = code
    clients, game = games[code]
    clients.add(ui.context.client)
    ui.query("body").classes("max-w-2xl mx-auto")
    game.view(
        ui.switch("Spymaster", on_change=lambda: game.view.refresh()),
    )


@niceapp.on_disconnect
def on_disconnect(client):
    clients, _ = games[code := client.storage.get("code")]
    clients.discard(client)
    if not clients:
        del games[code]


app = FastAPI()


@app.get("/")
def index():
    return RedirectResponse(f"/game/{'-'.join(sample(words, 3))}")


games: dict[str, Tuple[set, Game]] = defaultdict(lambda: (set(), Game()))

ui.run_with(app)
