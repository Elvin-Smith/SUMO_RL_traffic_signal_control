import torch 
import traci
import time

class baseEnv():
    def __init__(self, configs):
        self.configs=configs
        self.indicators = {
            'arrived_vehicles': 0,
            'avg_waiting_time': 0,
            'avg_travel_time': 0
        }
        self.step=0
        self.MAX_STEPS = int(configs['max_steps'])

    def run(self,sumoCmd):
        travel_time = list()
        waiting_time = list()
        part_velocity = list()
        total_velocity = list()

        traci.start(sumoCmd)
        a = time.time()
        while self.step<self.MAX_STEPS:
            traci.simulationStep()
            self.step += 1
            
            for _, interests in enumerate(self.configs['interest_list']):
                
                dup_list = list()
                
                for interest in interests:
                    inflow = interest['inflow']
                    outflow = interest['outflow']
                    
                    if inflow != None and inflow not in dup_list:
                        
                        if traci.edge.getLastStepVehicleNumber(inflow) != 0:
                            
                            waiting_time.append(traci.edge.getWaitingTime(inflow))
                            
                            tmp_travel = traci.edge.getTraveltime(inflow)
                            if tmp_travel <= 500 and tmp_travel != -1: 
                                travel_time.append(tmp_travel)
                            
                        dup_list.append(inflow)

                    if outflow != None and outflow not in dup_list:
                        if traci.edge.getLastStepVehicleNumber(outflow) != 0:
                            
                            tmp_travel = traci.edge.getTraveltime(outflow)
                            if tmp_travel <= 500 and tmp_travel != -1: 
                                travel_time.append(tmp_travel)
                        dup_list.append(interest['outflow'])

            
            arrived_vehicles += traci.simulation.getAllSubscriptionResults()[
                ''][0x79]  # throughput
        b = time.time()
        traci.close()
        avg_part_velocity = torch.tensor(part_velocity, dtype=torch.float).mean()

        avg_velocity = torch.tensor(total_velocity, dtype=torch.float).mean()
        avg_travel_time = torch.tensor(travel_time, dtype=torch.float).mean()
        avg_waiting_time = torch.tensor(waiting_time, dtype=torch.float).mean()
        print('======== arrived number:{} avg waiting time:{},avg velocity:{} avg_part_velocity: {} avg_travel_time: {}'.format(
            arrived_vehicles, avg_waiting_time, avg_velocity, avg_part_velocity, avg_travel_time))
        print("sim_time=", b-a)


    def get_evaluations(self):
        return self.indicators

    def get_state(self):
        
        raise NotImplementedError

    def step(self, action):
        raise NotImplementedError
    
    def collect_state(self):
        raise NotImplementedError

    def get_reward(self):
        
        raise NotImplementedError

    def _toPhase(self, action):  # action을 해석가능한 phase로 변환
        '''
        right: green signal
        straight: green=1, yellow=x, red=0 <- x is for changing
        left: green=1, yellow=x, red=0 <- x is for changing
        '''
        signal_set = list()
        phase_set=tuple()
        phase = str()
        for _, a in enumerate(action):
            signal_set.append(self._getMovement(a))
        for j,signal in enumerate(signal_set):
            # 1개당
            for i in range(4):  # 4차로
                phase = phase + 'g'+self.configs['numLane']*signal[j][2*i] + \
                    signal[j][2*i+1]+'r'  # 마지막 r은 u-turn
            phase_set+=phase
        print(phase_set)
        return phase_set

    def _toState(self, phase_set):  # env의 phase를 해석불가능한 state로 변환
        state_set=tuple()
        for i,phase in enumerate(phase_set):
            state = torch.zeros(8, dtype=torch.int)
            for i in range(4):  # 4차로
                phase = phase[1:]  # 우회전
                state[i] = self._mappingMovement(phase[0])  # 직진신호 추출
                phase = phase[3:]  # 직전
                state[i+1] = self._mappingMovement(phase[0])  # 좌회전신호 추출
                phase = phase[1:]  # 좌회전
                phase = phase[1:]  # 유턴
            state_set+=state
        return state_set

    def _getMovement(self, num):
        if num == 1:
            return 'G'
        elif num == 0:
            return 'r'
        else:
            return 'y'

    def _mappingMovement(self, movement):
        if movement == 'G':
            return 1
        elif movement == 'r':
            return 0
        else:
            return -1  # error
