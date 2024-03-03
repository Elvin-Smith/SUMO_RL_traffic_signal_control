import torch
import traci
import time
import numpy as np
import traci.constants as tc
from Agent.DQN import agent_single_DQN


class baseEnv:
    def __init__(self, configs):
        self.configs = configs
        self.indicators = {
            "arrived_vehicles": 0,
            "avg_waiting_time": 0,
            "avg_travel_time": 0,
        }
        self.yellow_light_duration = list()
        self.state_space = 2
        self.num_node = 25
        self.step = 0
        self.MAX_STEPS = int(configs["max_steps"])
        self.device = "cpu"

    def run(self, sumoCmd):
        # 初始化智能体
        self.agent = agent_single_DQN(self.configs)

        travel_time = list()
        waiting_time = list()
        part_velocity = list()
        total_velocity = list()

        traci.start(sumoCmd)
        # 获取路口的ID列表
        junction_ids = traci.trafficlight.getIDList()

        a = time.time()
        traci.simulation.subscribe([tc.VAR_ARRIVED_VEHICLES_NUMBER])
        while self.step < self.MAX_STEPS:
            traci.simulationStep()
            self.step += 1
            for index, node in enumerate(junction_ids):
                state_current_phase, state_count, state_speed = (
                    self.get_single_node_state(junction_ids[index])
                )
                state_current_phase = (
                    traci.trafficlight.getAllProgramLogics(node)[0]
                    .getPhases()[traci.trafficlight.getPhase(node)]
                    .state
                )
                # 如果是黄灯直接跳过
                if state_current_phase.lower().isalpha() and all(
                    char == "y" for char in state_current_phase.lower()
                ):
                    if self.yellow_light_duration[index] < 2:
                        self.yellow_light_duration[index] + 1
                    else:
                        self.to_next_phase(node)
                else:
                    action = self.agent.get_action(
                        state_current_phase, state_count, state_speed
                    )

            for _, interests in enumerate(self.configs["interest_list"]):

                dup_list = list()

                for interest in interests:
                    inflow = interest["inflow"]
                    outflow = interest["outflow"]

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
                        dup_list.append(interest["outflow"])

            self.indicators[
                "arrived_vehicles"
            ] += traci.simulation.getAllSubscriptionResults()[""][
                0x79
            ]  # throughput
        b = time.time()
        traci.close()
        avg_part_velocity = torch.tensor(part_velocity, dtype=torch.float).mean()

        avg_velocity = torch.tensor(total_velocity, dtype=torch.float).mean()
        self.indicators["avg_travel_time"] = torch.tensor(
            travel_time, dtype=torch.float
        ).mean()
        self.indicators["avg_waiting_time"] = torch.tensor(
            waiting_time, dtype=torch.float
        ).mean()
        print(
            "======== arrived number:{} avg waiting time:{},avg velocity:{} avg_part_velocity: {} avg_travel_time: {}".format(
                self.indicators["arrived_vehicles"],
                self.indicators["avg_waiting_time"],
                avg_velocity,
                avg_part_velocity,
                self.indicators["avg_travel_time"],
            )
        )
        print("sim_time=", b - a)

    def get_evaluations(self):
        return self.indicators

    def get_single_node_state(self, node, num_lanes=3):

        # 获取当前情况下的车辆状态
        state_count = torch.zeros(
            (1, 1, num_lanes * 4), dtype=torch.float, device=self.device
        )
        state_speed = torch.zeros(
            (1, 1, num_lanes * 4), dtype=torch.float, device=self.device
        )
        # 获取路口入口车道的ID列表
        incoming_lane_ids = traci.trafficlight.getControlledLanes(node)
        # 取出的值有重复需要去重
        ilds_in = []
        # 获取每个车道上的车辆数目
        for lane_id in incoming_lane_ids:

            ild_name = lane_id
            if ild_name not in ilds_in:
                ilds_in.append(ild_name)
        for lane_index, lane_id in enumerate(ilds_in):
            vehicle_count = traci.lane.getLastStepVehicleNumber(lane_id)
            mean_speed = traci.lane.getLastStepMeanSpeed(lane_id)
            state_count[0, 0, lane_index] = vehicle_count
            state_speed[0, 0, lane_index] = mean_speed
        # 获取当前情况下的信号灯状态
        state_current_phase = (
            traci.trafficlight.getAllProgramLogics(node)[0]
            .getPhases()[traci.trafficlight.getPhase(node)]
            .state
        )
        state_current_phase = self.phase_info_to_tensor(state_current_phase).view(
            1, 1, 20
        )
        print(state_current_phase.shape)
        assert state_count.shape == torch.Size([1, 1, 12])
        assert state_speed.shape == torch.Size([1, 1, 12])
        assert state_current_phase.shape == torch.Size([1, 1, 20])
        return state_current_phase, state_count, state_speed

    def step(self, action):
        raise NotImplementedError

    def collect_state(self):
        raise NotImplementedError

    def get_reward(self):

        raise NotImplementedError

    def _toPhase(self, node, action):  # 从action转换到phase

        signal_set = list()
        phase_set = tuple()
        phase = str()
        for _, a in enumerate(action):
            signal_set.append(self._getMovement(a))
        for j, signal in enumerate(signal_set):
            # 1개당
            for i in range(4):  # 4차로
                phase = (
                    phase
                    + "g"
                    + self.configs["numLane"] * signal[j][2 * i]
                    + signal[j][2 * i + 1]
                    + "r"
                )  # 마지막 r은 u-turn
            phase_set += phase
        print(phase_set)
        return phase_set

    def _toState(self, phase_set):  # env의 phase를 해석불가능한 state로 변환
        state_set = tuple()
        for i, phase in enumerate(phase_set):
            state = torch.zeros(8, dtype=torch.int)
            for i in range(4):  # 4차로
                phase = phase[1:]  # 우회전
                state[i] = self._mappingMovement(phase[0])  # 직진신호 추출
                phase = phase[3:]  # 직전
                state[i + 1] = self._mappingMovement(phase[0])  # 좌회전신호 추출
                phase = phase[1:]  # 좌회전
                phase = phase[1:]  # 유턴
            state_set += state
        return state_set

    def _getMovement(self, num):
        if num == 1:
            return "G"
        elif num == 0:
            return "r"
        else:
            return "y"

    def _mappingMovement(self, movement):
        if movement == "G":
            return 1
        elif movement == "r":
            return 0
        else:
            return -1  # error

    def get_all_edges(self, node, flow_type):
        edges = list()
        for _, interests in enumerate(self.configs["interest_list"]):
            if node in interests[flow_type]:
                edges.append(interests[flow_type])

    def to_next_phase(self, node):
        next_phase = (
            traci.trafficlight.getAllProgramLogics(node)[0]
            .getPhases()[(traci.trafficlight.getPhase(node) + 1) % 8]
            .state
        )
        traci.trafficlight.setRedYellowGreenState(node, next_phase)

    def phase_info_to_tensor(self, phase_info: str) -> torch.Tensor:
        # 定义一个空列表以保存转换后的值
        values = []

        for char in phase_info:
            if char.lower() == "r" or char.lower() == "R":
                values.append(1.0)
            elif char.lower() == "g" or char.lower() == "G":
                values.append(-1.0)
            elif char.lower() == "y" or char.lower() == "Y":
                values.append(0.0)
            else:
                raise ValueError(
                    f"Invalid character: '{char}'. Only 'r'/'R' and 'g'/'G' are allowed."
                )
            # 将值转换为形状为(1, 20)的张量
        tensor = torch.tensor(values, dtype=torch.float).view(1, -1)
        assert tensor.shape[1] == len(phase_info)
        return tensor


if __name__ == "__main__":
    # 示例用法
    phase_info = "rrrrGrrrrrrrrrGrrrry"
    # 定义一个空列表以保存转换后的值
    values = []

    for char in phase_info:
        if char.lower() == "r" or char.lower() == "R":
            values.append(1.0)
        elif char.lower() == "g" or char.lower() == "G":
            values.append(-1.0)
        elif char.lower() == "y" or char.lower() == "Y":
            values.append(0.0)
        else:
            raise ValueError(
                f"Invalid character: '{char}'. Only 'r'/'R' and 'g'/'G' are allowed."
            )

    # 将值转换为形状为(1, 20)的张量
    result_tensor = torch.tensor(values, dtype=torch.float).view(1, -1)
    assert result_tensor.shape[1] == len(phase_info)
    print("转换后的张量形状:", result_tensor.shape)
    print("转换后的张量:", result_tensor)
