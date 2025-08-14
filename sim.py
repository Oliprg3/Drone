import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import heapq

class Drone:
    def __init__(self, id, start_pos=(0,0), color='blue'):
        self.id = id
        self.position = start_pos
        self.status = "idle"
        self.battery = 100
        self.color = color
        self.path = []

    def move_step(self):
        if self.path:
            next_pos = self.path.pop(0)
            self.position = next_pos
            self.battery -= random.uniform(0.5, 2)
            if self.battery < 20:
                self.status = "returning"
            else:
                self.status = "flying"

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

def detect_obstacle():
    return random.choice([False, False, True, False])

def avoid_obstacle(drone):
    if drone.path:
        drone.path = drone.path[::-1]

class DeliverySystem:
    def __init__(self, grid, drones):
        self.grid = grid
        self.drones = drones
        self.orders = []

    def add_order(self, order_id, restaurant, customer):
        self.orders.append({
            "order_id": order_id,
            "restaurant": restaurant,
            "customer": customer,
            "status": "pending"
        })

    def assign_paths(self):
        for order in self.orders:
            if order["status"] == "pending":
                drone = self.get_available_drone()
                if not drone:
                    continue
                path_to_restaurant = a_star(drone.position, order["restaurant"], self.grid)
                path_to_customer = a_star(order["restaurant"], order["customer"], self.grid)
                drone.path = path_to_restaurant + path_to_customer
                order["status"] = "assigned"

    def get_available_drone(self):
        for drone in self.drones:
            if drone.status in ["idle","flying"]:
                return drone
        return None

def simulate(system, steps=100):
    fig, ax = plt.subplots()
    grid = system.grid
    drones = system.drones

    def update(frame):
        ax.clear()
        ax.set_xlim(-1,len(grid))
        ax.set_ylim(-1,len(grid[0]))
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    ax.plot(i,j,'ks')
        for drone in drones:
            if drone.path:
                if detect_obstacle():
                    avoid_obstacle(drone)
                drone.move_step()
            ax.plot(drone.position[0], drone.position[1], 'o', color=drone.color)
        return ax

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=500, repeat=False)
    plt.show()

if __name__ == "__main__":
    grid_size = 20
    grid = [[0]*grid_size for _ in range(grid_size)]
    for _ in range(40):
        x = random.randint(0,grid_size-1)
        y = random.randint(0,grid_size-1)
        grid[x][y] = 1
    drones = [Drone(0,(0,0),'blue'), Drone(1,(0,1),'red')]
    system = DeliverySystem(grid, drones)
    system.add_order(1, (2,2), (15,15))
    system.add_order(2, (1,1), (18,18))
    system.assign_paths()
    simulate(system, steps=50)
