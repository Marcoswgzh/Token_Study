# written by Erika Škodová, Nadja Poltoracki
from exp_setup import exp_setup
from recovery_project.simulation.parallel_attacker import send_attack

if __name__ == '__main__':
    exp_setup("rq1","rq1_entropy.json",send_attack)
