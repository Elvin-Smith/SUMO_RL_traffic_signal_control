
import json
import os
import sys
import time
import torch
import torch.optim as optim
import traci
import random
import numpy as np
import traci.constants as tc
from sumolib import checkBinary
from configs import EXP_CONFIGS
from Env.base import baseEnv
from gen_net import Grid_Net
from Utils.utils import *
from Utils.master_config import *

def Baseline(sumoConfig):

    print(find_json_file(sumoConfig))
    NET_CONFIGS=read_list_from_json(find_json_file(sumoConfig))

    sumoBinary = checkBinary('sumo')
    sumoCmd = [sumoBinary, "-c", sumoConfig]
    env=baseEnv(NET_CONFIGS)
    
    env.run(sumoCmd)
    


if __name__ == "__main__":
    Baseline(r'J:\code\mycode\network\5x5grid.sumocfg')