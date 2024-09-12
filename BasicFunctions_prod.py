# congif settings

# pip install simpy
import simpy
import random
import numpy as np
import pandas as pd
import seaborn as sns
import math



def get_parameters(period, town, weekday):
    # parameters used in discrete event simulation model settings
    station_names = None # to be modified

    rent_prob_df = None # to be modified
    
    return_prob_df =  None # to be modified

    od_metrix_df =  None # to be modified

    travel_time_param =  None # to be modified

    incentive_index_adjust =  None # to be modified

    vehicles_per_station =  None # to be modified

    vehicle_average_level =  None # to be modified

    avg_arriving_time =  None # to be modified

    avg_opening_app_time =  None # to be modified
                
    avg_using_app_time =  None # to be modified

    insurance_use_rate =  None # to be modified

    stay_time_ratio =  None # to be modified
    
    operation_time = None # to be modified

    return    station_names, rent_prob_df, return_prob_df \
            , od_metrix_df, travel_time_param, incentive_index_adjust\
            , vehicles_per_station, vehicle_average_level , avg_arriving_time\
            , avg_opening_app_time, avg_using_app_time, insurance_use_rate\
            , stay_time_ratio, operation_time



class CarSharingSystem():
    def __init__(self, incentive_on, is_dispatch):
        # input values
        self.is_dispatch = is_dispatch
        self.period = period
        
        # get parameters
        station_names, rent_prob_df, return_prob_df \
        , od_metrix_df, travel_time_param, incentive_index_adjust\
        , vehicles_per_station, vehicle_average_level , avg_arriving_time\
        , avg_opening_app_time, avg_using_app_time, insurance_use_rate\
        , stay_time_ratio, operation_time                                   = get_parameters()

        # parameters for the simulation
        self.station_names = station_names
        self.rent_prob_df = rent_prob_df
        self.return_prob_df = return_prob_df
        self.od_metrix_df = od_metrix_df
        self.travel_time_param = travel_time_param
        self.incentive_index_adjust = incentive_index_adjust
        self.vehicles_per_station = vehicles_per_station
        self.vehicle_average_level = vehicle_average_level
        self.avg_arriving_time = avg_arriving_time
        self.avg_opening_app_time = avg_opening_app_time
        self.avg_using_app_time = avg_using_app_time
        self.insurance_use_rate = insurance_use_rate
        self.stay_time_ratio = stay_time_ratio
        self.operation_time = operation_time
        

        self.max_queue_waiting_time = 20
        self.final_price = 0
        self.relocation_cost = 0
        self.relocation_frequency = 0
        self.insurance_rate = 60
        self.base_fee = 125/2 # base fee: 125 / hour
        self.rent_unit_price = 3.1 # millage fee
        self.capacity = max(vehicles_per_station) #container capacity
        self.station_number = len(station_names)

        self.discount_minutes = 5
        self.dispatch_cost = 160
        self.max_incentive_level = 4
        self.max_accept_probability = 0.5

        # random seed setting
        seed = 88
        random.seed(seed)
        np.random.seed(seed)
        self.rng = np.random.default_rng(seed=seed)


        # initial
        self.env = simpy.Environment()
        self.station_map = {name: simpy.Container(self.env, init=random.randint(*vehicles_per_station), capacity=max(vehicles_per_station))
                            for name in station_names 
                           }

        # records
        self.total_travel_time_list = []
        self.mile_earning_list = []
        self.insurance_list = []
        self.base_fee_hour_list = []
        self.vehicle_final_level_list = []
        self.unserved_list = []
        self.served_list = []
        self.relocation_cost_list = []

    # setting functions
    def set_discount_minutes(self, new_value):
        self.discount_minutes = new_value
    
    def set_max_accept_probability(self, new_value):
        self.max_accept_probability = new_value

    def set_vehicle_average_level(self, new_value):
        self.vehicle_average_level = new_value
    
    def set_seed(self, new_value):
        random.seed(new_value)
        np.random.seed(new_value)
        self.rng = np.random.default_rng(seed=new_value)

    # getting functions
    def get_capacity(self):
        return self.capacity
    
    def get_station_number(self):
        return self.station_number

    # generate traveling time
    def sampling_travel_time(self, sigma, sigma_, mu_):
        # sampling
        z = np.random.normal(mu_, sigma_, 1)

        # calculate traveling time
        z = np.exp(z)*sigma

        return z[0]
     
    # get incentive accepting rate
    def _get_incentive_accepting_rate(self):
        p_accept = 0
        level_current = np.array([self.station_map[s].level for s in self.station_map])
        level_average = np.array(self.vehicle_average_level)
        P_select = (level_current < level_average) #the parking areas that need relocation
        
        # decide incentive level
        incentive_level = 1-level_current/self.vehicle_average_level
        incentive_level[~np.isfinite(incentive_level)] = 0
        incentive_level[(incentive_level>0.75) & (incentive_level<=1)] = 4
        incentive_level[(incentive_level>0.5) & (incentive_level<=0.75)] = 3
        incentive_level[(incentive_level>0.25) & (incentive_level<=0.5)] = 2
        incentive_level[incentive_level<=0.25] = 1
        

        P_select = (level_current < level_average)
        P_available = np.sum(incentive_level*P_select)
        
        if P_available != 0:
            #   the probability that the parking area {name} is selected among the incentivized parking areas
            # * the ratio of incentive_level compared with the maximum incentive level
            # * the maximum probability that a customer could accept the incentive (self defined)
            p_accept = P_select \
                            * incentive_level/self.max_incentive_level \
                            * self.max_accept_probability

        return p_accept, P_select, incentive_level
    
    # if it is a dispatch scenario, set relocation scenario
    def _set_dispatch_scenario(self, name, return_probs):
        # accept incentive or not
        p_accept, P_select, incentive_level = self._get_incentive_accepting_rate()

        # choose a station that is imbalance
        try: #if total weights = 0, or all P_select are 0, then might occur error
            name_new = random.choices(self.station_names,weights = return_probs*P_select)[0]
        except:
            name_new = name
        

        # if incentive_on = 0, then the relocating cost handled by customner is transfered to a dispatcher
        # do reposition or not
        do_relocation = random.choices([1,0],weights=[p_accept[name-self.incentive_index_adjust-1], 1-p_accept[name-self.incentive_index_adjust-1]])[0]
        if do_relocation == 1: # if the customer chose a parking area needed relocation
            name = name_new
            self.relocation_cost_list.append(incentive_level[name-self.incentive_index_adjust-1])

        else: # if the customer decline incentive
            self.relocation_cost_list.append(0)




    # drop off
    def drop_off(self, rent_start_time, return_probs):
        # initial
        name = name_orig = name_new = 1
        ## use vehicle

        ## drop off a vehicle
        # choose a station to drop off
        name = random.choices(self.station_names,weights = return_probs)[0]

        if self.is_dispatch == 1:
            self._set_dispatch_scenario(name, return_probs)

        
        # generate travel time (with stay time)
        travel_time = self.sampling_travel_time(self.travel_time_param[0], self.travel_time_param[1], self.travel_time_param[2])
        # record total travel time
        self.total_travel_time_list.append(travel_time)
        # record total travel time without stay time
        self.mile_earning_list.append(travel_time-travel_time*self.stay_time_ratio)
        

        # insurance
        use_insurance_ornot = random.choices([1,0],weights=[self.insurance_use_rate, 1-self.insurance_use_rate])[0]
        self.insurance_list.append(use_insurance_ornot*math.ceil(travel_time/60)) # minute to hour
        self.base_fee_hour_list.append(math.ceil((travel_time)/30)) #125/hour, 63/ half hour

        # yield travel time (with stay time)
        yield self.env.timeout(travel_time)

        ## Drop off a vehicle (return the resource)
        station = self.station_map[name]
        yield station.put(1)

    # rent process
    def rent_process(self, id):
        ## Customer use the app and search for a station to book a vehicle
        # yield app using time
        yield self.env.timeout(self.rng.exponential(scale=self.avg_using_app_time, size=1)[0])  
        waiting_start_time = self.env.now
        
        ## select a parking area for renting
        name = random.choices(self.station_names,weights=self.rent_prob_df['rent_weight'].values)
        name = name[0]
        station = self.station_map[name]

        ## Customer started to book a Vehicle at parking area {name}
        #  yield arriving time to the parking area which for picking up a vehicle
        yield self.env.timeout(self.rng.exponential(scale=self.avg_arriving_time, size=1)[0])
        
        ## Customer pick up a vehicle
        yield station.get(1)
        # if the customer is waiting for too long, give up using the app
        # if the time waiting in a queue is larger than max_queue_waiting_time, and there's no available vehicle --> give up using the app
        if (self.env.now - waiting_start_time) > self.max_queue_waiting_time and station.level == 0:
            yield station.put(1) #Drop off without timeout --> act as the customer didn't rent a vehicle
            self.unserved_list.append(id)

        # if the time waiting in a queue is smaller than or equal to max_queue_waiting_time, then rent a vehicle
        else:
            # Customer rented a vehicle at parking area {name}
            rent_start_time = self.env.now
            self.served_list.append(id) # add into serverd list
            
            ## Customer drop off a vehicle
            # return prob decided by od matrix, if lending parking area {name} is not in od, then use elk return weight
            # if there're renting records in history OD-matrix
            if name in self.od_metrix_df.loc[self.od_metrix_df['S_district_index']==name]['S_district_index']:
                od_metrix_df_temp = self.od_metrix_df.loc[self.od_metrix_df['S_district_index']==name]
                return_probs = self.rent_prob_df[['district_index']].merge(od_metrix_df_temp[['E_district_index','avg_OD_count']]
                                                                           , how = 'left'
                                                                           , left_on='district_index'
                                                                           ,right_on='E_district_index')
                return_probs.loc[return_probs['avg_OD_count'].isnull(), 'avg_OD_count'] = 0
                return_probs = return_probs['avg_OD_count']
            # use the weight of potential return weight 
            else:
                return_probs = self.return_prob_df['return_weight'].values

            self.env.process(self.drop_off(rent_start_time, return_probs))

    # arrivals
    def generate_arrivals(self):
        ## Generates arrivales to the car sharing system
        cnt = 0
        while True:
            ## create agents
            # yield the time interval when a customer get into the rental system
            yield self.env.timeout(self.rng.exponential(scale=self.avg_opening_app_time, size=1)[0])
            # start a rental process
            self.env.process(self.rent_process(cnt))
            cnt += 1

    # simulation
    def run_simulation(self):
        # record lists
        self.total_travel_time_list = []
        self.mile_earning_list = []
        self.insurance_list = []
        self.base_fee_hour_list = []
        self.vehicle_final_level_list = []
        self.unserved_list = []
        self.served_list = []
        self.relocation_cost_list = []

        # initial environment
        self.env = simpy.Environment()
        self.station_map = {
                            name: simpy.Container(self.env, init=random.randint(*self.vehicles_per_station), capacity=max(self.vehicles_per_station))
                            for name in self.station_names 
                           }
        
        # start generation arrivals
        self.env.process(self.generate_arrivals())

        # start sim
        self.env.run(self.operation_time)
        self.vehicle_final_level_list = [self.station_map[s].level for s in self.station_map]
        
        # calculate results
        self.Base_fee = sum(self.base_fee_hour_list)*self.base_fee
        self.Mileage_fee = sum(self.mile_earning_list)*self.rent_unit_price
        self.Insurance_fee = sum(self.insurance_list)*self.insurance_rate

        
        if self.is_dispatch == 1:
            if self.incentive_on == 1:
                self.relocation_cost = sum(self.relocation_cost_list)*self.discount_minutes*self.rent_unit_price
                # print(self.relocation_cost)
            else:
                self.relocation_cost = len([i for i in self.relocation_cost_list if i > 0])*self.dispatch_cost
            
            self.relocation_frequency = len([i for i in self.relocation_cost_list if i > 0])
            

        self.final_price = sum(self.mile_earning_list)*self.rent_unit_price+sum(self.base_fee_hour_list)*self.base_fee \
                         + sum(self.insurance_list)*self.insurance_rate \
                         - self.relocation_cost
        
        # return vehicle_final_level_list, travel_time, final_price, Order_count, relocation_frequency
        return self.vehicle_final_level_list,sum(self.total_travel_time_list), self.final_price, len(self.mile_earning_list), self.relocation_frequency


def PSO(itteration, simulation_instance, seed):
    capacity = simulation_instance.get_capacity()
    station_number = simulation_instance.get_station_number()
    # random seed settings
    # simulation_instance.set_seed(seed)
    particle = 10 #swarm size
    c = 1
    R1 = random.random() # local
    R2 = random.random() # global
    w = 1 #random.random() # inertia
    S0 = [] #vehicle_level_criteria size = particle
    # S = np.array([[0, 0] for _ in range(particle)]) #vehicle_level_criteria size = particle
    S = [[0 for _ in range(capacity)] for _ in range(particle)]
    S_lb = [[] for _ in range(particle)] #vehicle_level_criteria local_best size = particle
    S_gb = [] #vehicle_level_criteria global_best size = 1
    P = [[0 for _ in range(2)] for _ in range(particle)] #N*3 fitness (local, local_best, global_best)
    P_gb = 0
    Obj = 0 # final_price
    #initial S
    for _ in range(particle):
        S0.append([random.choice(range(1, capacity)) for _ in range(station_number)])
    S0 = np.array(S0)
    for t in range(itteration):
        for j in range(particle):
            # get simulation result as objective value
            simulation_instance.set_vehicle_average_level(S0[j])
            vehicle_final_level_list, travel_time, final_price, Order_count, relocation_frequency = simulation_instance.run_simulation()
            S[j] ,P[j][0] = vehicle_final_level_list, final_price
            #update local optimal
            if P[j][0] > P[j][1]:
                P[j][1] = P[j][0]
                S_lb[j] = S[j]
                # print(f'round {t} -- particle {j} update local optimal: P = {P[j][1]}, S = {S_lb[j]}')
                print(f'round {t} -- particle {j} update local optimal: P = {P[j][1]}')
        
        #update global optimal
        if max([p[1] for p in P]) > P_gb:
            P_gb = max([p[1] for p in P])
            S_gb = S[j]
            # print(f'round {t} -- update global optimal: P = {P_gb}, S = {S_gb}')
            print(f'round {t} -- update global optimal: P = {P_gb}')
        S0 = w*S0 + c*R1*(S_lb - S0) + c*R2*(S_gb - S0) #update particle
        # handle negative value
        S0[S0<0] = 0
        # set as integer
        S0 = np.round(S0)
        # adjust total vehicle numbers
        S_temp = w*S0 + c*R1*(S_lb - S0) + c*R2*(S_gb - S0)
        S_temp[S_temp<0] = 0
        S_diff = S_temp.size - S0.size
        neg_flag = S_diff < 0
        adjust = random.sample(range(S0.size),abs(S_diff))

        if len(adjust) > 0:
            if neg_flag:
                S0 = S_temp[adjust] - 1
            else:
                S0 = S_temp[adjust] + 1

    return P_gb, S_gb


