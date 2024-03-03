from copy import deepcopy
import traci
import torch
from base import baseEnv


class CityEnv(baseEnv):
    def __init__(self, configs):
        super().__init__(configs)

    def step(self, action, mask_matrix, action_update_mask):

        # 遍历所有智能体
        for index in torch.nonzero(mask_matrix):

            tl_rl = self.tl_rl_list[index]
            phase_length_set = self._toPhaseLength(tl_rl, action[0, index])

            tls = traci.trafficlight.getCompleteRedYellowGreenDefinition(
                self.tl_rl_list[index]
            )
            for phase_idx in self.traffic_node_info[tl_rl]["phase_index"]:
                tls[0].phases[phase_idx].duration = phase_length_set[phase_idx]
            traci.trafficlight.setProgramLogic(tl_rl, tls[0])
            self.tl_rl_memory[index].action = action[0, index]
            # print(traci.trafficlight.getCompleteRedYellowGreenDefinition(self.tl_rl_list[index])[0].phases)
            # print(phase_length_set)
        # action을 environment에 등록 후 상황 살피기,action을 저장
        # step
        traci.simulationStep()
        # for index in torch.nonzero(mask_matrix):
        #     tls=traci.trafficlight.getCompleteRedYellowGreenDefinition(self.tl_rl_list[index])
        #     print(tls[0].phases,"after")

        self.before_action_update_mask = action_update_mask

    def _toPhaseLength(self, tl_rl, action):  # action을 해석가능한 phase로 변환
        tl_dict = deepcopy(self.traffic_node_info[tl_rl])
        for j, idx in enumerate(tl_dict["phase_index"]):
            tl_dict["phase_duration"][idx] = tl_dict["phase_duration"][idx] + tl_dict[
                "matrix_actions"
            ][action[0, 0]][j] * int((action[0, 1] + 1) * 1.5)
        phase_length_set = tl_dict["phase_duration"]
        return phase_length_set
