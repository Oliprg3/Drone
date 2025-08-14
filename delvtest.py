from delivery.delivery_system import DeliverySystem

grid = [[0]*10 for _ in range(10)]
system = DeliverySystem(grid)
system.add_order(1, (0,0), (5,5))
system.assign_and_deliver()
