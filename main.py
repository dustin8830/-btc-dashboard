import threading
import requests

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


BG = (0.055, 0.075, 0.11, 1)
CARD = (0.10, 0.13, 0.19, 1)
ORANGE = (1, 0.60, 0.12, 1)
WHITE = (0.94, 0.96, 1, 1)
GREY = (0.60, 0.66, 0.75, 1)


class Chart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = []
        self.bind(pos=self.draw, size=self.draw)

    def update_values(self, values):
        self.values = values[-30:]
        self.draw()

    def draw(self, *args):
        self.canvas.clear()

        with self.canvas:
            Color(*CARD)
            Rectangle(pos=self.pos, size=self.size)

            if len(self.values) < 2:
                return

            low = min(self.values)
            high = max(self.values)
            diff = max(high - low, 0.001)

            points = []
            for i, value in enumerate(self.values):
                x = self.x + dp(12) + (
                    i / (len(self.values) - 1)
                ) * (self.width - dp(24))

                y = self.y + dp(15) + (
                    (value - low) / diff
                ) * (self.height - dp(30))

                points.extend([x, y])

            Color(*ORANGE)
            Line(points=points, width=dp(2.2))


class Dashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            **kwargs
        )

        self.prices = []
        self.price_text = self.label("-- EUR", 30, WHITE)
        self.network_text = self.label("-- EH/s", 21, ORANGE)
        self.status_text = self.label("Verbinde...", 14, GREY)

        self.add_widget(
            self.label("BTC MINER DASHBOARD", 23, ORANGE)
        )

        self.add_widget(
            self.label("BITCOIN MARKTÜBERSICHT", 11, GREY)
        )

        self.add_card(
            "BITCOIN PREIS",
            self.price_text
        )

        self.add_card(
            "NETZWERK HASHRATE",
            self.network_text
        )

        self.add_card(
            "KURSVERLAUF",
            Chart(size_hint_y=None, height=dp(150))
        )

        self.add_card(
            "MINING STATUS",
            self.label("Inaktiv", 19, ORANGE)
        )

        self.add_widget(self.status_text)

        Clock.schedule_once(
            lambda dt: self.refresh(),
            1
        )

        Clock.schedule_interval(
            lambda dt: self.refresh(),
            60
        )

    def label(self, text, size, color):
        return Label(
            text=text,
            font_size=dp(size),
            color=color,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(size + 18)
        )

    def add_card(self, title, content):
        card = BoxLayout(
            orientation="vertical",
            padding=dp(13),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(105)
        )

        with card.canvas.before:
            Color(*CARD)
            card.bg = Rectangle(
                pos=card.pos,
                size=card.size
            )

        card.bind(
            pos=lambda obj, val: setattr(
                obj.bg, "pos", val
            ),
            size=lambda obj, val: setattr(
                obj.bg, "size", val
            )
        )

        card.add_widget(
            self.label(title, 11, GREY)
        )

        card.add_widget(content)
        self.add_widget(card)

    def refresh(self):
        self.status_text.text = "Aktualisiere Daten..."

        threading.Thread(
            target=self.load_data,
            daemon=True
        ).start()

    def load_data(self):
        try:
            headers = {"User-Agent": "BTC-Dashboard/1.0"}

            price = requests.get(
                "https://mempool.space/api/v1/prices",
                headers=headers,
                timeout=12
            ).json()["EUR"]

            network = requests.get(
                "https://mempool.space/api/v1/mining/hashrate/3d",
                headers=headers,
                timeout=12
            ).json()["currentHashrate"]

            Clock.schedule_once(
                lambda dt: self.show_data(price, network)
            )

        except Exception as error:
            Clock.schedule_once(
                lambda dt: self.show_error(str(error)[:60])
            )

    def show_data(self, price, network):
        self.price_text.text = f"{price:,.2f} EUR"
        self.network_text.text = (
            f"{network / 1e18:.2f} EH/s"
        )

        self.prices.append(float(price))

        chart = self.children[1].children[0] \
            if False else None

        # Kurswerte für das Diagramm speichern
        self.status_text.text = "Live-Daten aktualisiert"

    def show_error(self, error):
        self.status_text.text = "Verbindungsfehler: " + error


class BTCApp(App):
    def build(self):
        self.title = "BTC Miner Dashboard"

        root = Dashboard()
        root.background_color = BG

        with root.canvas.before:
            Color(*BG)
            self.background = Rectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=lambda obj, val: setattr(
                self.background, "pos", val
            ),
            size=lambda obj, val: setattr(
                self.background, "size", val
            )
        )

        return root


BTCApp().run()
