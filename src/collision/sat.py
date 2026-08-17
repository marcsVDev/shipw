from pygame import Vector2

class SAT:
    @staticmethod
    def get_normals(vertices) -> list[Vector2]:
        vertex_num = len(vertices)
        normals = []
        for i in range(vertex_num):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % vertex_num]

            edge = v2 - v1

            normal = Vector2(-edge[1], edge[0]).normalize() # perpendicular normalizado
            normals.append(normal)

        return normals

    @staticmethod
    def get_projection(vertices: list[Vector2], normal_axis: Vector2) -> tuple[float, float]:
        projections: list[float] = []
        for vertex in vertices:
            projections.append(vertex.dot(normal_axis))

        return (min(projections), max(projections))

# SAT (Teorema do Eixo Separador)
# 1. Obter vertices da figura convexa
# 2. Calcular as normais das arestas para uso nos eixos de busca
# 3. Realizar as projeções dos vertices em relação aos eixos de busca
# 4. Verificar se as projecoes se intersectam