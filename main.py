"""
2048 — mobile neon UI (Kivy)
Swipe or arrow controls, score + leaderboard.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex, platform
import json
import os
import random
from datetime import datetime

# Desktop preview size (ignored on Android/iOS)
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 780
GRID_SIZE = 4
ANIMATION_DURATION = 0.12
SWIPE_MIN_DIST = 40

Window.clearcolor = get_color_from_hex('#0B0B12')
if platform in ('win', 'linux', 'macosx'):
    Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)


def rgba(hex_color, alpha=1.0):
    """Convert #RRGGBB to Kivy RGBA tuple."""
    c = get_color_from_hex(hex_color)
    return (c[0], c[1], c[2], alpha)


class Game2048Logic:
    """Core game logic for 2048"""
    
    def __init__(self, size=4):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        self.game_started = False
        
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        """Add a new random tile (2 or 4)"""
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = random.choice([2, 2, 2, 4])
            return (i, j)
        return None

    def compress(self, line):
        """Remove zeros from line"""
        return [x for x in line if x != 0] + [0] * (self.size - len([x for x in line if x != 0]))

    def merge(self, line):
        """Merge tiles and calculate score"""
        line = self.compress(line)
        score_gained = 0
        merged = False
        
        for i in range(self.size - 1):
            if line[i] != 0 and line[i] == line[i + 1]:
                line[i] *= 2
                score_gained += line[i]
                line[i + 1] = 0
                merged = True
        
        return self.compress(line), score_gained

    def move(self, direction):
        """Move tiles in specified direction"""
        if self.game_over:
            return False

        old_board = [row[:] for row in self.board]
        score_gained = 0

        if direction == 'left':
            for i in range(self.size):
                self.board[i], gained = self.merge(self.board[i])
                score_gained += gained

        elif direction == 'right':
            for i in range(self.size):
                row = self.board[i][::-1]
                row, gained = self.merge(row)
                self.board[i] = row[::-1]
                score_gained += gained

        elif direction == 'up':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)]
                col, gained = self.merge(col)
                for i in range(self.size):
                    self.board[i][j] = col[i]
                score_gained += gained

        elif direction == 'down':
            for j in range(self.size):
                col = [self.board[i][j] for i in range(self.size)][::-1]
                col, gained = self.merge(col)
                col = col[::-1]
                for i in range(self.size):
                    self.board[i][j] = col[i]
                score_gained += gained

        # Check if board changed
        if old_board != self.board:
            self.score += score_gained
            self.moves += 1
            self.game_started = True
            self.add_new_tile()
            self.check_game_state()
            return True
        return False

    def check_game_state(self):
        """Check if game is won or over"""
        if any(2048 in row for row in self.board):
            self.won = True
        if not self.has_possible_moves():
            self.game_over = True

    def has_possible_moves(self):
        """Check if any moves are possible"""
        # Check for empty cells
        for row in self.board:
            if 0 in row:
                return True

        # Check for possible merges
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                if j < self.size - 1 and current == self.board[i][j + 1]:
                    return True
                if i < self.size - 1 and current == self.board[i + 1][j]:
                    return True
        return False

    def reset(self):
        """Reset the game"""
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.won = False
        self.game_started = False
        self.add_new_tile()
        self.add_new_tile()

    def get_board(self):
        """Get current board state"""
        return self.board

    def to_dict(self):
        return {
            'board': [row[:] for row in self.board],
            'score': self.score,
            'moves': self.moves,
            'game_over': self.game_over,
            'won': self.won,
            'game_started': self.game_started,
        }

    def load_dict(self, data):
        board = data.get('board')
        if not isinstance(board, list) or len(board) != self.size:
            return False
        for row in board:
            if not isinstance(row, list) or len(row) != self.size:
                return False
        self.board = [list(row) for row in board]
        self.score = int(data.get('score', 0))
        self.moves = int(data.get('moves', 0))
        self.game_over = bool(data.get('game_over', False))
        self.won = bool(data.get('won', False))
        self.game_started = bool(data.get('game_started', False))
        return True


class LeaderboardManager:
    """Manage game scores and leaderboard"""
    
    def __init__(self, filename='leaderboard.json'):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_score(self, score, moves, timestamp=None):
        """Save a new score"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.scores.append({
            'score': score,
            'moves': moves,
            'timestamp': timestamp
        })
        
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:20]
        self.save_to_file()

    def save_to_file(self):
        """Save scores to file"""
        directory = os.path.dirname(self.filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.scores, f, indent=2)

    def get_top_scores(self, count=10):
        """Get top scores"""
        return self.scores[:count]

    def get_best_score(self):
        """Get the best score"""
        if self.scores:
            return self.scores[0]['score']
        return 0


class Game2048UI:
    """Mobile neon tile theme (matches colorful dark 2048 UI)."""

    # Vibrant tile colors from the mobile reference
    TILE_COLORS = {
        0: rgba('#1C1C26'),
        2: rgba('#7A2BE2'),      # purple
        4: rgba('#E91E8C'),      # hot pink
        8: rgba('#F5C400'),      # gold
        16: rgba('#8FE600'),     # lime
        32: rgba('#3B1B7A'),     # deep indigo
        64: rgba('#FF2D6F'),     # pink-red
        128: rgba('#FF8A00'),    # orange
        256: rgba('#00C9A7'),    # teal
        512: rgba('#2F9BFF'),    # sky blue
        1024: rgba('#FF4D9A'),   # magenta
        2048: rgba('#00E5FF'),   # bright cyan
        4096: rgba('#B388FF'),
        8192: rgba('#FF6E40'),
    }

    BACKGROUND = rgba('#0B0B12')
    BOARD_BG = rgba('#12121A')
    BOARD_BORDER = rgba('#3D2A6B')
    PANEL_BG = rgba('#16161F')
    BUTTON_COLOR = rgba('#7A2BE2')
    BUTTON_SECONDARY = rgba('#2F9BFF')
    BUTTON_DANGER = rgba('#FF2D6F')
    BUTTON_SUCCESS = rgba('#00C9A7')
    ACCENT_COLOR = rgba('#00E5FF')
    TEXT_MUTED = rgba('#9AA0B4')
    TEXT_WHITE = (1, 1, 1, 1)

    @staticmethod
    def get_tile_color(value):
        return Game2048UI.TILE_COLORS.get(value, rgba('#5C6BC0'))

    @staticmethod
    def get_text_color(value):
        # All filled tiles use white numbers like the mobile UI
        if value == 0:
            return (0, 0, 0, 0)
        return Game2048UI.TEXT_WHITE

    @staticmethod
    def font_size_for(value):
        if value >= 1000:
            return '22sp'
        if value >= 100:
            return '26sp'
        return '32sp'


class Tile(Label):
    """Colored rounded tile with white number."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.halign = 'center'
        self.valign = 'middle'
        self.bold = True
        self.color = Game2048UI.TEXT_WHITE
        self._tile_value = 0
        with self.canvas.before:
            self._bg_color = Color(*Game2048UI.get_tile_color(0))
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._sync_canvas, size=self._sync_canvas)

    def _sync_canvas(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self.text_size = self.size

    def set_value(self, value):
        self._tile_value = value
        self._bg_color.rgba = Game2048UI.get_tile_color(value)
        self.color = Game2048UI.get_text_color(value)
        self.font_size = Game2048UI.font_size_for(value)
        self.text = '' if value == 0 else str(value)


class RoundedPanel(BoxLayout):
    """Dark rounded container for the board / score cards."""

    def __init__(self, bg_color=None, radius=18, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self._radius = dp(radius)
        bg = bg_color or Game2048UI.BOARD_BG
        with self.canvas.before:
            if border_color:
                self._border_color = Color(*border_color)
                self._border = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            self._bg_color = Color(*bg)
            inset = dp(2) if border_color else 0
            self._inset = inset
            self._bg = RoundedRectangle(
                pos=(self.x + inset, self.y + inset),
                size=(self.width - inset * 2, self.height - inset * 2),
                radius=[max(0, self._radius - inset)],
            )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_args):
        inset = getattr(self, '_inset', 0)
        if hasattr(self, '_border'):
            self._border.pos = self.pos
            self._border.size = self.size
        self._bg.pos = (self.x + inset, self.y + inset)
        self._bg.size = (self.width - inset * 2, self.height - inset * 2)


class Game2048App(App):
    """Main application — mobile neon UI + swipe controls"""
    
    def build(self):
        self.title = '2048'
        
        self.game = Game2048Logic(GRID_SIZE)
        # Writable path on Android/iOS; local folder on desktop
        data_dir = self.user_data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.leaderboard = LeaderboardManager(
            os.path.join(data_dir, 'leaderboard.json')
        )
        self._save_path = os.path.join(data_dir, 'save.json')
        self.best_score = self.leaderboard.get_best_score()
        self._touch_start = None
        self._popup = None
        self._win_dialog_shown = False
        self._score_saved = False
        self.load_progress()

        root = FloatLayout()
        with root.canvas.before:
            Color(*Game2048UI.BACKGROUND)
            self._root_bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(self._root_bg, 'pos', root.pos),
                  size=lambda *_: setattr(self._root_bg, 'size', root.size))

        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(20), dp(16), dp(16)],
            spacing=dp(12),
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
        )

        main_layout.add_widget(self.create_header())

        # Board with dark rounded frame
        board_wrap = RoundedPanel(
            orientation='vertical',
            bg_color=Game2048UI.BOARD_BG,
            border_color=Game2048UI.BOARD_BORDER,
            radius=22,
            padding=dp(10),
            size_hint_y=0.58,
        )
        self.grid = GridLayout(cols=4, rows=4, spacing=dp(8), size_hint=(1, 1))
        self.tile_labels = []
        for _ in range(16):
            tile = Tile()
            self.tile_labels.append(tile)
            self.grid.add_widget(tile)
        board_wrap.add_widget(self.grid)
        board_wrap.bind(
            on_touch_down=self.on_board_touch_down,
            on_touch_up=self.on_board_touch_up,
        )
        main_layout.add_widget(board_wrap)

        # Swipe hint
        hint = Label(
            text='Swipe or use arrows',
            size_hint_y=0.04,
            font_size='12sp',
            color=Game2048UI.TEXT_MUTED,
        )
        main_layout.add_widget(hint)

        main_layout.add_widget(self.create_controls())
        main_layout.add_widget(self.create_arrows())

        root.add_widget(main_layout)
        self._main = main_layout

        self.update_display()
        self.bind_keyboard()
        if self.game.game_over:
            Clock.schedule_once(lambda dt: self.show_game_over_dialog(), 0.2)
        elif self.game.won and not self._win_dialog_shown:
            Clock.schedule_once(lambda dt: self.show_won_dialog(), 0.2)
        return root

    def on_pause(self):
        self.save_progress()
        return True

    def on_stop(self):
        self.save_progress()

    def load_progress(self):
        if not os.path.exists(self._save_path):
            return
        try:
            with open(self._save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if self.game.load_dict(data):
                self._win_dialog_shown = bool(data.get('win_dialog_shown', self.game.won))
                self._score_saved = bool(data.get('score_saved', False))
        except Exception:
            pass

    def save_progress(self):
        payload = self.game.to_dict()
        payload['win_dialog_shown'] = self._win_dialog_shown
        payload['score_saved'] = self._score_saved
        try:
            with open(self._save_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
        except Exception:
            pass

    def persist_finished_score(self):
        if self._score_saved or not self.game.game_over or self.game.score <= 0:
            return
        self.leaderboard.save_score(self.game.score, self.game.moves)
        self._score_saved = True
        if self.game.score > self.best_score:
            self.best_score = self.game.score
        self.best_display.text = str(max(self.best_score, self.game.score))

    def open_popup(self, popup):
        self._popup = popup
        popup.bind(on_dismiss=self._on_popup_dismiss)
        popup.open()

    def _on_popup_dismiss(self, *_args):
        self._popup = None

    def create_header(self):
        header = BoxLayout(orientation='vertical', size_hint_y=0.16, spacing=dp(8))

        title = Label(
            text='2048',
            font_size='40sp',
            bold=True,
            size_hint_y=0.45,
            color=Game2048UI.TEXT_WHITE,
        )
        header.add_widget(title)

        score_row = BoxLayout(size_hint_y=0.55, spacing=dp(8))

        def make_stat(title_text, attr_name, initial):
            box = RoundedPanel(
                orientation='vertical',
                bg_color=Game2048UI.PANEL_BG,
                radius=14,
                padding=[dp(6), dp(4)],
            )
            box.add_widget(Label(
                text=title_text,
                size_hint_y=0.4,
                font_size='11sp',
                bold=True,
                color=Game2048UI.TEXT_MUTED,
            ))
            value = Label(
                text=str(initial),
                font_size='22sp',
                bold=True,
                color=Game2048UI.ACCENT_COLOR,
            )
            setattr(self, attr_name, value)
            box.add_widget(value)
            return box

        score_row.add_widget(make_stat('SCORE', 'score_display', 0))
        score_row.add_widget(make_stat('BEST', 'best_display', self.best_score))
        score_row.add_widget(make_stat('MOVES', 'moves_display', 0))
        header.add_widget(score_row)
        return header

    def create_controls(self):
        controls = BoxLayout(size_hint_y=0.08, spacing=dp(8))

        up_btn = Button(
            text='UP',
            background_normal='',
            background_color=Game2048UI.BUTTON_COLOR,
            bold=True,
            color=Game2048UI.TEXT_WHITE,
        )
        up_btn.bind(on_press=lambda x: self.move_game('up'))

        new_game_btn = Button(
            text='NEW',
            background_normal='',
            background_color=Game2048UI.BUTTON_DANGER,
            bold=True,
            color=Game2048UI.TEXT_WHITE,
        )
        new_game_btn.bind(on_press=self.reset_game)

        leaderboard_btn = Button(
            text='TOP',
            background_normal='',
            background_color=Game2048UI.BUTTON_SUCCESS,
            bold=True,
            color=Game2048UI.TEXT_WHITE,
        )
        leaderboard_btn.bind(on_press=self.show_leaderboard)

        controls.add_widget(up_btn)
        controls.add_widget(new_game_btn)
        controls.add_widget(leaderboard_btn)
        return controls

    def create_arrows(self):
        arrows = BoxLayout(size_hint_y=0.09, spacing=dp(8))

        def arrow(text, direction):
            btn = Button(
                text=text,
                background_normal='',
                background_color=Game2048UI.BUTTON_SECONDARY,
                bold=True,
                color=Game2048UI.TEXT_WHITE,
            )
            btn.bind(on_press=lambda x: self.move_game(direction))
            return btn

        arrows.add_widget(arrow('LEFT', 'left'))
        arrows.add_widget(arrow('DOWN', 'down'))
        arrows.add_widget(arrow('RIGHT', 'right'))
        return arrows

    def on_board_touch_down(self, widget, touch):
        if self._popup or not widget.collide_point(*touch.pos):
            return False
        self._touch_start = (touch.x, touch.y)
        return False

    def on_board_touch_up(self, widget, touch):
        if self._popup or not self._touch_start:
            self._touch_start = None
            return False
        dx = touch.x - self._touch_start[0]
        dy = touch.y - self._touch_start[1]
        self._touch_start = None
        if abs(dx) < SWIPE_MIN_DIST and abs(dy) < SWIPE_MIN_DIST:
            return False
        if abs(dx) > abs(dy):
            self.move_game('right' if dx > 0 else 'left')
        else:
            self.move_game('up' if dy > 0 else 'down')
        return True

    def bind_keyboard(self):
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        # Let Android Back / Esc leave the app or close a popup.
        if key in (27, 1001):
            if self._popup:
                self._popup.dismiss()
                return True
            return False
        key_map = {
            273: 'up',
            274: 'down',
            275: 'right',
            276: 'left',
            119: 'up',    # w
            97: 'left',   # a
            115: 'down',  # s
            100: 'right', # d
        }
        if key in key_map:
            self.move_game(key_map[key])
            return True
        return False

    def move_game(self, direction):
        if self._popup:
            return
        if self.game.move(direction):
            self.update_display()
            self.save_progress()
            if self.game.game_over:
                Clock.schedule_once(lambda dt: self.show_game_over_dialog(), 0.35)
            elif self.game.won and not self._win_dialog_shown:
                self._win_dialog_shown = True
                self.save_progress()
                Clock.schedule_once(lambda dt: self.show_won_dialog(), 0.35)

    def update_display(self):
        self.score_display.text = str(self.game.score)
        self.moves_display.text = str(self.game.moves)
        self.best_display.text = str(max(self.best_score, self.game.score))

        for i in range(16):
            row, col = divmod(i, 4)
            value = self.game.board[row][col]
            tile = self.tile_labels[i]
            tile.set_value(value)
            # pop animation on non-empty tiles
            if value:
                tile.opacity = 0.7
                Animation(opacity=1, duration=ANIMATION_DURATION).start(tile)

    def reset_game(self, instance):
        self.persist_finished_score()
        self.game.reset()
        self._win_dialog_shown = False
        self._score_saved = False
        self.update_display()
        self.save_progress()

    def show_game_over_dialog(self):
        if self._popup:
            return
        self.persist_finished_score()
        self.save_progress()
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text=f'Game Over\n\nScore: {self.game.score}\nMoves: {self.game.moves}',
            font_size='18sp',
            color=Game2048UI.TEXT_WHITE,
            size_hint_y=0.6,
        ))
        button_layout = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        new_game_btn = Button(text='New Game', background_normal='', background_color=Game2048UI.BUTTON_COLOR)
        leaderboard_btn = Button(text='Leaderboard', background_normal='', background_color=Game2048UI.BUTTON_SUCCESS)
        button_layout.add_widget(new_game_btn)
        button_layout.add_widget(leaderboard_btn)
        content.add_widget(button_layout)

        popup = Popup(
            title='Game Over',
            content=content,
            size_hint=(0.85, 0.45),
            background_color=Game2048UI.PANEL_BG,
            separator_color=Game2048UI.BOARD_BORDER,
            title_color=Game2048UI.TEXT_WHITE,
        )
        new_game_btn.bind(on_press=lambda x: self.close_and_reset(popup))
        leaderboard_btn.bind(on_press=lambda x: self.close_and_show_leaderboard(popup))
        self.open_popup(popup)

    def show_won_dialog(self):
        if self._popup:
            return
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text=f'You reached 2048!\n\nScore: {self.game.score}\nMoves: {self.game.moves}\n\nKeep going?',
            font_size='18sp',
            color=Game2048UI.TEXT_WHITE,
            size_hint_y=0.6,
        ))
        button_layout = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        continue_btn = Button(text='Continue', background_normal='', background_color=Game2048UI.BUTTON_SUCCESS)
        new_game_btn = Button(text='New Game', background_normal='', background_color=Game2048UI.BUTTON_COLOR)
        button_layout.add_widget(continue_btn)
        button_layout.add_widget(new_game_btn)
        content.add_widget(button_layout)

        popup = Popup(
            title='You Won!',
            content=content,
            size_hint=(0.85, 0.45),
            background_color=Game2048UI.PANEL_BG,
            separator_color=Game2048UI.BOARD_BORDER,
            title_color=Game2048UI.TEXT_WHITE,
        )
        continue_btn.bind(on_press=popup.dismiss)
        new_game_btn.bind(on_press=lambda x: self.close_and_reset(popup))
        self.open_popup(popup)

    def show_leaderboard(self, instance):
        scores = self.leaderboard.get_top_scores(20)
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(
            text='Top Scores',
            font_size='22sp',
            bold=True,
            size_hint_y=0.1,
            color=Game2048UI.TEXT_WHITE,
        ))

        scroll = ScrollView(size_hint=(1, 0.8))
        score_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        score_list.bind(minimum_height=score_list.setter('height'))

        if scores:
            for idx, score_data in enumerate(scores, 1):
                score_text = f"{idx}. {score_data['score']} pts · {score_data['moves']} moves · {score_data['timestamp']}"
                score_list.add_widget(Label(
                    text=score_text,
                    font_size='12sp',
                    size_hint_y=None,
                    height=dp(36),
                    color=Game2048UI.TEXT_MUTED,
                ))
        else:
            score_list.add_widget(Label(
                text='No scores yet. Start playing!',
                font_size='14sp',
                color=Game2048UI.TEXT_MUTED,
            ))

        scroll.add_widget(score_list)
        content.add_widget(scroll)

        close_btn = Button(
            text='Close',
            size_hint_y=0.1,
            background_normal='',
            background_color=Game2048UI.BUTTON_COLOR,
        )
        content.add_widget(close_btn)

        popup = Popup(
            title='Leaderboard',
            content=content,
            size_hint=(0.9, 0.75),
            background_color=Game2048UI.PANEL_BG,
            separator_color=Game2048UI.BOARD_BORDER,
            title_color=Game2048UI.TEXT_WHITE,
        )
        close_btn.bind(on_press=popup.dismiss)
        self.open_popup(popup)

    def close_and_reset(self, popup):
        popup.dismiss()
        self.reset_game(None)

    def close_and_show_leaderboard(self, popup):
        popup.dismiss()
        self.show_leaderboard(None)


if __name__ == '__main__':
    Game2048App().run()
