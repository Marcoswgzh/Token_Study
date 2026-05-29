# written by Erika Škodová, Nadja Poltoracki
import json
from pathlib import Path
from recovery_project.services.token_service import TokenService as ts
from recovery_project.simulation.attacker import Attacker


if __name__ == '__main__':
    # Read a JSON file
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    config_path = base_dir / "configs" / "experiments" / "rq1_entropy.json"

    with open(config_path, "r") as f:
        data = json.load(f)
    print(data[0])

    results_times = []
    for i in range(len(data)):
        experiment_time = []
        for j in range(data[i]["trials"]):
            # Test token generation
            token_info = data[i]["token_policy"]
            token = ts(token_info["alphabet"],token_info["length"]).generate_token()[0] #only stores token, not hash

            # Call bruteforce attack
            attack = Attacker(token_info["alphabet"])
            experiment_time.append(attack.send_attack(token,token_info["length"]))
        results_times.append(experiment_time)