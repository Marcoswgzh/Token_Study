# written by Erika Škodová
from exp_setup import exp_setup
from recovery_project.experiments.non_parallel_attacker import non_parallel_attacker

if __name__ == '__main__':
    exp_setup("rq3","rq3_rate_limiting.json",non_parallel_attacker)