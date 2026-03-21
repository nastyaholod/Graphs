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
        """
        Удаляет все висячие вершины (вершины со степенью 1) из графа.
        Возвращает новый граф без висячих вершин.
        """
        print("\n" + "=" * 50)
        print("ЗАДАНИЕ 3: Удаление висячих вершин")
        print("=" * 50)

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
        """
        Вспомогательный метод для поиска висячих вершин в текущем графе.
        Возвращает множество висячих вершин.
        """
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
        """
        Вспомогательный метод для создания копии графа.
        """
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
        print("13. Выйти")

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
            # Задание 3: Удаление висячих вершин
            print("\n" + "=" * 50)
            print("ЗАДАНИЕ 3: Удаление висячих вершин")
            print("=" * 50)

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
            break

        else:
            print("Некорректный ввод. Пожалуйста, введите номер от 1 до 13.")

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