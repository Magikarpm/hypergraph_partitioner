#!/usr/bin/python3
import subprocess
import ntpath
import argparse
import time
import re
import math
import os
import os.path
from threading import Timer
import signal

###################################
# SETUP ENV
###################################
algorithm = "Mt-KaHIP"
mt_kahip = os.environ.get("MT_KAHIP")
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("threads", type=int)
parser.add_argument("k", type=int)
parser.add_argument("epsilon", type=float)
parser.add_argument("seed", type=int)
parser.add_argument("objective", type=str)
parser.add_argument("timelimit", type=int)

args = parser.parse_args()

# Run Mt-KaHIP
mt_kahip_proc = subprocess.Popen([mt_kahip,
                                  args.graph,
                                  "--k=" + str(args.k),
                                  "--num_threads=" + str(args.threads),
                                  "--seed=" + str(args.seed),
                                  "--imbalance=" + str(args.epsilon * 100.0),
                                  "--preconfiguration=fastsocialmultitry_parallel"],
                                 stdout=subprocess.PIPE, universal_newlines=True)

def kill_proc():
	mt_kahip_proc.terminate() #signal.SIGTERM

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = mt_kahip_proc.communicate()
t.cancel()
end = time.time()

total_time = 0
cut = 0
km1 = 0
imbalance = 0.0
timeout = "no"
failed = "no"

if mt_kahip_proc.returncode == 0:
  # Extract metrics out of MT-KaHIP output
  already_found_refinement_line = False
  for line in out.split('\n'):
    s = str(line).strip()
    if ">> Refinement" in s:
      already_found_refinement_line = True
    if "cut" in s and already_found_refinement_line:
      cut = int(s.split('cut')[1])
      km1 = int(s.split('cut')[1])
    if "balance" in s and already_found_refinement_line:
      imbalance = float(s.split('balance')[1]) - 1.0
    if "time spent for partitioning" in s and already_found_refinement_line:
      total_time = float(s.split('time spent for partitioning')[1])

elif mt_kahip_proc.returncode == -signal.SIGTERM:
  timeout = "yes"
else:
  failed = "yes"

# CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed
print(algorithm,
      ntpath.basename(args.graph),
      timeout,
      args.seed,
      args.k,
      args.epsilon,
      args.threads,
      imbalance,
      total_time,
      args.objective,
      km1,
      cut,
      failed,
      sep=",")