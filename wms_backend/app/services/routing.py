"""
Thuật toán tối ưu đường đi khi pick hàng.

Hai chiến lược:
- s_shape_route: cho kho bố cục dãy kệ đơn giản, đi theo hình rắn qua các dãy.
- tsp_route: cho kho phức tạp hơn, dùng nearest neighbor để dựng lộ trình ban
  đầu rồi cải tiến bằng 2-opt.

optimize_picking_route() là điểm vào chung, chọn chiến lược theo layout_complexity.
"""
from dataclasses import dataclass
from typing import Dict, List

from app.models.warehouse import Bin


@dataclass
class PickStop:
    order_item_id: str
    bin: Bin
    quantity: int


def s_shape_route(stops: List[PickStop]) -> List[PickStop]:
    by_aisle: Dict[int, List[PickStop]] = {}
    for s in stops:
        by_aisle.setdefault(s.bin.aisle_index, []).append(s)

    route: List[PickStop] = []
    for i, aisle in enumerate(sorted(by_aisle.keys())):
        items = sorted(by_aisle[aisle], key=lambda s: s.bin.position_in_aisle)
        if i % 2 == 1:  # dãy chẵn (theo thứ tự) đi ngược chiều - tạo hình rắn
            items = list(reversed(items))
        route.extend(items)
    return route


def manhattan_distance(a: Bin, b: Bin) -> float:
    """Khoảng cách quy đổi giữa 2 ô kệ. Với kho phức tạp hơn (có tường,
    khu vực cấm), thay hàm này bằng tra cứu shortest-path trên đồ thị kho
    (Dijkstra, tính sẵn và cache lại)."""
    return abs(a.aisle_index - b.aisle_index) * 10 + abs(a.position_in_aisle - b.position_in_aisle)


def build_distance_matrix(stops: List[PickStop]) -> List[List[float]]:
    n = len(stops)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = manhattan_distance(stops[i].bin, stops[j].bin)
    return matrix


def nearest_neighbor_route(matrix: List[List[float]]) -> List[int]:
    n = len(matrix)
    if n == 0:
        return []
    visited = [False] * n
    route = [0]
    visited[0] = True
    for _ in range(n - 1):
        last = route[-1]
        nxt = min((j for j in range(n) if not visited[j]), key=lambda j: matrix[last][j])
        route.append(nxt)
        visited[nxt] = True
    return route


def two_opt_improve(route: List[int], matrix: List[List[float]]) -> List[int]:
    """Cải tiến tour bằng cách đảo ngược các đoạn cắt nhau nếu giúp giảm
    tổng quãng đường - lặp tới khi không cải thiện được nữa."""
    best = route[:]
    n = len(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if j - i == 1:
                    continue
                a, b_ = best[i - 1], best[i]
                c, d = best[j - 1], best[j % n]
                old_cost = matrix[a][b_] + matrix[c][d]
                new_cost = matrix[a][c] + matrix[b_][d]
                if new_cost < old_cost:
                    best[i:j] = reversed(best[i:j])
                    improved = True
    return best


def tsp_route(stops: List[PickStop]) -> List[PickStop]:
    if len(stops) <= 1:
        return stops
    matrix = build_distance_matrix(stops)
    order = nearest_neighbor_route(matrix)
    order = two_opt_improve(order, matrix)
    return [stops[i] for i in order]


def optimize_picking_route(stops: List[PickStop], layout_complexity: str = "simple") -> List[PickStop]:
    if not stops:
        return []
    if layout_complexity == "simple":
        return s_shape_route(stops)
    return tsp_route(stops)


def total_route_distance(stops: List[PickStop]) -> float:
    if len(stops) < 2:
        return 0.0
    return sum(manhattan_distance(stops[i].bin, stops[i + 1].bin) for i in range(len(stops) - 1))
