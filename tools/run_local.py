import itertools
import os

import utils

MANUAL_SWEEP = None


if __name__ == "__main__":
    parser = utils.get_parser()

    # Args for generating split scripts
    parser.add_argument("--save_split", type=int, default=None)
    parser.add_argument("--split_dir", type=str, default="run_scripts")
    parser.add_argument("--prefix", type=str, default=None)

    args = parser.parse_args()
    

    if MANUAL_SWEEP is not None:
        scripts = []
        configs = list(itertools.product(*MANUAL_SWEEP.values()))
        keys = list(itertools.chain(*(k if isinstance(k, tuple) else (k,) for k in MANUAL_SWEEP)))
        for config in configs:
            values = itertools.chain(*(v if isinstance(v, tuple) else (v,) for v in config))
            script_args = {k: v for k, v in zip(keys, values, strict=False)}
            if "path" not in script_args:
                # Add a path based on the parameters.
                path = script_args.pop("path")
                name = "_".join([utils._format_name(v) for v in script_args.values()])
                script_args["path"] = os.path.join(path, name)
            scripts.append(script_args)
    else:
        scripts = utils.get_scripts(args)

    commands = []
    for script in scripts:
        command_str = ["python", args.entry_point]
        for arg_name, arg_value in script.items():
            command_str.append("--" + arg_name + "=" + str(arg_value))
        command_str = " ".join(command_str) + "\n"
        print(command_str)
        print()
        commands.append(command_str)

    if args.save_split is not None:
        prefix = ""
        if args.prefix is not None:
            # Load slurm prefix from path
            with open(args.prefix, "r") as f:
                prefix = f.read()
        for split in range(args.save_split):
            output_file = os.path.join(f"{args.split_dir}/job_{split}.sh")
            if not os.path.exists(args.split_dir):
                os.makedirs(args.split_dir)
            print(output_file)
            with open(output_file, "w") as f:
                f.write(prefix)
                for command in commands[
                    split * len(commands) // args.save_split : (split + 1) * len(commands) // args.save_split
                ]:
                    f.write(command + "\n")
        print(f"Saved to run_scripts, split into {args.save_split} files")
