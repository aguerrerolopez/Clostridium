import dtreeviz
import matplotlib.pyplot as plt
import wandb
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    ConfusionMatrixDisplay,
)
import pickle
import numpy as np


def plot_tree(model, x_train, y_train, masses_original, path, wandbflag=False):
    viz_model = dtreeviz.model(
        model,
        X_train=x_train,
        y_train=y_train,
        feature_names=masses_original,
        target_name="Ribotype",
        class_names=["RT027", "RT181", "Others"],
    )
    v = viz_model.view()  # render as SVG into internal object
    print(path)
    v.save(path)  # optionally save as svg


def plot_importances(model, importances, masses_original, path, wandbflag=False):
    masses = np.mean(masses_original, axis=0)
    plt.figure(figsize=(10, 10))
    plt.plot(masses, importances)
    plt.xlabel("Feature importance")
    plt.ylabel("Feature")
    plt.savefig(path)
    # Dump as a pickle masses and importances
    results = {"masses": masses, "importances": importances}
    pickle.dump(results, open(path + ".pkl", "wb"))
    if wandbflag:
        wandb.sklearn.plot_feature_importances(model, masses)


def multi_class_evaluation(
    true_value, pred, pred_proba, wandbflag=False, results_path=None
):
    # Check if there is more than one label in true_value
    if len(np.unique(true_value)) == 1:
        print("Only one label in true_value, cannot Confusion matrix")
        cm = None
        roc_auc = None
    else:
        # compute confusion matrix
        cm = confusion_matrix(true_value, pred)
        # Store it as png
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm, display_labels=["RT027", "RT181", "Others"]
        )
        disp.plot()
        plt.savefig(results_path + "/confusion_matrix.png")
        # compute roc auc
        roc_auc = roc_auc_score(true_value, pred_proba, multi_class="ovr")
    # compute precision, recall and f1-score
    precision = precision_score(true_value, pred, average="macro")
    recall = recall_score(true_value, pred, average="macro")
    f1 = f1_score(true_value, pred, average="macro")
    # compute balanced acc
    balanced_acc = balanced_accuracy_score(true_value, pred)
    # compute accuracy
    acc = accuracy_score(true_value, pred)

    if wandbflag:
        # Visualize single plot
        wandb.sklearn.plot_confusion_matrix(
            true_value, pred, labels=["RT027", "RT181", "Others"]
        )
        wandb.log({"Precision": precision})
        wandb.log({"Recall": recall})
        wandb.log({"F1": f1})
        wandb.log({"Balanced accuracy": balanced_acc})
        wandb.log({"ROC AUC": roc_auc})
        wandb.log({"Accuracy": acc})
    else:
        print("Confusion Matrix:")
        print(cm)
        print("Precision: ", precision)
        print("Recall: ", recall)
        print("F1: ", f1)
        print("Balanced accuracy: ", balanced_acc)
        print("ROC AUC: ", roc_auc)
        print("Accuracy: ", acc)
        # Create a dictionary with the metrics and store it as pkl
        metrics = {
            "Confusion Matrix": cm,
            "Precision": precision,
            "Recall": recall,
            "F1": f1,
            "Balanced accuracy": balanced_acc,
            "ROC AUC": roc_auc,
            "Accuracy": acc,
        }
        with open(results_path + "/metrics.pkl", "wb") as handle:
            pickle.dump(metrics, handle, protocol=pickle.HIGHEST_PROTOCOL)
