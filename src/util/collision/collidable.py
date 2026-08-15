from pygame import Rect, Vector2

from util.collision.sat import SAT


class Collidable:
    def __init__(self):
        self._collider_vertices: list[Vector2] = []
        super().__init__()

    def update_vertices_from_rect(self, rect: Rect):
        self._collider_vertices = [
            Vector2(rect.topleft), 
            Vector2(rect.topright), 
            Vector2(rect.bottomleft), 
            Vector2(rect.bottomright)]

    def collide_with(self, collider: Collidable) -> bool:
        axes = SAT.get_normals(self._collider_vertices) + SAT.get_normals(collider._collider_vertices)
        for axis in axes:
            p1 = SAT.get_projection(self._collider_vertices, axis)
            p2 = SAT.get_projection(collider._collider_vertices, axis)            

            if p1[1] < p2[0] or p2[1] < p1[0]: # max_1 < min_2 or max_2 < min_1
                return False
            
        return True

    

