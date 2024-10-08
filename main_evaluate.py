import argparse
from sklearn.model_selection import train_test_split
import yaml
from imblearn.over_sampling import RandomOverSampler
import pickle
import numpy as np
from performance_tools import plot_tree, plot_importances, multi_class_evaluation
import wandb
from lazypredict.Supervised import LazyClassifier
import os


def main(model, config, depth=None, wandbflag=False):
    # ============ Load config ===================
    print("Loading config")
    with open(
        "/export/usuarios01/alexjorguer/Datos/HospitalProject/Clostridium/" + config
    ) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    main_path = config["main_path"]
    maldi_data_path = main_path + "data/data_exp3.pkl"
    results = main_path + "results_paper/"

    # ============ Wandb ===================
    if wandbflag:
        config_dict = {
            "static_config": config,
            "hyerparams": {"depth": depth, "model": model},
        }
        wandb.init(
            project="clostridium",
            entity="alexjorguer",
            group="AutoCRT",
            config=config_dict,
        )

    # ============ Load data ===================
    print("Loading data...")
    with open(maldi_data_path, "rb") as handle:
        data = pickle.load(handle)
    print(data.keys())
    x_test = np.vstack(data["test"]["intensities"]) * 1e4
    y_test = data["test"]["labels"]
    x_masses = np.vstack(np.array(data["test"]["masses"]))

    # Check if path "results_paper/model" exists, if not, create it
    if not os.path.exists(results + "exp3/" + model + "/"):
        os.makedirs(results + "exp3/" + model + "/")
    results = results + "exp3/" + model + "/"

    if model == "base":
        raise ValueError("Base model not implemented yet")

    if model == "rf":
        # Load results from experiment 1 from a pkl
        with open(main_path + "results_paper/exp1/rf/metrics.pkl", "rb") as handle:
            metrics = pickle.load(handle)
        print("Results in experiment 1:")
        for key in metrics.keys():
            print(key)
            print(metrics[key])

        # Load feature importances from experiment 1
        with open(
            main_path
            + "results_paper/exp1/rf/feature_importance_completemodel.png.pkl",
            "rb",
        ) as handle:
            importances = pickle.load(handle)
        masses = importances["masses"]
        importances = importances["importances"]
        # Sort masses by importances
        idx = np.argsort(-importances)
        masses = masses[idx]
        print("Masses sorted by importance")
        print(masses)
        print(importances[idx])

        # Load model from pickle file
        with open(main_path + "results_paper/exp1/rf/model_all.pkl", "rb") as handle:
            model = pickle.load(handle)

        # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
        # Train the final model with all data
        # TODO: Load data from exp1 and retrain the model with all data: exp1+exp3

    elif model == "lr":
        # Load results from experiment 1 from a pkl
        with open(main_path + "results_paper/exp1/lr/metrics.pkl", "rb") as handle:
            metrics = pickle.load(handle)
        print("Results in experiment 1:")
        for key in metrics.keys():
            print(key)
            print(metrics[key])

        with open(
            main_path
            + "results_paper/exp1/lr/feature_importance_completemodel_mean_all_classes.png.pkl",
            "rb",
        ) as handle:
            importances = pickle.load(handle)
        masses = importances["masses"]
        importances = importances["importances"]
        # Sort masses by importances
        idx = np.argsort(-importances)
        masses = masses[idx]
        print("Masses sorted by importance")
        print(masses)
        print(importances[idx])

        # Load model from pickle file
        with open(main_path + "results_paper/exp1/lr/model_all.pkl", "rb") as handle:
            model = pickle.load(handle)

        if wandbflag:
            wandb.sklearn.plot_learning_curve(model, x_test, y_test)

        # Evaluation

        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        print("Results in experiment 3:")
        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
        # Train the final model with all data
        # TODO: Load data from exp1 and retrain the model with all data: exp1+exp3

    elif model == "dt":
        # Load results from experiment 1 from a pkl
        with open(main_path + "results_paper/exp1/dt/metrics.pkl", "rb") as handle:
            metrics = pickle.load(handle)
        print("Results in experiment 1:")
        for key in metrics.keys():
            print(key)
            print(metrics[key])

        with open(
            main_path
            + "results_paper/exp1/dt/feature_importance_completemodel.png.pkl",
            "rb",
        ) as handle:
            importances = pickle.load(handle)
        masses = importances["masses"]
        importances = importances["importances"]
        # Sort masses by importances
        idx = np.argsort(-importances)
        masses = masses[idx]
        print("Masses sorted by importance")
        print(masses)
        print(importances[idx])

        # Load model from pickle file
        with open(main_path + "results_paper/exp1/dt/model_all.pkl", "rb") as handle:
            model = pickle.load(handle)

        if wandbflag:
            wandb.sklearn.plot_learning_curve(model, x_test, y_test)

        # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        print("Results in experiment 3:")
        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
        # Train the final model with all data
        # TODO: Load data from exp1 and retrain the model with all data: exp1+exp3

    elif model == "favae":
        # Load model from pickle file
        with open(main_path + "results_paper/exp1/favae/model_all.pkl", "rb") as handle:
            model = pickle.load(handle)

        # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        # Make pred_proba to sum 1 in each row
        pred_proba = pred_proba / pred_proba.sum(axis=1)[:, None]

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
    elif model == "ksshiba":
        # Load model from pickle file
        with open(
            main_path
            + "results_paper/exp1/ksshiba_kernel_linear_epochs_1000_fs_True/model_all.pkl",
            "rb",
        ) as handle:
            model = pickle.load(handle)

        # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)
        print(pred)

        # Make pred_proba to sum 1 in each row
        pred_proba = pred_proba / pred_proba.sum(axis=1)[:, None]

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
    else:
        raise ValueError("Model not implemented")


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument(
        "--model",
        type=str,
        default="base",
        help="Model to train",
        choices=["base", "rf", "dt", "favae", "lr", "ksshiba"],
    )
    argparse.add_argument(
        "--config", type=str, default="config.yaml", help="Path to config file"
    )
    argparse.add_argument("--depth", type=int, default=10, help="Max depth of the tree")
    argparse.add_argument("--wandb", type=bool, default=False, help="Use wandb")

    args = argparse.parse_args()

    main(args.model, args.config, depth=args.depth, wandbflag=args.wandb)
