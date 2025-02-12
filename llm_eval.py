import os
os.environ["OPENAI_API_KEY"] = "***"
os.environ["OPENAI_BASE_URL"] = "***"
import json
from eval_helper.get_evaluation import get_evaluation
from agentverse.agentverse import AgentVerse
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--config", type=str, default="config.yaml")
parser.add_argument("--reverse_input", default=False, action="store_true")

args = parser.parse_args()

agentverse, args_data_path, args_output_dir = AgentVerse.from_task(args.config)

print(args)

os.makedirs(args_output_dir, exist_ok=True)
with open(os.path.join(args_output_dir, "args.txt"), "w") as f:
    f.writelines(str(args))

with open(args_data_path) as f:
    data = json.load(f)

if "faireval" in args_data_path:
    pair_comparison_output = []

    for num, ins in enumerate(data[:80]):

        print(f"================================instance {num}====================================")

        for agent_id in range(len(agentverse.agents)):
            agentverse.agents[agent_id].source_text = ins["question"]

            participant1_responses = [v for k, v in ins["response"].items() if k.startswith("participant1")]
            participant2_responses = [v for k, v in ins["response"].items() if k.startswith("participant2")]

            agentverse.agents[agent_id].compared_text_one = " ".join(participant1_responses)
            agentverse.agents[agent_id].compared_text_two = " ".join(participant2_responses)

            agentverse.agents[agent_id].final_prompt = ""

        agentverse.run()

        evaluation = get_evaluation(setting="every_agent", messages=agentverse.agents[0].memory.messages, agent_nums=len(agentverse.agents))

        evaluation_data = {
            "question": ins["question"],
            "response": {
                "participant1": " ".join(participant1_responses),
                "participant2": " ".join(participant2_responses)
            },
            "evaluation": evaluation
        }

        pair_comparison_output.append(evaluation_data)

        os.makedirs(args_output_dir, exist_ok=True)
        with open(os.path.join(args_output_dir, "pair_comparison_results.json"), "w") as f:
            json.dump(pair_comparison_output, f, indent=4)

elif "adversarial" in args_data_path:
    pair_comparison_output = []

    for num, ins in enumerate(data):

        print(f"================================instance {num}====================================")

        for agent_id in range(len(agentverse.agents)):
            agentverse.agents[agent_id].source_text = ins["question"]

            if args.reverse_input:
                agentverse.agents[agent_id].compared_text_one = ins["response"]["output_2"]
                agentverse.agents[agent_id].compared_text_two = ins["response"]["output_1"]
            else:
                agentverse.agents[agent_id].compared_text_one = ins["response"]["output_1"]
                agentverse.agents[agent_id].compared_text_two = ins["response"]["output_2"]

            agentverse.agents[agent_id].final_prompt = ""

        agentverse.run()

        evaluation = get_evaluation(setting="every_agent", messages=agentverse.agents[0].memory.messages, agent_nums=len(agentverse.agents))

        pair_comparison_output.append({
            "question": ins["question"],
            "response": {
                "output_1": ins["response"]["output_1"],
                "output_2": ins["response"]["output_2"]
            },
            "evaluation": evaluation
        })

        os.makedirs(args_output_dir, exist_ok=True)
        with open(os.path.join(args_output_dir, "pair_comparison_results.json"), "w") as f:
            json.dump(pair_comparison_output, f, indent=4)
