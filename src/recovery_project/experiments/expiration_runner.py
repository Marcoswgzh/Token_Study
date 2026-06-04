# written by Erika Škodová
from exp_setup import exp_setup
from recovery_project.simulation.parallel_attacker import send_attack

if __name__ == '__main__':
    exp_setup("rq2","rq2_expiration_window_attack.json",send_attack)
