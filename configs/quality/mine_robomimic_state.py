"""
Config for training beta vae's on robomimic

Example command:

python scripts/train.py --config=configs/quality/infonce_robomimic_state.py --path ../test/robomimic/ --name infonce

"""

import optax
import tensorflow as tf
from ml_collections import ConfigDict

from openx.algs.mine import MINE
from openx.data.datasets.robomimic import robomimic_dataset_transform
from openx.data.utils import NormalizationType, StateEncoding
from openx.networks.components.mlp import MLP
from openx.networks.core import Concatenate, MultiEncoder
from openx.utils.spec import ModuleSpec


def get_config(config_str="square/mh,1"):
    ds, seed = config_str.split(",")
    seed = int(seed)

    # Define the structure
    structure = {
        "observation": {
            "state": {
                StateEncoding.EE_POS: NormalizationType.GAUSSIAN,
                StateEncoding.EE_QUAT: NormalizationType.GAUSSIAN,
                StateEncoding.GRIPPER: NormalizationType.NONE,
                StateEncoding.MISC: NormalizationType.GAUSSIAN,
            },
        },
        "action": {
            "desired_delta": {
                StateEncoding.EE_POS: NormalizationType.GAUSSIAN,
                StateEncoding.EE_EULER: NormalizationType.GAUSSIAN,
            },
            "desired_absolute": {StateEncoding.GRIPPER: NormalizationType.NONE},
        },
    }

    dataloader = dict(
        datasets={
            ds.replace("/", "_"): dict(
                path="/home/hanbit-o/code/openx/demonstration-information/dataset/{ds}/robo_mimic/1.0.0".format(ds=ds),
                train_split="train",
                val_split="val",
                transform=ModuleSpec.create(robomimic_dataset_transform),
            ),
        },
        n_obs=1,
        n_action=1,
        shuffle_size=100000,
        batch_size=256,
        recompute_statistics=False,  # Small, just recompute.
        cache=True,  # Small enough to stay in memory
        prefetch=tf.data.AUTOTUNE,  # Enable prefetch.
    )

    alg = ModuleSpec.create(
        MINE,
        obs_action_encoder=ModuleSpec.create(
            MultiEncoder,
            encoders={"observation->state": None, "action": None},
            trunk=ModuleSpec.create(
                Concatenate, model=ModuleSpec.create(MLP, [512, 512], activate_final=True), flatten_time=True
            ),
        ),
        alpha=0.9,
    )

    lr_schedule = ModuleSpec.create(optax.constant_schedule, 0.0001)
    optimizer = ModuleSpec.create(optax.adam)

    return ConfigDict(
        dict(
            structure=structure,
            alg=alg,
            dataloader=dataloader,
            optimizer=optimizer,
            lr_schedule=lr_schedule,
            # steps=50000,
            steps=5000,
            log_freq=500,
            val_freq=2500,
            # save_freq=10000,
            save_freq=1000,
            val_steps=25,
            seed=seed,
        )
    )
