import heapq

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(start, goal, grid):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start:0}
    f_score = {start:heuristic(start, goal)}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        x,y = current
        neighbors = [(x+dx,y+dy) for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]]
        for nx, ny in neighbors:
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny]==0:
                tentative_g = g_score[current]+1
                if (nx,ny) not in g_score or tentative_g < g_score[(nx,ny)]:
                    came_from[(nx,ny)] = current
                    g_score[(nx,ny)] = tentative_g
                    f_score[(nx,ny)] = tentative_g + heuristic((nx,ny), goal)
                    heapq.heappush(open_set, (f_score[(nx,ny)], (nx,ny)))
    return []
