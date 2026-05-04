class Graph:
    def __init__(self, directed=False, adjacency_list=None, weighted=False):
        if adjacency_list is None:
            self.adjacency_list = {}
        else:
            self.adjacency_list = {v: list(adj) for v, adj in adjacency_list.items()}
        self.directed = directed
        self.weighted = weighted  # Атрибут для определения взвешенности графа

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Определяем тип графа (направленный/ненаправленный) и взвешенный/невзвешенный
        header = lines[0].strip().lower().split()
        self.directed = header[0] == 'directed'
        self.weighted = header[1] == 'weighted'

        # Используем словарь для хранения графа
        self.graph = {}
        all_vertices = set()

        for i, line in enumerate(lines[1:]):
            parts = line.strip().split()

            if len(parts) == 1:
                vertex = parts[0]
                all_vertices.add(vertex)
                self.graph.setdefault(vertex, [])
                continue

            if self.weighted:
                u, v, weight = parts[0], parts[1], float(parts[2])
                all_vertices.update([u, v])
                self.graph.setdefault(u, []).append((v, weight))
                if not self.directed:
                    if u != v:
                        self.graph.setdefault(v, []).append((u, weight))
            else:
                u, v = parts[0], parts[1]
                all_vertices.update([u, v])
                # ИСПРАВЛЕНИЕ: добавляем кортеж из одного элемента (v,), а не (v, None)
                self.graph.setdefault(u, []).append((v,))
                if not self.directed:
                    if u != v:
                        self.graph.setdefault(v, []).append((u,))

        # Обеспечиваем наличие всех вершин, включая обособленные
        for vertex in all_vertices:
            if vertex not in self.graph:
                self.graph[vertex] = []

        # Копируем данные из self.graph в self.adjacency_list для дальнейшего использования
        self.adjacency_list = self.graph.copy()

        # Вывод содержимого графа:
        print(f"Граф из файла '{filename}' загружен. Вот его содержимое:")
        for vertex, edges in self.graph.items():
            if edges:
                if self.weighted:
                    edges_str = ', '.join(f"{v} (вес: {weight})" for v, weight in edges)
                else:
                    # ИСПРАВЛЕНИЕ: для невзвешенного графа edges теперь состоит из кортежей (v,)
                    edges_str = ', '.join(v for v, in edges)
                print(f"{vertex}: {edges_str}")
            else:
                if self.directed:
                    has_incoming = any(vertex in [v for v, *_ in adj] for adj in self.graph.values())
                    if has_incoming:
                        print(f"{vertex}: нет исходящих рёбер")
                    else:
                        print(f"{vertex}: нет рёбер")
                else:
                    print(f"{vertex}: нет рёбер")

        # Вывод типа графа:
        graph_type = "Ориентированный" if self.directed else "Неориентированный"
        weight_type = "Взвешенный" if self.weighted else "Невзвешенный"
        print(f"Тип графа: {graph_type}, {weight_type}")

    def display_adjacency_list(self):
        for vertex in self.adjacency_list:
            if self.weighted:
                edges = ', '.join(f"{adj} ({weight})" for adj, weight in self.adjacency_list[vertex])
            else:
                edges = ', '.join(str(adj) for adj, *_ in self.adjacency_list[vertex])
            print(f"{vertex}: {edges if edges else ''}")

    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
        else:
            print(f"Вершина {vertex} уже существует.")

    def add_edge(self, u, v, weight=None, overwrite=False):
        # Проверяем существование обеих вершин
        if u not in self.adjacency_list or v not in self.adjacency_list:
            print(f"Ошибка: Вершины '{u}' и/или '{v}' не существуют.")
            return False

        # Определяем вес ребра
        if self.weighted:
            if weight is None:
                print("Ошибка: Для взвешенного графа необходимо указать вес ребра.")
                return False
        else:
            weight = None  # В невзвешенном графе вес не хранится

        # Проверяем существование ребра
        existing_edge = None
        if self.weighted:
            # Для взвешенного графа - ищем кортеж (сосед, вес)
            for i, edge in enumerate(self.adjacency_list[u]):
                if isinstance(edge, tuple) and len(edge) >= 1 and edge[0] == v:
                    existing_edge = (i, edge[1] if len(edge) > 1 else None)
                    break
        else:
            # Для невзвешенного графа - может быть (v,) или (v, None)
            for i, edge in enumerate(self.adjacency_list[u]):
                if isinstance(edge, tuple) and len(edge) >= 1 and edge[0] == v:
                    existing_edge = i
                    break

        if existing_edge is not None:
            if overwrite:
                if self.weighted:
                    index, _ = existing_edge
                    self.adjacency_list[u][index] = (v, weight)
                else:
                    index = existing_edge
                    self.adjacency_list[u][index] = (v,)  # Всегда сохраняем как (v,) для невзвешенного
                print(f"Ребро {u}-{v} обновлено.")
            else:
                print(f"Ребро {u}-{v} уже существует.")
                return False
        else:
            if self.weighted:
                self.adjacency_list[u].append((v, weight))
                print(f"Ребро {u}-{v} добавлено с весом {weight}.")
            else:
                self.adjacency_list[u].append((v,))  # Всегда добавляем как (v,)
                print(f"Ребро {u}-{v} добавлено.")

        if not self.directed and u != v:
            # Проверяем существование обратного ребра
            existing_reverse_edge = None
            if self.weighted:
                for i, edge in enumerate(self.adjacency_list[v]):
                    if isinstance(edge, tuple) and len(edge) >= 1 and edge[0] == u:
                        existing_reverse_edge = (i, edge[1] if len(edge) > 1 else None)
                        break
            else:
                for i, edge in enumerate(self.adjacency_list[v]):
                    if isinstance(edge, tuple) and len(edge) >= 1 and edge[0] == u:
                        existing_reverse_edge = i
                        break

            if existing_reverse_edge is not None:
                if overwrite and self.weighted:
                    index, _ = existing_reverse_edge
                    self.adjacency_list[v][index] = (u, weight)
            else:
                if self.weighted:
                    self.adjacency_list[v].append((u, weight))
                else:
                    self.adjacency_list[v].append((u,))

        return True

    def remove_vertex(self, vertex):
        if vertex in self.adjacency_list:
            # Удаляем все рёбра, связанные с этой вершиной
            self.adjacency_list.pop(vertex)
            for adj in self.adjacency_list:
                if self.weighted:
                    self.adjacency_list[adj] = [(v, w) for v, w in self.adjacency_list[adj] if v != vertex]
                else:
                    self.adjacency_list[adj] = [v for v, *_ in self.adjacency_list[adj] if v != vertex]
        else:
            print(f"Вершина {vertex} не существует.")

    def remove_edge(self, u, v):
        if u in self.adjacency_list:
            if self.weighted:
                original_length = len(self.adjacency_list[u])
                self.adjacency_list[u] = [(x, w) for x, w in self.adjacency_list[u] if x != v]
                if len(self.adjacency_list[u]) < original_length:
                    print(f"Ребро {u}-{v} удалено.")
                else:
                    print(f"Ребро {u}-{v} не существует.")
            else:
                original_length = len(self.adjacency_list[u])
                # Для невзвешенного графа - фильтруем по первому элементу кортежа
                self.adjacency_list[u] = [x for x in self.adjacency_list[u] if x[0] != v]
                if len(self.adjacency_list[u]) < original_length:
                    print(f"Ребро {u}-{v} удалено.")
                else:
                    print(f"Ребро {u}-{v} не существует.")

            if not self.directed:
                if self.weighted:
                    self.adjacency_list[v] = [(x, w) for x, w in self.adjacency_list[v] if x != u]
                else:
                    self.adjacency_list[v] = [x for x in self.adjacency_list[v] if x[0] != u]
        else:
            print(f"Вершина {u} не существует.")

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            type_line = ""
            if self.directed and self.weighted:
                type_line = "directed weighted"
            elif self.directed and not self.weighted:
                type_line = "directed unweighted"
            elif not self.directed and self.weighted:
                type_line = "undirected weighted"
            else:
                type_line = "undirected unweighted"
            file.write(f"{type_line}\n")
            for vertex in self.adjacency_list:
                if not self.adjacency_list[vertex]:
                    file.write(f"{vertex}\n")
                else:
                    for edge in self.adjacency_list[vertex]:
                        if self.directed or (not self.directed and vertex < edge[0]):
                            if self.weighted:
                                file.write(f"{vertex} {edge[0]} {edge[1]}\n")
                            else:
                                file.write(f"{vertex} {edge[0]}\n")

    def __str__(self):
        # Вывод графа в виде строки с указанием весов рёбер, включая петли
        result = ""
        for vertex in self.adjacency_list:
            result += f"{vertex}: "
            if self.weighted:
                edges = ", ".join(f"{adj} ({weight})" for adj, weight in self.adjacency_list[vertex])
            else:
                edges = ", ".join(adj for adj, *_ in self.adjacency_list[vertex])
            result += f"{edges}\n"
        return result

    def edges(self):
        edge_list = []
        seen_edges = set()
        for vertex in self.adjacency_list:
            for edge in self.adjacency_list[vertex]:
                neighbor = edge[0]
                weight = edge[1] if self.weighted else None
                if self.directed:
                    edge_repr = (vertex, neighbor, weight) if self.weighted else (vertex, neighbor)
                    edge_list.append(edge_repr)
                else:
                    # Для неориентированного графа избегаем дублирования ребер
                    edge_key = tuple(sorted([vertex, neighbor]))
                    if edge_key not in seen_edges:
                        edge_repr = (vertex, neighbor, weight) if self.weighted else (vertex, neighbor)
                        edge_list.append(edge_repr)
                        seen_edges.add(edge_key)
        return edge_list

    # Задание 1. Для данной вершины орграфа вывести все «заходящие» соседние вершины
    def incoming_neighbors(self, target_vertex):
        if target_vertex not in self.adjacency_list:
            print(f"Ошибка: Вершина '{target_vertex}' не существует в графе.")
            return []

        if not self.directed:
            print("Граф неориентированный. В неориентированном графе понятие 'заходящие' вершины не применяется.")
            print("Все соседние вершины являются одновременно входящими и исходящими.")
            # Для неориентированного графа выводим всех соседей
            neighbors = [neighbor for neighbor, *_ in self.adjacency_list[target_vertex]]
            print(f"Вершины, смежные с {target_vertex}: {neighbors}")
            return neighbors

        incoming = []
        for vertex, neighbors in self.adjacency_list.items():
            if any(neighbor == target_vertex for neighbor, *_ in neighbors):
                incoming.append(vertex)

        print(f"Вершины, которые имеют ребра, направленные на {target_vertex}: {incoming}")
        return incoming

    # Задание 2: Для каждой вершины графа вывести её степень
    def print_vertex_degrees(self):
        print("Степени вершин:")

        if self.directed:
            # Для ориентированного графа - полустепени захода и исхода
            print("Ориентированный граф - полустепени захода и исхода:")

            # Вычисляем полустепени захода
            indegree = {vertex: 0 for vertex in self.adjacency_list}
            for vertex, neighbors in self.adjacency_list.items():
                for neighbor, *_ in neighbors:
                    indegree[neighbor] += 1

            # Вычисляем полустепени исхода (просто длина списка смежности)
            outdegree = {vertex: len(neighbors) for vertex, neighbors in self.adjacency_list.items()}

            # Выводим результаты
            for vertex in sorted(self.adjacency_list.keys()):
                print(f"Вершина {vertex}:")
                print(f"  Полустепень захода = {indegree[vertex]}")
                print(f"  Полустепень исхода = {outdegree[vertex]}")
                print(f"  Полная степень = {indegree[vertex] + outdegree[vertex]}")
                print()
        else:
            # Для неориентированного графа - просто степень
            print("Неориентированный граф - степень каждой вершины:")

            for vertex in sorted(self.adjacency_list.keys()):
                # В неориентированном графе степень равна количеству соседей
                # (для петель считаю дважды)
                degree = 0
                for neighbor, *_ in self.adjacency_list[vertex]:
                    if neighbor == vertex:  # петля
                        degree += 2
                    else:
                        degree += 1
                print(f"Вершина {vertex}: степень = {degree}")

    # Задание 3: Удаление висячих вершин
    def remove_pendant_vertices(self):

        # Находим висячие вершины
        pendant_vertices = self._find_pendant_vertices()

        print(f"Найдены висячие вершины: {sorted(pendant_vertices) if pendant_vertices else 'нет'}")

        # Если нет висячих вершин, возвращаем копию текущего графа
        if not pendant_vertices:
            print("Висячих вершин не найдено. Граф остался без изменений.")
            return self._copy_graph()

        # Создаём новый граф без висячих вершин
        result_graph = Graph(directed=self.directed, weighted=self.weighted)

        # Добавляем все вершины, кроме висячих
        for vertex in self.adjacency_list:
            if vertex not in pendant_vertices:
                result_graph.add_vertex(vertex)

        # Добавляем все рёбра, не связанные с висячими вершинами
        for vertex in self.adjacency_list:
            if vertex not in pendant_vertices:
                for edge in self.adjacency_list[vertex]:
                    neighbor = edge[0]
                    if neighbor not in pendant_vertices:
                        if self.weighted:
                            weight = edge[1]
                            result_graph.add_edge(vertex, neighbor, weight=weight)
                        else:
                            result_graph.add_edge(vertex, neighbor)

        # Показываем процесс удаления
        print(f"\nУдалены висячие вершины: {sorted(pendant_vertices)}")
        print("Рёбра, связанные с этими вершинами, также удалены.")

        return result_graph

    def _find_pendant_vertices(self):

        pendant = set()

        if self.directed:
            # Для ориентированного графа
            indegree = {vertex: 0 for vertex in self.adjacency_list}
            outdegree = {vertex: len(neighbors) for vertex, neighbors in self.adjacency_list.items()}

            # Вычисляем полустепени захода
            for vertex, neighbors in self.adjacency_list.items():
                for neighbor, *_ in neighbors:
                    indegree[neighbor] += 1

            # Находим висячие вершины
            for vertex in self.adjacency_list:
                total_degree = indegree[vertex] + outdegree[vertex]
                # Проверяем, есть ли петля
                has_loop = any(neighbor == vertex for neighbor, *_ in self.adjacency_list[vertex])

                # Висячая вершина: общая степень = 1 и нет петли
                if total_degree == 1 and not has_loop:
                    pendant.add(vertex)
        else:
            # Для неориентированного графа
            for vertex in self.adjacency_list:
                degree = 0
                has_loop = False
                for neighbor, *_ in self.adjacency_list[vertex]:
                    if neighbor == vertex:
                        has_loop = True
                        degree += 2  # Петля даёт вклад 2
                    else:
                        degree += 1

                # Висячая вершина: степень = 1 и нет петли
                if degree == 1 and not has_loop:
                    pendant.add(vertex)

        return pendant

    def _copy_graph(self):

        copy_graph = Graph(directed=self.directed, weighted=self.weighted)

        # Копируем вершины
        for vertex in self.adjacency_list:
            copy_graph.add_vertex(vertex)

        # Копируем рёбра
        for vertex in self.adjacency_list:
            for edge in self.adjacency_list[vertex]:
                if self.weighted:
                    neighbor, weight = edge[0], edge[1]
                    copy_graph.add_edge(vertex, neighbor, weight=weight)
                else:
                    neighbor = edge[0]
                    copy_graph.add_edge(vertex, neighbor)

        return copy_graph

    # Задание 4: Проверить, является ли заданный орграф ацикличным (DFS)
    def is_acyclic(self):


        if not self.directed:
            print("Граф неориентированный. Для неориентированных графов понятие 'ацикличный' означает 'дерево'.")
            print("Проверка выполняется для неориентированного графа...")
            return self._is_acyclic_undirected()

        # Для ориентированного графа используем DFS с тремя состояниями
        # 0 - не посещена, 1 - в процессе обхода, 2 - полностью обработана
        state = {vertex: 0 for vertex in self.adjacency_list}
        parent = {vertex: None for vertex in self.adjacency_list}
        cycle_found = False
        cycle_vertices = []

        def dfs(vertex):
            nonlocal cycle_found
            state[vertex] = 1  # В процессе обхода

            for neighbor, *_ in self.adjacency_list[vertex]:
                if state[neighbor] == 0:  # Не посещена
                    parent[neighbor] = vertex
                    dfs(neighbor)
                    if cycle_found:
                        return
                elif state[neighbor] == 1:  # Нашли обратное ребро (цикл)
                    cycle_found = True
                    # Восстанавливаем цикл
                    cycle_vertices.append(neighbor)
                    v = vertex
                    while v != neighbor:
                        cycle_vertices.append(v)
                        v = parent[v]
                    cycle_vertices.append(neighbor)
                    cycle_vertices.reverse()
                    return

            state[vertex] = 2  # Полностью обработана

        # Запускаем DFS из всех непосещённых вершин
        for vertex in self.adjacency_list:
            if state[vertex] == 0:
                dfs(vertex)
                if cycle_found:
                    break

        print("\nРезультат проверки:")
        if cycle_found:
            print("Граф содержит цикл!")
            print(f"Найден цикл: {' → '.join(cycle_vertices)}")
            return False
        else:
            print("Граф ацикличный")
            return True

    def _is_acyclic_undirected(self):

        visited = {vertex: False for vertex in self.adjacency_list}
        parent = {vertex: None for vertex in self.adjacency_list}
        cycle_found = False
        cycle_vertices = []

        def dfs(vertex):
            nonlocal cycle_found
            visited[vertex] = True

            for neighbor, *_ in self.adjacency_list[vertex]:
                if not visited[neighbor]:
                    parent[neighbor] = vertex
                    dfs(neighbor)
                    if cycle_found:
                        return
                elif parent[vertex] != neighbor:  # Нашли ребро к уже посещённой вершине (не родителю)
                    cycle_found = True
                    # Восстанавливаем цикл
                    cycle_vertices.append(neighbor)
                    v = vertex
                    while v != neighbor:
                        cycle_vertices.append(v)
                        v = parent[v]
                    cycle_vertices.append(neighbor)
                    cycle_vertices.reverse()
                    return

        # Запускаем DFS из всех непосещённых вершин
        for vertex in self.adjacency_list:
            if not visited[vertex]:
                dfs(vertex)
                if cycle_found:
                    break

        if cycle_found:
            print(f"Граф содержит цикл!")
            print(f"Найден цикл: {' - '.join(cycle_vertices)}")
            return False
        else:
            print("Граф ацикличный (не содержит циклов)")
            return True

    # Задание 5: Вывести кратчайшие (по числу дуг) пути из вершины u во все остальные (BFS)
    def shortest_paths_bfs(self, start_vertex):

        if start_vertex not in self.adjacency_list:
            print(f"Ошибка: Вершина '{start_vertex}' не существует в графе.")
            return {}

        # Инициализация
        distances = {vertex: -1 for vertex in self.adjacency_list}  # -1 означает недостижима
        parents = {vertex: None for vertex in self.adjacency_list}
        distances[start_vertex] = 0

        # Очередь для BFS
        queue = [start_vertex]

        print(f"\nПроцесс обхода в ширину из вершины {start_vertex}:")

        step = 0
        while queue:
            current = queue.pop(0)  # Берём первый элемент из очереди
            step += 1
            print(f"Шаг {step}: Посещаем вершину {current}, расстояние = {distances[current]}")

            for neighbor, *_ in self.adjacency_list[current]:
                if distances[neighbor] == -1:  # Вершина ещё не посещена
                    distances[neighbor] = distances[current] + 1
                    parents[neighbor] = current
                    queue.append(neighbor)
                    print(f"Найдена вершина {neighbor}, расстояние = {distances[neighbor]}")

        # Вывод результатов
        results = {}
        for vertex in sorted(self.adjacency_list.keys()):
            if vertex == start_vertex:
                print(f"\n{vertex} (стартовая вершина): расстояние 0")
                results[vertex] = (0, [vertex])
            elif distances[vertex] == -1:
                print(f"\n{vertex}: недостижима")
                results[vertex] = (-1, None)
            else:
                # Восстанавливаем путь
                path = []
                current = vertex
                while current is not None:
                    path.append(current)
                    current = parents[current]
                path.reverse()

                path_str = ' → '.join(path)
                print(f"\n{vertex}: расстояние = {distances[vertex]}")
                print(f"  Путь: {path_str}")
                results[vertex] = (distances[vertex], path)

        return results


    # Задание 6: Алгоритм Краскала для поиска минимального остовного дерева
    def kruskal_mst(self):

        # Проверка: граф должен быть неориентированным и взвешенным
        if self.directed:
            print("Ошибка: Алгоритм Краскала работает только для неориентированных графов!")
            return None

        if not self.weighted:
            print("Ошибка: Алгоритм Краскала работает только для взвешенных графов!")
            return None

        # Получаем все рёбра графа
        edges = []
        for vertex in self.adjacency_list:
            for neighbor, weight in self.adjacency_list[vertex]:
                # Добавляем каждое ребро только один раз (используем лексикографический порядок)
                if vertex < neighbor:
                    edges.append((weight, vertex, neighbor))

        if not edges:
            print("Граф не содержит рёбер. Невозможно построить остовное дерево.")
            return None

        # Сортируем рёбра по весу (возрастание)
        edges.sort(key=lambda x: x[0])

        print(f"\nВсего рёбер в графе: {len(edges)}")
        print("Рёбра, отсортированные по весу:")
        for weight, u, v in edges:
            print(f"  {u} - {v} (вес: {weight})")

        # Инициализация системы непересекающихся множеств (DSU)
        parent = {vertex: vertex for vertex in self.adjacency_list}
        rank = {vertex: 0 for vertex in self.adjacency_list}

        def find(vertex):
            if parent[vertex] != vertex:
                parent[vertex] = find(parent[vertex])
            return parent[vertex]

        def union(vertex1, vertex2):
            root1 = find(vertex1)
            root2 = find(vertex2)

            if root1 == root2:
                return False  # Уже в одном множестве

            # Объединяем по рангу
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            elif rank[root1] > rank[root2]:
                parent[root2] = root1
            else:
                parent[root2] = root1
                rank[root1] += 1

            return True  # Успешно объединены

        # Алгоритм Краскала
        mst_edges = []
        total_weight = 0
        edges_considered = 0


        for weight, u, v in edges:
            edges_considered += 1
            print(f"\nРассматриваем ребро {edges_considered}: {u} - {v} (вес: {weight})")

            if find(u) != find(v):
                # Рёбра не создают цикл - добавляем в MST
                union(u, v)
                mst_edges.append((u, v, weight))
                total_weight += weight
                print(f"Ребро добавлено в остовное дерево")
                print(f"Текущий вес MST: {total_weight}")
            else:
                print(f"Ребро пропущено (создаёт цикл)")

        # Проверяем, получилось ли связное остовное дерево
        # Находим корень для первой вершины
        first_vertex = list(self.adjacency_list.keys())[0]
        root = find(first_vertex)

        # Проверяем, все ли вершины в одном множестве
        all_connected = True
        for vertex in self.adjacency_list:
            if find(vertex) != root:
                all_connected = False
                break

        # Вывод результатов

        if not all_connected:
            print("\nВнимание: Граф не является связным!")
            print("Построен минимальный остовный лес.")
            print(f"Найдено компонент связности: {len(set(find(v) for v in self.adjacency_list))}")

        print(f"\nКоличество рёбер в MST: {len(mst_edges)}")
        print(f"Общий вес MST: {total_weight}")

        if mst_edges:
            print("\nРёбра минимального остовного дерева (в порядке добавления):")
            for i, (u, v, weight) in enumerate(mst_edges, 1):
                print(f"  {i}. {u} - {v} (вес: {weight})")

            # Выводим рёбра, отсортированные по вершинам
            print("\nРёбра минимального остовного дерева (в алфавитном порядке):")
            sorted_edges = sorted(mst_edges, key=lambda x: (x[0], x[1]))
            for u, v, weight in sorted_edges:
                print(f"  {u} - {v} (вес: {weight})")

        # Создаём граф-результат (остовное дерево)
        mst_graph = Graph(directed=False, weighted=True)

        # Добавляем все вершины
        for vertex in self.adjacency_list:
            mst_graph.add_vertex(vertex)

        # Добавляем рёбра MST
        for u, v, weight in mst_edges:
            mst_graph.add_edge(u, v, weight=weight)

        return mst_graph, total_weight, mst_edges

    # Вспомогательный метод для визуализации остовного дерева
    def display_mst_comparison(self, mst_graph, total_weight):

        print("\nИсходный граф:")
        self.display_adjacency_list()

        print(f"\nМинимальное остовное дерево (общий вес: {total_weight}):")
        mst_graph.display_adjacency_list()






        # Задание 7: Алгоритм Дейкстры - кратчайший путь из u в v (нет отрицательных весов)
    def dijkstra_shortest_path(self, start, end):

        # Проверка существования вершин
        if start not in self.adjacency_list:
            print(f"Ошибка: Вершина '{start}' не существует в графе.")
            return None
        if end not in self.adjacency_list:
            print(f"Ошибка: Вершина '{end}' не существует в графе.")
            return None

        # Проверка на отрицательные веса (только для взвешенных графов)
        if self.weighted:
            for vertex in self.adjacency_list:
                for neighbor, weight in self.adjacency_list[vertex]:
                    if weight < 0:
                        print("Ошибка: Алгоритм Дейкстры не работает с отрицательными весами")
                        return None

        # Инициализация
        distances = {vertex: float('inf') for vertex in self.adjacency_list}
        parents = {vertex: None for vertex in self.adjacency_list}
        distances[start] = 0
        visited = set()

        print(f"\nНачальная вершина: {start}")
        print(f"Целевая вершина: {end}")
        print("\nПроцесс работы алгоритма Дейкстры:")

        step = 0
        while len(visited) < len(self.adjacency_list):
            # Находим непосещённую вершину с минимальным расстоянием
            current = None
            min_distance = float('inf')
            for vertex in self.adjacency_list:
                if vertex not in visited and distances[vertex] < min_distance:
                    min_distance = distances[vertex]
                    current = vertex

            if current is None:
                break  # Нет достижимых вершин

            visited.add(current)
            step += 1
            print(f"\nШаг {step}: Выбрана вершина {current}, расстояние = {distances[current]}")

            # Если достигли целевой вершины, можно остановиться
            if current == end:
                print(f"\n Достигнута целевая вершина {end}")
                break

            # Обновляем расстояния до соседей
            for edge in self.adjacency_list[current]:
                if self.weighted:
                    neighbor, weight = edge[0], edge[1]
                else:
                    neighbor = edge[0]
                    weight = 1  # Для невзвешенного графа вес = 1

                if neighbor not in visited:
                    new_distance = distances[current] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        parents[neighbor] = current
                        print(f" - Обновлена вершина {neighbor}: {distances[neighbor]} (через {current})")

        # Восстанавливаем путь
        if distances[end] == float('inf'):
            print(f"\nПуть из {start} в {end} не существует")
            return None

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()

        # Вывод результатов
        print(f"Кратчайшее расстояние из {start} в {end}: {distances[end]}")
        print(f"Путь: {' → '.join(path)}")

        return {
            'distance': distances[end],
            'path': path,
            'distances': distances,
            'parents': parents
        }

    # Задание 8: Алгоритм Беллмана-Форда - вершины на расстоянии ≤ N (нет циклов отриц. веса)
    def bellman_ford_vertices_within_distance(self, start, max_distance):

        # Проверка существования вершины
        if start not in self.adjacency_list:
            print(f"Ошибка: Вершина '{start}' не существует в графе.")
            return None

        # Инициализация
        distances = {vertex: float('inf') for vertex in self.adjacency_list}
        distances[start] = 0
        parents = {vertex: None for vertex in self.adjacency_list}

        # Получаем все рёбра
        edges = []
        for vertex in self.adjacency_list:
            for edge in self.adjacency_list[vertex]:
                if self.weighted:
                    neighbor, weight = edge[0], edge[1]
                else:
                    neighbor = edge[0]
                    weight = 1  # Для невзвешенного графа вес = 1
                edges.append((vertex, neighbor, weight))

        print(f"\nНачальная вершина: {start}")
        print(f"Максимальное расстояние: {max_distance}")
        print(f"Всего рёбер в графе: {len(edges)}")

        # Алгоритм Беллмана-Форда
        print("\nПроцесс работы алгоритма Беллмана-Форда:")

        # Релаксация рёбер |V| - 1 раз
        V = len(self.adjacency_list)
        for i in range(V - 1):
            updated = False
            print(f"\nИтерация {i + 1}:")
            for u, v, weight in edges:
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    parents[v] = u
                    updated = True
                    print(f" -Обновлена вершина {v}: {distances[v]} (через {u}, вес {weight})")
            if not updated:
                print("  Нет обновлений, алгоритм завершён досрочно")
                break

        # Проверка на циклы отрицательного веса
        has_negative_cycle = False
        for u, v, weight in edges:
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                has_negative_cycle = True
                print(f"\n Найден цикл отрицательного веса. (ребро {u} → {v})")
                break

        if has_negative_cycle:
            print("\nВ графе есть циклы отрицательного веса.")
            print("Алгоритм Беллмана-Форда не гарантирует корректность результата.")

        # Находим вершины с расстоянием ≤ max_distance
        result_vertices = []

        for vertex in sorted(self.adjacency_list.keys()):
            if distances[vertex] <= max_distance:
                result_vertices.append(vertex)
                status = "Достижима" if distances[vertex] != float('inf') else "Недостижима"
                if distances[vertex] != float('inf'):
                    print(f"{vertex}: расстояние = {distances[vertex]} - {status}")
                else:
                    print(f"{vertex}: недостижима - {status}")

        print(f"\nВершины, расстояние до которых не превышает {max_distance}:")
        if result_vertices:
            print(f"  {', '.join(result_vertices)}")
            print(f"Всего вершин: {len(result_vertices)}")
        else:
            print("  Нет таких вершин")

        return {
            'vertices': result_vertices,
            'distances': distances,
            'parents': parents,
            'has_negative_cycle': has_negative_cycle
        }

    # Задание 9: Алгоритм Флойда-Уоршелла - кратчайшие пути до u из всех вершин (могут быть отриц. циклы)
    def floyd_warshall_paths_to_vertex(self, target):

        # Проверка существования вершины
        if target not in self.adjacency_list:
            print(f"Ошибка: Вершина '{target}' не существует в графе.")
            return None

        # Получаем список всех вершин
        vertices = sorted(self.adjacency_list.keys())
        vertex_to_index = {v: i for i, v in enumerate(vertices)}
        index_to_vertex = {i: v for i, v in enumerate(vertices)}
        n = len(vertices)

        # Инициализация матрицы расстояний
        dist = [[float('inf')] * n for _ in range(n)]
        next_vertex = [[None] * n for _ in range(n)]

        # Расстояние до себя = 0
        for i in range(n):
            dist[i][i] = 0

        # Заполняем расстояния из рёбер
        for vertex in self.adjacency_list:
            i = vertex_to_index[vertex]
            for edge in self.adjacency_list[vertex]:
                if self.weighted:
                    neighbor, weight = edge[0], edge[1]
                else:
                    neighbor = edge[0]
                    weight = 1  # Для невзвешенного графа вес = 1

                j = vertex_to_index[neighbor]
                if weight < dist[i][j]:
                    dist[i][j] = weight
                    next_vertex[i][j] = j

        # Инициализируем next_vertex для прямых рёбер
        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] != float('inf') and next_vertex[i][j] is None:
                    next_vertex[i][j] = j

        print(f"\nЦелевая вершина: {target}")
        print(f"Всего вершин в графе: {n}")

        # Алгоритм Флойда-Уоршелла
        print("\nПроцесс работы алгоритма Флойда-Уоршелла:")

        for k in range(n):
            print(f"\nИтерация {k + 1}: используем вершину {index_to_vertex[k]} как промежуточную")
            updates = 0
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        if dist[i][k] + dist[k][j] < dist[i][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            next_vertex[i][j] = next_vertex[i][k]
                            updates += 1
            print(f"  Выполнено обновлений: {updates}")

        # Проверка на циклы отрицательного веса
        has_negative_cycle = False
        for i in range(n):
            if dist[i][i] < 0:
                has_negative_cycle = True
                print(f"\nНайден цикл отрицательного веса в вершине {index_to_vertex[i]}")
                break

        if has_negative_cycle:
            print("\nВ графе есть циклы отрицательного веса")
            print("Кратчайшие пути могут быть не определены (можно уйти в -∞)")

        # Находим пути до target из всех вершин
        target_idx = vertex_to_index[target]


        results = {}
        for vertex in vertices:
            i = vertex_to_index[vertex]
            distance = dist[i][target_idx]

            if distance == float('inf'):
                print(f"\n{vertex} → {target}: недостижима")
                results[vertex] = (None, None)
            elif distance == float('-inf'):
                print(f"\n{vertex} → {target}: путь не ограничен (цикл отрицательного веса)")
                results[vertex] = (float('-inf'), None)
            else:
                # Восстанавливаем путь
                path = []
                if i == target_idx:
                    path = [vertex]
                elif next_vertex[i][target_idx] is not None:
                    current = i
                    while current != target_idx:
                        path.append(index_to_vertex[current])
                        current = next_vertex[current][target_idx]
                        if current is None:
                            break
                    path.append(target)

                path_str = ' → '.join(path) if path else "путь не найден"
                print(f"\n{vertex} → {target}:")
                print(f"  Расстояние: {distance}")
                print(f"  Путь: {path_str}")
                results[vertex] = (distance, path)

        return {
            'distances': dist,
            'next_vertex': next_vertex,
            'target': target,
            'target_idx': target_idx,
            'results': results,
            'has_negative_cycle': has_negative_cycle
        }

    # Вспомогательный метод для восстановления пути (используется в Флойде-Уоршелле)
    def _reconstruct_path_floyd(self, next_vertex, start, end, index_to_vertex, vertex_to_index):

        #Восстанавливает путь из start в end по матрице next_vertex
        if next_vertex[vertex_to_index[start]][vertex_to_index[end]] is None:
            return None

        path = [start]
        current = start
        while current != end:
            current_idx = vertex_to_index[current]
            end_idx = vertex_to_index[end]
            next_idx = next_vertex[current_idx][end_idx]
            if next_idx is None:
                return None
            current = index_to_vertex[next_idx]
            path.append(current)
        return path




    # Задание 10: Алгоритм Эдмондса-Карпа для нахождения максимального потока
    def max_flow_edmonds_karp(self, source, sink):

        # Проверка: граф должен быть ориентированным
        if not self.directed:
            print("Ошибка: Алгоритм поиска максимального потока работает только для ориентированных графов.")
            return None

        # Проверка: граф должен быть взвешенным
        if not self.weighted:
            print("Ошибка: Для поиска максимального потока граф должен быть взвешенным.")
            return None

        # Проверка существования вершин
        if source not in self.adjacency_list:
            print(f"Ошибка: Вершина-исток '{source}' не существует в графе")
            return None
        if sink not in self.adjacency_list:
            print(f"Ошибка: Вершина-сток '{sink}' не существует в графе")
            return None

        print(f"\nИсток: {source}")
        print(f"Сток: {sink}")

        # Получаем все вершины графа
        all_vertices = list(self.adjacency_list.keys())

        # Создаём остаточную сеть (матрица смежности)
        # Используем словарь словарей, но предварительно инициализируем все вершины
        residual = {}
        for u in all_vertices:
            residual[u] = {}
            for v in all_vertices:
                residual[u][v] = 0  # Инициализируем нулями

        # Заполняем пропускные способности из исходного графа
        for u in self.adjacency_list:
            for edge in self.adjacency_list[u]:
                v, capacity = edge[0], edge[1]
                residual[u][v] = capacity

        # Словарь для хранения потока по рёбрам
        flow = {}
        for u in all_vertices:
            for v in all_vertices:
                flow[(u, v)] = 0

        # Функция BFS для поиска увеличивающего пути
        def bfs_find_path(parent):
            visited = {vertex: False for vertex in all_vertices}
            queue = [source]
            visited[source] = True

            while queue:
                u = queue.pop(0)

                # Проверяем всех возможных соседей
                for v in all_vertices:
                    if not visited[v] and residual[u][v] > 0:
                        visited[v] = True
                        parent[v] = u
                        if v == sink:
                            return True
                        queue.append(v)
            return False

        # Основной цикл алгоритма Эдмондса-Карпа
        max_flow_value = 0
        iteration = 0
        paths_found = []

        print("Процесс нахождения максимального потока:")

        parent = {}

        while bfs_find_path(parent):
            iteration += 1

            # Находим минимальную остаточную пропускную способность на найденном пути
            path_flow = float('inf')
            v = sink
            path_edges = []

            while v != source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                path_edges.append((u, v))
                v = u

            # Обновляем остаточные пропускные способности
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow

                # Обновляем поток
                flow[(u, v)] += path_flow

                v = u

            max_flow_value += path_flow

            # Сохраняем информацию о найденном пути
            path_edges.reverse()
            paths_found.append({
                'iteration': iteration,
                'path': path_edges,
                'flow': path_flow
            })

            print(f"\nИтерация {iteration}:")
            print(f"  Найден путь: {' → '.join([u for u, v in path_edges] + [sink])}")
            print(f"  Добавляемый поток: {path_flow}")
            print(f"  Текущий максимальный поток: {max_flow_value}")

            # Сбрасываем parent для следующей итерации
            parent = {}

        # Вывод результатов
        print("\nРезультат работы алгоритма Эдмондса-Карпа:")

        if max_flow_value == 0:
            print(f"\nМаксимальный поток из {source} в {sink}: 0 (путей не найдено)")
            return {
                'max_flow': 0,
                'flow_distribution': dict(flow),
                'iterations': iteration,
                'paths_found': paths_found,
                'min_cut': None
            }

        print(f"\nМаксимальный поток из {source} в {sink}: {max_flow_value}")
        print(f"Количество итераций (найденных путей): {iteration}")

        print("-" * 40)
        print("\nРаспределение потока по рёбрам:")
        for (u, v), f in sorted(flow.items()):
            if f > 0:
                # Находим исходную пропускную способность
                original_capacity = None
                for edge in self.adjacency_list[u]:
                    if edge[0] == v:
                        original_capacity = edge[1]
                        break
                if original_capacity is not None:
                    print(f"  {u} → {v}: {f} / {original_capacity}")
                else:
                    print(f"  {u} → {v}: {f}")

        # Вывод минимального разреза
        print("-" * 40)
        print("\nМинимальный разрез (вершины, достижимые из истока в остаточной сети):")
        reachable = set()
        queue = [source]
        visited = {vertex: False for vertex in all_vertices}
        visited[source] = True

        while queue:
            u = queue.pop(0)
            reachable.add(u)
            for v in all_vertices:
                if not visited[v] and residual[u][v] > 0:
                    visited[v] = True
                    queue.append(v)

        not_reachable = set(all_vertices) - reachable
        print(f"  Достижимые из истока: {sorted(reachable)}")
        print(f"  Недостижимые: {sorted(not_reachable)}")

        # Вывод рёбер, входящих в разрез
        cut_edges = []
        cut_capacity = 0
        for u in reachable:
            for edge in self.adjacency_list[u]:
                v = edge[0]
                if v in not_reachable:
                    cut_edges.append((u, v, edge[1]))
                    cut_capacity += edge[1]

        if cut_edges:
            print(f"\nРёбра, образующие минимальный разрез:")
            for u, v, cap in cut_edges:
                print(f"  {u} → {v} (пропускная способность: {cap})")
            print(f"  Суммарная пропускная способность разреза: {cut_capacity}")

            if cut_capacity == max_flow_value:
                print(" Теорема Форда-Фалкерсона подтверждена: поток = пропускной способности разреза")

        return {
            'max_flow': max_flow_value,
            'flow_distribution': dict(flow),
            'iterations': iteration,
            'paths_found': paths_found,
            'min_cut': (list(reachable), list(not_reachable), cut_edges)
        }




def console_interface():
    print("Добро пожаловать в систему работы с графом!")
    initial_choice = input("Введите '1' для загрузки из файла или '2' для создания нового графа: ").strip()

    if initial_choice == '1':
        filename = input("Введите имя файла с графом: ").strip()
        try:
            graph = Graph()  # Инициализируем граф перед загрузкой
            graph.load_from_file(filename)
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден. Создан пустой граф.")
            # Запрашиваем тип графа при создании пустого графа
            graph = create_new_graph()
        except ValueError as ve:
            print(f"Ошибка при загрузке графа: {ve}")
            # Запрашиваем тип графа при создании пустого графа
            graph = create_new_graph()
    elif initial_choice == '2':
        graph = create_new_graph()
    else:
        print("Некорректный выбор. Создан пустой граф.")
        graph = Graph()

    while True:
        print("\nМеню:")
        print("1. Добавить вершину")
        print("2. Добавить ребро")
        print("3. Удалить вершину")
        print("4. Удалить ребро")
        print("5. Показать граф")
        print("6. Показать рёбра графа")
        print("7. Сохранить в файл")
        print("8. Создать копию графа")
        print("9. Загрузить граф из файла")
        print("10. Задание 1: Вывести заходящие соседние вершины")
        print("11. Задание 2: Вывести степени всех вершин")
        print("12. Задание 3: Удалить висячие вершины")
        print("13. Задание 4: Проверить граф на ацикличность (DFS)")
        print("14. Задание 5: Кратчайшие пути из вершины (BFS)")
        print("15. Задание 6: Построить минимальное остовное дерево (алгоритм Краскала)")
        print("16. Задание 7: Кратчайший путь из u в v (Дейкстра)")
        print("17. Задание 8: Вершины на расстоянии ≤ N (Беллман-Форд)")
        print("18. Задание 9: Кратчайшие пути до вершины (Флойд-Уоршелл)")
        print("19. Задание 10: Максимальный поток (Эдмондс-Карп)")
        print("20. Выйти")

        choice = input("Введите номер действия: ").strip()

        if choice == '1':
            vertex = input("Введите имя вершины: ").strip()
            graph.add_vertex(vertex)

        elif choice == '2':
            u = input("Введите первую вершину: ").strip()
            v = input("Введите вторую вершину: ").strip()
            if graph.weighted:
                while True:
                    weight_input = input("Введите вес ребра: ").strip()
                    try:
                        weight = float(weight_input)
                        break
                    except ValueError:
                        print("Неверный формат веса. Пожалуйста, введите число.")
            else:
                weight = None

            # Проверяем, существует ли уже ребро
            edge_exists = False
            if graph.weighted:
                edge_exists = any(neighbor == v for neighbor, _ in graph.adjacency_list.get(u, []))
            else:
                edge_exists = any(neighbor == v for neighbor, *_ in graph.adjacency_list.get(u, []))

            if edge_exists:
                overwrite_choice = input(
                    f"Ребро {u}-{v} уже существует. Хотите перезаписать его? (да/нет): ").strip().lower()
                if overwrite_choice in ['да', 'д', 'yes', 'y']:
                    success = graph.add_edge(u, v, weight=weight, overwrite=True)
                    if not success:
                        print("Не удалось перезаписать ребро.")
                else:
                    print("Добавление ребра отменено.")
            else:
                success = graph.add_edge(u, v, weight=weight)
                if not success:
                    print("Не удалось добавить ребро.")

        elif choice == '3':
            vertex = input("Введите имя вершины для удаления: ").strip()
            graph.remove_vertex(vertex)

        elif choice == '4':
            u = input("Введите первую вершину: ").strip()
            v = input("Введите вторую вершину: ").strip()
            graph.remove_edge(u, v)

        elif choice == '5':
            print("\nТекущий граф:")
            graph.display_adjacency_list()
            # Отображаем тип графа
            graph_type = []
            graph_type.append("Ориентированный" if graph.directed else "Неориентированный")
            graph_type.append("Взвешенный" if graph.weighted else "Невзвешенный")
            print(f"Тип графа: {', '.join(graph_type)}")

        elif choice == '6':
            print("\nСписок рёбер:")
            for edge in graph.edges():
                if graph.weighted:
                    print(f"{edge[0]} - {edge[1]} (Вес: {edge[2]})")
                else:
                    print(f"{edge[0]} - {edge[1]}")

        elif choice == '7':
            filename = input("Введите имя файла для сохранения: ").strip()
            graph.save_to_file(filename)
            print(f"Граф сохранён в файл '{filename}'.")

        elif choice == '8':
            # Создаём новый граф с теми же параметрами
            copy_graph = Graph(directed=graph.directed, weighted=graph.weighted)

            # сначала добавляем все вершины
            for vertex in graph.adjacency_list:
                copy_graph.add_vertex(vertex)

            # потом добавляем все рёбра
            for vertex in graph.adjacency_list:
                for edge in graph.adjacency_list[vertex]:
                    if graph.weighted:
                        # Для взвешенного графа
                        neighbor, weight = edge[0], edge[1]
                        copy_graph.add_edge(vertex, neighbor, weight=weight)
                    else:
                        # Для невзвешенного графа
                        neighbor = edge[0]
                        copy_graph.add_edge(vertex, neighbor)

            print("\nСоздана копия графа. Вот её содержимое:")
            copy_graph.display_adjacency_list()
            graph_type = []
            graph_type.append("Ориентированный" if copy_graph.directed else "Неориентированный")
            graph_type.append("Взвешенный" if copy_graph.weighted else "Невзвешенный")
            print(f"Тип графа копии: {', '.join(graph_type)}")

        elif choice == '9':
            filename = input("Введите имя файла для загрузки графа: ").strip()
            try:
                graph.load_from_file(filename)
            except FileNotFoundError:
                print(f"Файл '{filename}' не найден.")
            except ValueError as ve:
                print(f"Ошибка при загрузке графа: {ve}")

        elif choice == '10':
            if not graph.directed:
                print("Внимание: Граф неориентированный. Функция выведет всех соседей указанной вершины.")
            target_vertex = input("Введите вершину для поиска заходящих соседей: ").strip()
            graph.incoming_neighbors(target_vertex)

        elif choice == '11':
            graph.print_vertex_degrees()

        elif choice == '12':
            # Показываем текущий граф
            print("Исходный граф:")
            graph.display_adjacency_list()

            # Создаём граф без висячих вершин
            new_graph = graph.remove_pendant_vertices()

            print("\nРезультат после удаления висячих вершин:")
            new_graph.display_adjacency_list()

            # Спрашиваем, хочет ли пользователь заменить исходный граф
            replace = input("\nЗаменить исходный граф полученным? (да/нет): ").strip().lower()
            if replace in ['да', 'д', 'yes', 'y']:
                graph = new_graph
                print("Исходный граф заменён.")
            else:
                print("Исходный граф сохранён. Результат можно посмотреть в копии.")

        elif choice == '13':
            # Задание 4: Проверка на ацикличность (DFS)
            graph.is_acyclic()

        elif choice == '14':
            # Задание 5: Кратчайшие пути (BFS)
            start_vertex = input("Введите начальную вершину: ").strip()
            graph.shortest_paths_bfs(start_vertex)


        elif choice == '15':
            # Задание 6: Алгоритм Краскала
            if not graph.weighted:
                print("Ошибка: Алгоритм Краскала работает только для взвешенных графов!")
                print("Пожалуйста, создайте взвешенный граф.")
            elif graph.directed:
                print("Ошибка: Алгоритм Краскала работает только для неориентированных графов!")
                print("Пожалуйста, создайте неориентированный граф.")
            else:
                # Выполняем алгоритм Краскала
                result = graph.kruskal_mst()

                if result is not None:
                    mst_graph, total_weight, mst_edges = result

                    # Показываем сравнение
                    graph.display_mst_comparison(mst_graph, total_weight)

                    # Спрашиваем, сохранить ли результат
                    save_choice = input("\nСохранить минимальное остовное дерево в файл? (да/нет): ").strip().lower()
                    if save_choice in ['да', 'д', 'yes', 'y']:
                        filename = input("Введите имя файла для сохранения: ").strip()
                        mst_graph.save_to_file(filename)
                        print(f"Минимальное остовное дерево сохранено в файл '{filename}'.")

                    # Спрашиваем, заменить ли исходный граф
                    replace_choice = input(
                        "\nЗаменить исходный граф минимальным остовным деревом? (да/нет): ").strip().lower()
                    if replace_choice in ['да', 'д', 'yes', 'y']:
                        graph = mst_graph
                        print("Исходный граф заменён минимальным остовным деревом.")



        elif choice == '16':
            # Задание 7: Алгоритм Дейкстры
            if not graph.weighted:
                print("Внимание: Граф невзвешенный. Вес каждого ребра будет считаться равным 1.")

            u = input("Введите начальную вершину: ").strip()
            v = input("Введите конечную вершину: ").strip()
            graph.dijkstra_shortest_path(u, v)

        elif choice == '17':
            # Задание 8: Алгоритм Беллмана-Форда
            if not graph.weighted:
                print("Внимание: Граф невзвешенный. Вес каждого ребра будет считаться равным 1.")

            start = input("Введите начальную вершину: ").strip()
            try:
                max_dist = float(input("Введите максимальное расстояние N: ").strip())
            except ValueError:
                print("Ошибка: Некорректное значение N")
                continue

            graph.bellman_ford_vertices_within_distance(start, max_dist)

        elif choice == '18':
            # Задание 9: Алгоритм Флойда-Уоршелла
            if not graph.weighted:
                print("Внимание: Граф невзвешенный. Вес каждого ребра будет считаться равным 1.")

            target = input("Введите целевую вершину: ").strip()
            graph.floyd_warshall_paths_to_vertex(target)

        elif choice == '19':
            # Задание 10: Алгоритм Эдмондса-Карпа (максимальный поток)
            if not graph.directed:
                print("Ошибка: Алгоритм поиска максимального потока работает только для ориентированных графов!")
                print("Пожалуйста, создайте ориентированный граф.")
            elif not graph.weighted:
                print("Ошибка: Для поиска максимального потока граф должен быть взвешенным!")
                print("Вес ребра интерпретируется как пропускная способность.")
            else:
                source = input("Введите вершину-исток: ").strip()
                sink = input("Введите вершину-сток: ").strip()

                result = graph.max_flow_edmonds_karp(source, sink)

                if result:

                    # Спрашиваем, сохранить ли результат
                    save_choice = input("\nСохранить результат в файл? (да/нет): ").strip().lower()
                    if save_choice in ['да', 'д', 'yes', 'y']:
                        filename = input("Введите имя файла для сохранения: ").strip()
                        with open(filename, 'w') as f:
                            f.write(f"Максимальный поток из {source} в {sink}: {result['max_flow']}\n")
                            f.write("\nРаспределение потока:\n")
                            for (u, v), flow_val in sorted(result['flow_distribution'].items()):
                                if flow_val > 0:
                                    f.write(f"{u} -> {v}: {flow_val}\n")
                        print(f"Результат сохранён в файл '{filename}'")
        elif choice == '20':
            break


        else:
            print("Некорректный ввод. Пожалуйста, введите номер от 1 до 15.")

    print("Завершение работы.")


def create_new_graph():
    # Запрашиваем тип графа у пользователя
    while True:
        directed_input = input("Граф ориентированный? (да/нет): ").strip().lower()
        if directed_input in ['да', 'д', 'yes', 'y']:
            directed = True
            break
        elif directed_input in ['нет', 'н', 'no', 'n']:
            directed = False
            break
        else:
            print("Пожалуйста, введите 'да' или 'нет'.")

    while True:
        weighted_input = input("Граф взвешенный? (да/нет): ").strip().lower()
        if weighted_input in ['да', 'д', 'yes', 'y']:
            weighted = True
            break
        elif weighted_input in ['нет', 'н', 'no', 'n']:
            weighted = False
            break
        else:
            print("Пожалуйста, введите 'да' или 'нет'.")

    graph = Graph(directed=directed, weighted=weighted)
    print("Создан новый граф.")
    graph_type = []
    graph_type.append("Ориентированный" if graph.directed else "Неориентированный")
    graph_type.append("Взвешенный" if graph.weighted else "Невзвешенный")
    print(f"Тип графа: {', '.join(graph_type)}")
    return graph


if __name__ == "__main__":
    console_interface()