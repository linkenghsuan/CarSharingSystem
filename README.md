# CarSharingSystem

## Introduction
In a free floating car sharing system, the vehicle disposition may become imbalance during opertaion time.

This could leads to shortages in some areas and surpluses in others. This not only increases the cost of dispatching personnel but also reduces overall operational efficiency. 
To address this issue, we have developed an innovative vehicle dispatch algorithm that leverages user incentives.

### Method
Our algorithm encourages users to return vehicles to locations identified by the system as needing more vehicles by offering them rate discounts. This user incentive mechanism helps to balance vehicle disposition.

The method is composed of two phase.
In the first phase, we develop a discrete event simulation model using historical data. This model captures the dynamics and randomness of the shared vehicle system and can flexibly incorporate various incentive scenarios.
In the second phase, we utilize the simulation model from Phase One to apply an algorithm aimed at maximizing revenue (objective value). This algorithm determines the optimal vehicle allocation (decision variables).

### Benefits
By following this two-phase development approach, we aim to create a robust and efficient vehicle dispatch algorithm that not only enhances operational efficiency but also increases revenue through strategic user incentives.

- Reduced Dispatch Costs: By incentivizing users to assist in vehicle redistribution, the need for dispatching is decreased and the personnel can get more time to clean up and prepare a vehicle for the next use.
- Increased Dispatch Frequency: With increased frequency of dispatches, more vehicles can be used by potential needs.
- Cross-Region Dispatching: The algorithm supports cross-region dispatching, meeting potential rental demands in various areas.
- Increased Revenue: Ultimately, these improvements contribute to higher revenue through better service availability and reduced operational costs.


## Parameters & Table Schemas
#### -- station names
district is seprated to small regions which can be seen as stations, set station name as integer (district index)
##### data type
list -> int
##### sample data
station_names = [1,  2,  3,  4,  5,  6,  7,  8,  9, 10] 

#### -- rent_prob_df
the weight of renting a vehicle from a station, which is used for sampling 
##### data type
dataframe
##### schema
| col_name  |data_type|
| :------------: | :------------: |
|district_index|int|
|rent_weight|double|

##### sample data
| district_index  |rent_weight|
| :------------: | :------------: |
|1|10.0|
|2|10.0|
|3|20.0|
|4|50.0|
|5|10.0|

#### -- return_prob_df
the weight of returning a vehicle from a station, which is used for sampling 
##### data type
dataframe
##### schema
| col_name  |data_type|
| :------------: | :------------: |
|district_index|int|
|return_weight|double|

##### sample data
| district_index  |return_weight|
| :------------: | :------------: |
|1|50.0|
|2|50.0|
|3|20.0|
|4|10.0|
|5|10.0|


#### -- od_metrix_df
origin-destination metrix, which is used for sampling 
##### data type
dataframe
##### schema
| col_name  |data_type|
| :------------: | :------------: |
|S_district_index|int|
|E_district_index|int|
|avg_OD_count|double|

##### sample data
| S_district_index  |E_district_index|avg_OD_count|
| :------------: | :------------: |:------------: |
|1|1|1.1|
|1|2|3.0|
|1|3|1.8|
|1|4|2.5|
|1|5|1.5|

#### -- vehicles_per_station
min and max of a station's initial vehicle number
##### data type
list -> int
##### sample data
vehicles_per_station = [0, 3]

#### -- vehicle_average_level
the average vehicle number of a station
##### data type
list -> float
##### sample data
vehicle_average_level = [1.0,  2.1,  2.3,  4.7,  0.2] -- order by station names

#### -- avg_opening_app_time
the average time interval among app opening time of customers
##### data type
float
##### sample data
avg_opening_app_time = 15.63

#### -- avg_using_app_time
the average time interval between opening the app and booking a vehicle
##### data type
float
##### sample data
avg_using_app_time = 5.28

#### -- avg_arriving_time
the average time interval between booking a vehicle and arriving to the place where the vehicle is parked
##### data type
float
##### sample data
avg_arriving_time = 9.79

#### -- travel_time_param
the total use time. travel time follow log-normal distribution, standard deviation, standardized standard deviation, and standardized mean are needed
##### data type
tuple -> double
##### sample data
travel_time_param = (419.18, 1.33, -1.1) -> (standard deviation, standardized standard deviation, standardized mean)

#### -- insurance_use_rate
the contract ratio of using insurance. This could be a special case in the created model
##### data type
float
##### sample data
insurance_use_rate = 0.26

#### -- stay_time_ratio
Stay time ratio of total use time. Vehicle using time is composed of stay time(engine off) and moving time(engine off). This could be a special case in the created model
##### data type
float
##### sample data
stay_time_ratio = 0.37

#### -- operation_time
the time period(minutes) for simulation
##### data type
int
##### sample data
operation_time = 540

#### -- incentive_index_adjust
the start index of district_index, default set to 0. This could be a special case in the created model
##### data type
int
##### sample data
incentive_index_adjust = 0

## discrete event simulation
### Main functions
```
class CarSharingSystem():
	def sampling_travel_time()
	def _get_incentive_accepting_rate()
	def _set_dispatch_scenario():
		 _get_incentive_accepting_rate
	def drop_off():
		_set_dispatch_scenario
		sampling_travel_time
	def rent_process():
		 drop_off
	def generate_arrivals():
		 rent_process
	def run_simulation():
		 generate_arrivals
```
### Pseudo Code
```
run_simulation() :
	environment set up
	 generate arrivals
	 start rent process:
		decide to dispatch or not
		decide to give incentive or not
		a customer to rent a vehicle or not
		if  a customer  rent a vehicle:
			decide origin and pick up a vehicle
			 generate travel time
			if  give incentive:
				get incentive accepting  rate
			decide destination and drop off a vehicle
		else:
			leave the system
```
## optimization model
### Parameters
```
particle = 10
𝑐_1, 𝑐_2 = 1 
𝑅_1, 𝑅_2 = random number between 0 and 1
𝑤 = 1
```
### Pseudo Code
```
for t in iteration:
	for p in particle:
		generate x
		calculate Objective value by discrete event simulation model
		update local optimal
	update global optimal
	#update particle
	𝑃=𝑤∙𝑥_𝑝 + 𝑐_1∙𝑅_1∙𝑥_𝐿𝑜𝑐𝑎𝑙𝐵𝑒𝑠𝑡 + 𝑐_2∙𝑅_2∙𝑥_𝐺𝑙𝑜𝑏𝑎𝑙𝐵𝑒𝑠𝑡
```
