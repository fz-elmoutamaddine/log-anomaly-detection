"""Métriques de qualité du parsing."""
import pandas as pd


def grouping_accuracy(truth, pred) -> float:
    """Part des lignes dont le groupe prédit est EXACTEMENT le groupe de la vérité terrain."""
    df = pd.DataFrame({"t": list(truth), "p": list(pred)})
    pred_size = df["p"].value_counts()
    correct = 0
    for _, g in df.groupby("t"):
        p_unique = g["p"].unique()
        if len(p_unique) == 1 and pred_size[p_unique[0]] == len(g):
            correct += len(g)
    return correct / len(df)