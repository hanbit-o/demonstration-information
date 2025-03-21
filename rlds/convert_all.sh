cd /home/hanbit-o/code/sub-goal-decomposed-vip/third_party/demonstration-information/rlds/robomimic_dataset
tasks=("can" "square" "lift")
for task in "${tasks[@]}"
do
    manual_dir="/home/hanbit-o/code/sub-goal-decomposed-vip/third_party/robomimic/datasets/$task/mh/"
    data_dir="/home/hanbit-o/code/sub-goal-decomposed-vip/third_party/demonstration-information/dataset/$task/mh/"
    tfds build --manual_dir $manual_dir --data_dir $data_dir
done

cd ..