import subprocess
import json
import copy
import os
import shutil
import datetime

# Create a temporary directory to store the experiment files required by the partitioner
os.makedirs("tmp_target_experiments", exist_ok=True)

with open("experiments.json") as experiment_json:
    with open("coarsener_experiments.json") as coarsener_json:
        experiment = json.load(experiment_json)
        coarsener_experiment = json.load(coarsener_json)

        # Append the arguments that don't change to the target 
        for const_args in coarsener_experiment["const_args"]:
            experiment["config"][0]["args"] += " " + const_args

        fileno = 1
        for s in coarsener_experiment["s"]:
            for t in coarsener_experiment["t"]:
                target_experiment = copy.deepcopy(experiment)
                target_experiment["config"][0]["args"] += " --c-s " + str(s)
                target_experiment["config"][0]["args"] += " --c-t " + str(t)
                with open("tmp_target_experiments/target_experiment_" + str(fileno) +".json", "w") as target_experiment_file:
                    target_experiment_file.write(json.dumps(target_experiment))
                    fileno += 1

        now = datetime.datetime.now()
        experiment_dir = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + experiment["name"]

        with open("tmp_workload.txt", "w+") as tmp_workload:
            for target in os.listdir(os.fsencode("tmp_target_experiments")):
                subprocess.run(["python", "../experiments/setup_experiments.py", "tmp_target_experiments/" + os.fsdecode(target)])
                with open(experiment_dir + "/workload.txt", "r") as workload:
                    tmp_workload.write(workload.read())
            tmp_workload.seek(0)
            # Finally, write back the the workload from the temporary file to the main file
            with open(experiment_dir + "/workload.txt", "w") as workload:
                workload.write(tmp_workload.read())

os.remove("tmp_workload.txt")
shutil.rmtree("tmp_target_experiments")
