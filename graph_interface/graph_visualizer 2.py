import pygame
import math
import sys
from graph_core import Graph

WIDTH, HEIGHT = 1200, 800
UI_W = 260
FPS = 60
NODE_R = 20
FONT = 'Helvetica Neue'
ANIM_DELAY = 500

BG = (240, 242, 245)
UI_BG = (235, 230, 245)
NODE_COL = (90, 50, 170)
NODE_HOVER = (120, 80, 210)
EDGE_COL = (100, 100, 110)
START_COL = (40, 200, 80)
END_COL = (220, 60, 60)
PATH_COL = (50, 100, 230)
MST_COL = (230, 150, 40)
TEXT = (40, 45, 50)
BTN_BG = (120, 60, 180)
BTN_HOVER = (155, 95, 225)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (180, 150, 220)
TYPE_BG = (250, 250, 255)


class GraphVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Интерактивный визуализатор графов")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT, 16)
        self.font_sm = pygame.font.SysFont(FONT, 13)

        self.graph = Graph()
        self.pos = {}
        self.temp_pos = (0, 0)
        self.dragging = None
        self.drag_off = (0, 0)

        self.mode = "IDLE"
        self.temp_u = None
        self.selected = None
        self.input_buf = ""
        self.status = "Добавить вершину."

        self.hl_nodes = set()
        self.hl_edges = set()
        self.start_node = None
        self.end_node = None
        self.graph_type_text = ""

        self.buttons = [
            ("Загрузить файл", "FILE_LOAD", 20),
            ("Синхронизировать", "SYNC", 65),
            ("Добавить ребро", "ADD_EDGE", 110),
            ("BFS (кратчайшие)", "BFS", 155),
            ("Дейкстра", "DIJKSTRA", 200),
            ("Краскал (MST)", "KRUSKAL", 245),
            ("Очистить граф", "CLEAR", 290),
            ("Сброс подсветки", "RESET", 335),
        ]
        self._update_graph_info()
        self._sync_positions()

    def _update_graph_info(self):
        d = "Ориентированный" if self.graph.directed else "Неориентированный"
        w = "Взвешенный" if self.graph.weighted else "Невзвешенный"
        self.graph_type_text = f"{d}, {w}"

    def _wrap_text(self, text, max_width):
        if not text: return ['']
        text = text.replace('\n', ' ')
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_sm.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def _sync_positions(self):
        n = len(self.graph.adjacency_list)
        if n == 0: return
        cx, cy = UI_W + (WIDTH - UI_W) // 2, HEIGHT // 2
        r = min(WIDTH - UI_W, HEIGHT) // 3 - 60
        existing = list(self.pos.keys())
        new_vertices = [v for v in self.graph.adjacency_list if v not in self.pos]
        start_idx = len(existing)
        for i, v in enumerate(new_vertices):
            ang = 2 * math.pi * (start_idx + i) / n
            self.pos[v] = (cx + r * math.cos(ang), cy + r * math.sin(ang))

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit();
                sys.exit()

            if ev.type == pygame.MOUSEBUTTONUP:
                self.dragging = None
                continue

            if ev.type == pygame.MOUSEBUTTONDOWN:
                self.dragging = None
                if mx < UI_W:
                    self.click_ui(mx, my)
                    continue

                clicked_v = None
                for v, (x, y) in self.pos.items():
                    if math.hypot(mx - x, my - y) < NODE_R + 5:
                        clicked_v = v
                        if self.mode == "IDLE":
                            self.dragging = v
                            self.drag_off = (mx - x, my - y)
                        break

                if clicked_v:
                    self._on_node_click(clicked_v)
                else:
                    if self.mode in ("IDLE", "ADD_EDGE_U", "DIJKSTRA_U", "BFS"):
                        self.temp_pos = (mx, my)
                        self.mode = "NAME_VERTEX"
                        self.input_buf = ""
                        self.status = "Введите имя вершины"
                    else:
                        self.status = "Сначала выберите режим или вершину."

            if ev.type == pygame.MOUSEMOTION and self.dragging:
                self.pos[self.dragging] = (mx - self.drag_off[0], my - self.drag_off[1])

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and self.mode != "IDLE":
                    self.mode = "IDLE"
                    self.input_buf = ""
                    self.status = "Операция отменена"
                    continue

                if self.mode in ("WEIGHT_INPUT", "FILE_LOAD", "NAME_VERTEX"):
                    if ev.key == pygame.K_RETURN:
                        if self.mode == "WEIGHT_INPUT":
                            self._confirm_weight()
                        elif self.mode == "FILE_LOAD":
                            self._load_file()
                        elif self.mode == "NAME_VERTEX":
                            self._confirm_vertex_name()
                    elif ev.key == pygame.K_BACKSPACE:
                        self.input_buf = self.input_buf[:-1]
                    else:
                        if self.mode == "NAME_VERTEX":
                            if ev.unicode.isalnum() or ev.unicode in ('_', '-'):
                                self.input_buf += ev.unicode
                        elif self.mode == "FILE_LOAD":
                            self.input_buf += ev.unicode
                        elif self.mode == "WEIGHT_INPUT":
                            if ev.unicode.isdigit() or ev.unicode in ('.', '-'):
                                self.input_buf += ev.unicode

    def _confirm_vertex_name(self):
        name = self.input_buf.strip()
        if not name:
            self.status = "Имя не может быть пустым"
            return
        if name in self.graph.adjacency_list:
            self.status = f"Ошибка: вершина '{name}' уже существует"
            self.mode = "IDLE"
            self.input_buf = ""
            return
        self.graph.add_vertex(name)
        self.pos[name] = self.temp_pos
        self.status = f"Добавлена вершина '{name}'"
        self.mode = "IDLE"
        self.input_buf = ""

    def click_ui(self, mx, my):
        for text, action, y in self.buttons:
            if pygame.Rect(15, y, UI_W - 30, 35).collidepoint((mx, my)):
                self._set_mode(action)
                return

    def _set_mode(self, action):
        self.input_buf = ""
        if action == "FILE_LOAD":
            self.mode = "FILE_LOAD"
            self.status = "Введите имя файла"
        elif action == "SYNC":
            self._sync_positions()
            self.status = "Координаты вершин обновлены"
        elif action == "ADD_EDGE":
            self.mode = "ADD_EDGE_U"
            self.status = "Кликните на ПЕРВУЮ вершину"
        elif action == "BFS":
            self.mode = "BFS"
            self.status = "Кликните на стартовую вершину для BFS"
        elif action == "DIJKSTRA":
            self.mode = "DIJKSTRA_U"
            self.status = "Кликните на вершину (начало)"
        elif action == "KRUSKAL":
            self.run_kruskal()
        elif action == "CLEAR":
            self.graph = Graph()
            self.pos = {}
            self.reset_highlight()
            self._update_graph_info()
            self.status = "Граф очищен"
        elif action == "RESET":
            self.reset_highlight()
            self.status = "Подсветка сброшена"

    def _on_node_click(self, v):
        if self.mode == "ADD_EDGE_U":
            self.temp_u = v
            self.mode = "ADD_EDGE_V"
            self.status = f"Выбрана {v}. Кликните на ВТОРУЮ вершину."
        elif self.mode == "ADD_EDGE_V":
            if v == self.temp_u:
                self.status = "Ребро в петлю не добавляется"
                return
            self.selected = v
            self.mode = "WEIGHT_INPUT"
            self.status = "Введите вес ребра:"
        elif self.mode == "DIJKSTRA_U":
            self.start_node = v
            self.hl_nodes.add(v)
            self.mode = "DIJKSTRA_V"
            self.status = f"Старт: {v}. Кликните на вершину (конец)"
        elif self.mode == "DIJKSTRA_V":
            self.end_node = v
            self.hl_nodes.add(v)
            self.run_dijkstra(self.start_node, v)
            self.mode = "IDLE"
        elif self.mode == "BFS":
            self.run_bfs(v)
            self.mode = "IDLE"
        else:
            self.status = f"Вершина {v} выделена"

    def _confirm_weight(self):
        if self.temp_u is None: return
        try:
            w = float(self.input_buf) if self.input_buf else 1.0
            self.graph.add_edge(self.temp_u, self.selected, weight=w)
            self.status = f"Ребро {self.temp_u}-{self.selected} добавлено"
        except ValueError:
            self.status = "Неверный вес. Используйте числа."
        self.mode = "IDLE"
        self.temp_u = None
        self.selected = None
        self.input_buf = ""

    def _load_file(self):
        filename = self.input_buf.strip()
        if not filename: return
        try:
            new_g = Graph()
            new_g.load_from_file(filename)
            self.graph = new_g
            self.pos = {}
            self._sync_positions()
            self.reset_highlight()
            self._update_graph_info()
            self.status = f"Загружено {len(self.graph.adjacency_list)} вершин"
        except FileNotFoundError:
            self.status = f"Файл '{filename}' не найден"
        except Exception as e:
            self.status = f"Ошибка загрузки: {e}"
        finally:
            self.mode = "IDLE"
            self.input_buf = ""

    def reset_highlight(self):
        self.hl_nodes.clear()
        self.hl_edges.clear()
        self.start_node = self.end_node = None

    def _step_delay(self):
        pygame.time.delay(ANIM_DELAY)
        pygame.event.pump()

    def run_bfs(self, start):
        if start not in self.graph.adjacency_list:
            self.status = "Вершина не существует"
            return
        self.status = "Запуск BFS..."
        res = self.graph.shortest_paths_bfs(start)
        self.hl_nodes.add(start)
        self.draw()
        self._step_delay()

        reachable = [(v, d, p) for v, (d, p) in res.items() if p and d != -1]
        reachable.sort(key=lambda x: x[1])

        for v, d, path in reachable:
            self.hl_nodes.add(v)
            for i in range(len(path) - 1):
                u, n = path[i], path[i + 1]
                key = (u, n) if self.graph.directed else tuple(sorted([u, n]))
                self.hl_edges.add(key)
            self.status = f"BFS: посещена {v} (расст. {d})"
            self.draw()
            self._step_delay()
        self.status = "BFS завершён. Путь выделен синим."

    def run_dijkstra(self, u, v):
        if u not in self.graph.adjacency_list or v not in self.graph.adjacency_list:
            self.status = "Одна из вершин не существует"
            return
        self.status = "Запуск Дейкстры..."
        res = self.graph.dijkstra_shortest_path(u, v)
        self.hl_nodes.add(u)
        self.draw()
        self._step_delay()

        if res and 'path' in res and res['path']:
            path = res['path']
            for i in range(1, len(path)):
                curr = path[i]
                prev = path[i - 1]
                self.hl_nodes.add(curr)
                key = (prev, curr) if self.graph.directed else tuple(sorted([prev, curr]))
                self.hl_edges.add(key)
                self.status = f"Дейкстра: шаг {i}/{len(path) - 1} -> {curr}"
                self.draw()
                self._step_delay()
            self.status = f"Кратчайший путь: {' -> '.join(path)} (вес: {res['distance']})"
        else:
            self.status = "Путь не найден"

    def run_kruskal(self):
        if self.graph.directed or not self.graph.weighted:
            self.status = "Краскал требует неориентированного взвешенного графа"
            return
        self.status = "Запуск Краскала..."
        res = self.graph.kruskal_mst()
        if res:
            _, total, edges = res
            for i, (u, v, w) in enumerate(edges):
                key = tuple(sorted([u, v]))
                self.hl_edges.add(key)
                self.status = f"Краскал: добавлено ребро {u}-{v} (шаг {i + 1}/{len(edges)})"
                self.draw()
                self._step_delay()
            self.status = f"MST построен. Общий вес: {total}. Рёбра выделены оранжевым."
        else:
            self.status = "Не удалось построить MST"

    def draw(self):
        self.screen.fill(BG)
        self.screen.fill(UI_BG, (0, 0, UI_W, HEIGHT))

        pygame.draw.rect(self.screen, TYPE_BG, (UI_W, 0, WIDTH - UI_W, 40))
        txt = self.font.render(self.graph_type_text, True, (60, 60, 80))
        self.screen.blit(txt, (UI_W + 20, 10))

        drawn = set()
        for u, edges in self.graph.adjacency_list.items():
            for e in edges:
                v = e[0]
                key = (u, v) if self.graph.directed else tuple(sorted([u, v]))
                if not self.graph.directed and key in drawn: continue
                drawn.add(key)
                if u in self.pos and v in self.pos:
                    self._draw_edge(u, v, key, e[1] if len(e) > 1 else 1)

        for v, (x, y) in self.pos.items():
            col = NODE_HOVER if v == self.dragging else NODE_COL
            if v == self.start_node:
                col = START_COL
            elif v == self.end_node:
                col = END_COL
            elif v in self.hl_nodes:
                col = (100, 180, 255)
            pygame.draw.circle(self.screen, col, (int(x), int(y)), NODE_R)
            pygame.draw.circle(self.screen, TEXT, (int(x), int(y)), NODE_R, 2)
            txt = self.font.render(str(v), True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=(int(x), int(y))))

        for text, _, y in self.buttons:
            rect = pygame.Rect(15, y, UI_W - 30, 35)
            hover = rect.collidepoint(pygame.mouse.get_pos())
            col = BTN_HOVER if hover else BTN_BG
            pygame.draw.rect(self.screen, col, rect, border_radius=6)
            t = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=rect.center))

        input_rect = pygame.Rect(15, 560, UI_W - 30, 120)
        pygame.draw.rect(self.screen, INPUT_BG, input_rect, border_radius=6)
        pygame.draw.rect(self.screen, INPUT_BORDER, input_rect, 2, border_radius=6)

        max_w = UI_W - 40
        display_lines = self._wrap_text(self.status, max_w)
        if self.mode in ("WEIGHT_INPUT", "FILE_LOAD", "NAME_VERTEX"):
            display_lines.extend(self._wrap_text(f"> {self.input_buf}", max_w))

        for i, line in enumerate(display_lines[:6]):
            txt = self.font_sm.render(line, True, TEXT)
            self.screen.blit(txt, (20, 565 + i * 18))

        legend = [("🟢 Старт", START_COL), ("🔴 Конец", END_COL), ("🔵 Путь", PATH_COL), ("🟠 MST", MST_COL)]
        for i, (txt, col) in enumerate(legend):
            pygame.draw.circle(self.screen, col, (25, 690 + i * 18), 6)
            t = self.font_sm.render(txt, True, TEXT)
            self.screen.blit(t, (35, 685 + i * 18))

        pygame.display.flip()

    def _draw_edge(self, u, v, key, weight):
        x1, y1 = self.pos[u]
        x2, y2 = self.pos[v]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0: return

        # Укорачиваем линию, чтобы не заходить в круги
        ux1 = x1 + (dx / dist) * NODE_R
        uy1 = y1 + (dy / dist) * NODE_R
        ux2 = x2 - (dx / dist) * NODE_R
        uy2 = y2 - (dy / dist) * NODE_R

        # Перпендикулярное смещение для направленных рёбер
        off_x, off_y = 0.0, 0.0
        if self.graph.directed:
            shift = 12  # Расстояние между параллельными рёбрами
            px, py = -dy / dist, dx / dist  # Нормализованный перпендикуляр
            off_x, off_y = px * shift, py * shift

        ux1 += off_x;
        uy1 += off_y
        ux2 += off_x;
        uy2 += off_y

        col = EDGE_COL
        if key in self.hl_edges:
            col = MST_COL if "MST" in self.status else PATH_COL
        pygame.draw.line(self.screen, col, (ux1, uy1), (ux2, uy2), 3 if key in self.hl_edges else 2)

        if self.graph.directed:
            ang = math.atan2(dy, dx)
            pygame.draw.polygon(self.screen, col, [
                (ux2, uy2),
                (ux2 - 10 * math.cos(ang - math.pi / 6), uy2 - 10 * math.sin(ang - math.pi / 6)),
                (ux2 - 10 * math.cos(ang + math.pi / 6), uy2 - 10 * math.sin(ang + math.pi / 6))
            ])

        # Вес тоже смещаем вместе с ребром
        if self.graph.weighted and weight is not None and weight != 0:
            mx = (x1 + x2) / 2 + off_x
            my = (y1 + y2) / 2 + off_y
            txt = self.font_sm.render(str(weight), True, (80, 80, 90))
            pygame.draw.circle(self.screen, BG, (mx + 12, my - 12), 14)
            self.screen.blit(txt, (mx + 4, my - 22))


if __name__ == "__main__":
    GraphVisualizer().run()