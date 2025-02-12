# far runnare questo codice con i vari dialoghi, in particolare questo deve avvenire ognuno per i 7 dialoghi
# (l'idea è di scrivere uno script che vada a scrivere nel config.yaml il tipo di dialogo su cui deve fare test)
# comando simile: python metriche.py agentverse/tasks/llm_eval/data/faireval/preprocessed_data/dialogo1.json sequential/summarizer/simultaneous
# dopodiche viene salvato l'output e vengono presi tutte le valutazioni totali dei due agenti:
# dopo ancora viene fatta una media di questi due valori che deve essere confrontata con il valore di eval_score
# questo confronto deve avvenire tramite 4 metriche precise:
#   -Kappa di Cohen,
#   -Spearman, 
#   -Pearson e 
#   -Kendall-Tau

# far scrivere in un txt tutto il ragionamento di chateval con tutte le metriche messe sotto e i parametri utilizzati

import argparse
import numpy as np
import subprocess
import json
import re

def change_dataset_strategy(path, strategy):
    # primo config.yaml
    with open("agentverse/tasks/config.yaml", "r") as file1:
        lines = file1.readlines()
    
    lines[1] = "  ./" + path + "\n"
    lines[32] = "      type: " + strategy + "\n"
    print("sono qui")
    
    with open("agentverse/tasks/config.yaml", 'w') as file2:
        file2.writelines(lines)

    # secondo config.yaml
    with open("agentverse/tasks/llm_eval/config.yaml", "r") as file1:
        lines = file1.readlines()
    
    lines[3] = "  ./" + path + "\n"
    lines[34] = "      type: " + strategy + "\n"
    
    with open("agentverse/tasks/llm_eval/config.yaml", 'w') as file2:
        file2.writelines(lines)
        
def parse_chateval_output(path, strategy, file_name):
    command = "python llm_eval.py --config agentverse/tasks/llm_eval/config.yaml"
    print("quiii")

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True, stderr=subprocess.STDOUT)
    
    if result.returncode != 0:
        print(f"Errore nell'esecuzione del comando: {result.stderr}")

    with open(file_name, "w+") as f1:
       f1.write(result.stdout)


    with open(file_name, "r") as f2:
        log_output = f2.read()

    # Regex per estrarre i punteggi
    pattern = r"The score of Assistant 1: (\d+).*?The score of Assistant 2: (\d+)"
    matches = re.findall(pattern, log_output, re.DOTALL)

    # Converte i punteggi in interi
    assistant_1_scores = [int(match[0]) for match in matches[-2:]]  # Prendi gli ultimi due punteggi
    assistant_2_scores = [int(match[1]) for match in matches[-2:]]

    return assistant_1_scores, assistant_2_scores


def take_eval_score_by_json(dataset):

    with open('convai2_data.json', 'r') as convai2_file:
        convai = json.load(convai2_file)

    with open(dataset, 'r') as file:
        data = json.load(file)

    question_id = data[0].get('question_id')

    for dialog in convai:
        if dialog.get('dialog_id') == question_id:
            return dialog.get('eval_score')

    return None

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Chosen dataset per il test")
    parser.add_argument("--strategy", required=True, help="Chosen type of communication strategy")

    args = parser.parse_args()
   
    dataset = args.dataset
    strategy = args.strategy
    file_name = dataset[-13:-5] + "_" + strategy + ".txt"
    # scelta del dataset e della strategia
    change_dataset_strategy(dataset, strategy)
    

    # prendiamo l'output, lo salviamo in un file e ci prendiamo i valori da calcolare, 
    # il valore sarà la media dei punteggi di chateval
    ass1, ass2, = parse_chateval_output(dataset, strategy, file_name)
    chateval_score = np.mean(ass1 + ass2)

    eval_score = take_eval_score_by_json(dataset)

    with open("output_scores.txt", "a+") as file:
        file.writelines("Dataset usato: " + dataset + "\t" + "Strategia: " + strategy + "\n")
        file.writelines("ChatEval Score: " + str(chateval_score) + "\t")
        file.writelines("Eval Score: " + str(eval_score) + "\n")

        file.close()




