import threading
from drones.drone import Drone
from drones.navigation import a_star
from drones.obstacle import detect_obstacle, avoid_obstacle

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
