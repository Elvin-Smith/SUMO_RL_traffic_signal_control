
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

    print(find_ini_file(sumoConfig))
    NET_CONFIGS=read_config(find_ini_file(sumoConfig))

    sumoBinary = checkBinary('sumo')
    sumoCmd = [sumoBinary, "-c", sumoConfig]
    env=baseEnv(NET_CONFIGS)
    
    env.run(sumoCmd)
    


if __name__ == "__main__":
    Baseline(r'E:\code\mycode\network\5x5grid.sumocfg')