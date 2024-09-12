# Run Functions
%run "./BasicFunctions_prod"

import time

# Environment set up



incentive_on = 1 # 1/0
is_dispatch  = 1 # 1/0

seed = 88
itteration_pso = 10
itteration_simulation = 100
# ---------Run simulation model--------------

## Simulation
# create instance
instance = CarSharingSystem(incentive_on, is_dispatch)

final_price_list = []
Order_count_list = []
Travel_time_list = []
relocation_frequency_list = []

start_time = time.time()
for _ in range(itteration_simulation):
    vehicle_final_level_list, travel_time, final_price, Order_count, relocation_frequency = instance.run_simulation()
    Travel_time_list.append(travel_time)
    final_price_list.append(final_price)
    Order_count_list.append(Order_count)
    relocation_frequency_list.append(relocation_frequency)
print(f'Avg. final price with relocation cost is: {sum(final_price_list)/len(final_price_list):.2f}')
print(f'Avg. travel time is: {sum(Travel_time_list)/len(Travel_time_list):.2f}')
print(f'Avg. Order Count is: {sum(Order_count_list)/len(Order_count_list):.2f}')
print(f'Avg. Relocation Frequency is: {sum(relocation_frequency_list)/len(relocation_frequency_list):.2f}')

end_time = time.time()
elapsed_time = end_time - start_time
print(f'\nElapsed_time: {elapsed_time}')

## PSO + Simulation
#PSO
#Create instance
instance = CarSharingSystem(incentive_on, is_dispatch, period, town, weekday)

start_time = time.time()
final_price_opt, vehicle_level_opt = PSO(itteration_pso, instance, seed)
# the optimal vehicle allocation is set as vehicle_average_level in the case without optimaization
# update the optimal vehicle allocation as vehicle_level_opt got from PSO process
instance.set_vehicle_average_level(vehicle_level_opt) 
end_time = time.time()
elapsed_time = end_time - start_time
print(f'\nElapsed_time: {elapsed_time}')

#Simulation
final_price_list = []
Order_count_list = []
Travel_time_list = []
relocation_frequency_list = []

start_time = time.time()
for _ in range(itteration_simulation):
    vehicle_final_level_list, travel_time, final_price, Order_count, relocation_frequency = instance.run_simulation()
    Travel_time_list.append(travel_time)
    final_price_list.append(final_price)
    Order_count_list.append(Order_count)
    relocation_frequency_list.append(relocation_frequency)
print(f'Avg. final price with relocation cost is: {sum(final_price_list)/len(final_price_list):.2f}')
print(f'Avg. travel time is: {sum(Travel_time_list)/len(Travel_time_list):.2f}')
print(f'Avg. Order Count is: {sum(Order_count_list)/len(Order_count_list):.2f}')
print(f'Avg. Relocation Frequency is: {sum(relocation_frequency_list)/len(relocation_frequency_list):.2f}')

end_time = time.time()
elapsed_time = end_time - start_time
print(f'\nElapsed_time: {elapsed_time}')
