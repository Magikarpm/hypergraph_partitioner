#!/usr/bin/python3
import os
import os.path

from mt_kahypar_common import (get_args, invalid, parse, parse_or_default,
                               parse_required_value, print_result,
                               run_mtkahypar, set_result_vals)

###################################
# SETUP ENV
###################################
algorithm = "MT-KaHyPar-D"
mt_kahypar = os.environ.get("MT_KAHYPAR")
assert (mt_kahypar != None), "check env.sh"
###################################

args = get_args()
if args.name != "":
  algorithm = args.name

result, success = run_mtkahypar(mt_kahypar, args, default_args={
  "--preset-type": "default",
  "--instance-type": "hypergraph",
})

set_result_vals(
  coarsening_max_allowed_weight_multiplier=invalid,
  coarsening_contraction_limit_multiplier=invalid,
  initial_km1=invalid,
  km1=invalid,
  initial_cut=invalid,
  cut=invalid,
  total_time=invalid,
  imbalance=1.0,
)
if success:
  parse_required_value(result, "coarsening_max_allowed_weight_multiplier", parser=float)
  parse_required_value(result, "coarsening_contraction_limit_multiplier", parser=int)
  parse_required_value(result, "initial_km1", parser=int)
  parse_required_value(result, "km1", parser=int)
  parse_required_value(result, "initial_cut", parser=int)
  parse_required_value(result, "cut", parser=int)
  parse_required_value(result, "totalPartitionTime", out="total_time")
  parse_required_value(result, "imbalance")

# CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,initial_km1,km1,cut,failed
print_result(algorithm, args)
