from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr, spearmanr, kendalltau
import re
import pandas as pd

chateval_scores = []
eval_scores = []

with open("norm_output_scores.txt", "r+") as file1:
    lines = file1.readlines()
    for i in range(len(lines)):
        if "Strategia: concurrent" in lines[i]:
            
            chateval_match = re.search(r"ChatEval Score: (\d+(\.\d+)?)", lines[i + 1])
            eval_match = re.search(r"Eval Score: (\d+)", lines[i + 1])

            if chateval_match and eval_match:
                chateval_scores.append(float(chateval_match.group(1)))
                eval_scores.append(int(eval_match.group(1)))

print(chateval_scores)

#Calcolo metriche
spearman_corr, _ = spearmanr(chateval_scores, eval_scores)
pearson_corr, _ = pearsonr(chateval_scores, eval_scores)
kendall_corr, _ = kendalltau(chateval_scores, eval_scores)

metrics_df = pd.DataFrame({
    'ChatEval Score': chateval_scores,
    'Eval Score': eval_scores,
    'Spearman': [spearman_corr] * len(chateval_scores),
    'Pearson': [pearson_corr] * len(chateval_scores),
    'Kendall-Tau': [kendall_corr] * len(chateval_scores)
})


metrics_df.to_csv('concurrent_scores.csv', index=False)


