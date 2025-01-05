import os
import random

import numpy as np

# import torch


def seed_everything(seed=1234):
    """乱数のseedを固定する関数"""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed(seed)
    # torch.backends.cudnn.deterministic = True
