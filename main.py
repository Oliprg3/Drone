import time
import random
import threading
import heapq

class Drone:
    def __init__(self, id, start_pos=(0,0)):
        self.id = id
        self.position = start_pos
        self.altitude = 0
        self.speed = 10
        self.battery = 100
        self.status = "idle"
        self.lock = threading.Lock()

    def takeoff(self, altitude=10):
        with self.lock:
            self.altitude = altitude
            self.status = "flying"
            print(f"[Drone {self.id}] Taking off to {altitude}m")

    def land(self):
        with self.lock:
            self.altitude = 0
            self.status = "idle"
            print(f"[Drone {self.id}] Landing at {self.position}")

    def move_to(self, coord):
        with self.lock:
            print(f"[Drone {self.id}] Moving from {self.position} to {coord}")
            self.position = coord
            self.battery -= random.uniform(0.5, 2)
            time.sleep(0.5)

    def emergency_return(self, home=(0,0)):
        print(f"[Drone {self.id}] Battery low! Returning home")
        self.move_to(home)
        self.land()

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
    print(f"[Drone {drone.id}] Obstacle detected! Rerouting...")
    time.sleep(0.5)

class DeliverySystem:
    def __init__(self, grid):
        self.drones = [Drone(i) for i in range(3)]
        self.orders = []
        self.grid = grid
        self.lock = threading.Lock()

    def add_order(self, order_id, restaurant, customer):
        self.orders.append({
            "order_id": order_id,
            "restaurant": restaurant,
            "customer": customer,
            "status": "pending"
        })

    def assign_and_deliver(self):
        threads = []
        for order in self.orders:
            if order["status"]=="pending":
                t = threading.Thread(target=self.handle_order, args=(order,))
                t.start()
                threads.append(t)
        for t in threads:
            t.join()

    def handle_order(self, order):
        drone = self.get_available_drone()
        if not drone:
            print("No drones available for order", order["order_id"])
            return
        drone.takeoff()
        path = a_star(drone.position, order["restaurant"], self.grid)
        for point in path:
            if detect_obstacle():
                avoid_obstacle(drone)
            drone.move_to(point)
            if drone.battery < 20:
                drone.emergency_return()
                return
        print(f"Order {order['order_id']} picked up")
        path = a_star(drone.position, order["customer"], self.grid)
        for point in path:
            if detect_obstacle():
                avoid_obstacle(drone)
            drone.move_to(point)
            if drone.battery < 20:
                drone.emergency_return()
                return
        drone.land()
        order["status"] = "delivered"
        print(f"Order {order['order_id']} delivered by Drone {drone.id}")

    def get_available_drone(self):
        for drone in self.drones:
            if drone.status == "idle" and drone.battery > 20:
                return drone
        return None

if __name__ == "__main__":
    grid = [[0]*20 for _ in range(20)]
    for i in range(20):
        grid[random.randint(0,19)][random.randint(0,19)] = 1
    system = DeliverySystem(grid)
    system.add_order(1, (0,0), (15,15))
    system.add_order(2, (2,2), (18,18))
    system.add_order(3, (1,1), (10,10))
    system.assign_and_deliver()
