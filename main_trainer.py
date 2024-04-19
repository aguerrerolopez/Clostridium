import argparse
from imblearn.over_sampling import RandomOverSampler
import pickle
import numpy as np
from performance_tools import plot_tree, plot_importances, multi_class_evaluation
import wandb

# from lazypredict.Supervised import LazyClassifier
import os

# Import smote
from imblearn.over_sampling import SMOTE


def main(model, config, depth=None, wandbflag=False):
    # ============ Load config ===================
    print("Loading config")
    # with open(
    #     "/export/usuarios01/alexjorguer/Datos/HospitalProject/Clostridium/" + config
    # ) as file:
    #     config = yaml.load(file, Loader=yaml.FullLoader)

    # main_path = config["main_path"]
    # # maldi_data_path = main_path + "data/data_exp1.pkl"
    # results = main_path + "results_paper/"
    results = "results_paper/"

    # ============ Wandb ===================
    if wandbflag:
        config_dict = {
            "static_config": config,
            "hyperparams": {"depth": depth, "model": model},
        }
        wandb.init(
            project="clostridium",
            entity="alexjorguer",
            group="AutoCRT",
            config=config_dict,
        )

    # ============ Load data ===================
    print("Loading data...")
    maldi_train_path = "data/df_train_exp2.pkl"
    maldi_test_path = "data/df_test_exp2.pkl"
    with open(maldi_train_path, "rb") as handle:
        data_train = pickle.load(handle)
    with open(maldi_test_path, "rb") as handle:
        data_test = pickle.load(handle)

    x_train = np.array([a[:18000] for a in data_train["intensity"].values]) * 1e4
    x_test = np.array([a[:18000] for a in data_test["intensity"].values]) * 1e4
    y_train = data_train["label"].values
    y_test = data_test["label"].values
    id_test = data_test["id"].values

    y_test_original = y_test.copy()

    # Get masses
    x_train_masses = np.array([a[:18000] for a in data_train["mz"].values])
    x_test_masses = np.array([a[:18000] for a in data_test["mz"].values])

    # Convert the labels: if "027" -> 0, if "181" -> 1, otherwise -> 2
    y_train = np.array([0 if a == "027" else 1 if a == "181" else 2 for a in y_train])
    y_test = np.array([0 if a == "027" else 1 if a == "181" else 2 for a in y_test])

    # Oversample trainig data using smtoe
    sm = SMOTE(random_state=42)
    x_train, y_train = sm.fit_resample(x_train, y_train)

    # Get now value counts
    print("Value counts of train: ", np.unique(y_train, return_counts=True))

    # ============ Preprocess data ===================

    if wandbflag:
        # Save number of samples in the dataset
        wandb.log({"Number of samples": len(np.vstack((x_train, x_test)))})
        # Save number of features in the dataset
        wandb.log({"Number of features": len(np.vstack((x_train, x_test)))})
        # Save number of samples in train
        wandb.log({"Number of samples in train": len(x_train)})
        # Save number of samples in test
        wandb.log({"Number of samples in test": len(x_test)})

    # Check if path "results_paper/model" exists, if not, create it
    # if not os.path.exists(results + "exp1/" + model + "/"):
    #     os.makedirs(results + "exp1/" + model + "/")
    # results = results + "exp1/" + model

    if model == "base":
        ros = RandomOverSampler()
        x_train, y_train = ros.fit_resample(x_train, y_train)

        clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None)
        models, predictions = clf.fit(x_train, x_test, y_train, y_test)

        print(models)

    elif model == "ksshiba":
        from models import KSSHIBA

        kernel = "linear"
        epochs = 200
        fs = True

        # results = (
        #     results + "_kernel_" + kernel + "_epochs_" + str(epochs) + "_fs_" + str(fs)
        # )
        # Check if path "results_paper/model" exists, if not, create it
        if not os.path.exists(results):
            os.makedirs(results)

        print("Training KSSHIBA")
        model = KSSHIBA(kernel=kernel, epochs=epochs, fs=fs)

        model.fit(x_train, y_train)

        print("Evaluating KSSHIBA")
        # # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)
        pred_proba = pred_proba / pred_proba.sum(axis=1)[:, None]

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )

        # Get which has failed
        failed = np.where(pred != y_test)[0]
        # Print the original label and the predicted label
        print("ID\tOriginal\tPredicted")
        for i in failed:
            print(id_test[i], "\t", y_test_original[i], "\t", pred[i])

        # model.fit(np.vstack((x_train, x_test)), np.hstack((y_train, y_test)))
        # pickle.dump(model, open(results + "/model_all.pkl", "wb"))

    elif model == "favae":
        from models import FAVAE

        model = FAVAE(latent_dim=100, epochs=1000)
        model.fit(x_train, y_train)

        # # Evaluation
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)
        pred_proba = pred_proba / pred_proba.sum(axis=1)[:, None]

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )

        model.fit(np.vstack((x_train, x_test)), np.hstack((y_train, y_test)))
        store = {"model": model, "x_train": x_train, "y_train": y_train}
        pickle.dump(store, open(results + "/model_all.pkl", "wb"))

    elif model == "rf":
        from models import RF

        # Declare the model
        model = RF(max_depth=depth)
        # Train it
        model.fit(x_train, y_train)
        model = model.get_model()

        # save the model to disk
        pickle.dump(model, open(results + "/model.pkl", "wb"))

        # Evaluation
        if wandbflag:
            wandb.sklearn.plot_learning_curve(model, x_train, y_train)

        # Evaluation
        importances = model.feature_importances_
        plot_importances(
            model,
            importances,
            x_train_masses,
            results + "/feature_importance_trainmodel.png",
            wandbflag=wandbflag,
        )
        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )

        # Get which has failed
        failed = np.where(pred != y_test)[0]
        # Print the original label and the predicted label
        print("ID\tOriginal\tPredicted")
        for i in failed:
            print(id_test[i], "\t", y_test_original[i], "\t", pred[i])

        # Retrain the model with all data and save it
        # model = RF(max_depth=depth)
        # model.fit(np.vstack((x_train, x_test)), np.hstack((y_train, y_test)))
        # model = model.get_model()
        # pickle.dump(model, open(results + "/model_all.pkl", "wb"))
        # importances = model.feature_importances_
        # plot_importances(
        #     model,
        #     importances,
        #     x_total_masses,
        #     results + "/feature_importance_completemodel.png",
        #     wandbflag=wandbflag,
        # )

    elif model == "dblfs":
        from models import LR_ARD

        # conver y_train to ohe
        # y_train2 = np.eye(3)[y_train]
        # y_test2 = np.eye(3)[y_test]

        # # Declare the model
        # pred_proba = []
        # for i in np.arange(y_train2.shape[1]):
        #     model = LR_ARD()
        #     # TODO: y_train must be ohe, check it
        #     model.fit(x_train, y_train2[:, i])
        #     pred_proba_i = model.predict_proba(x_test)
        #     pred_proba.append(pred_proba_i)
        # pred_proba = np.array(pred_proba).T
        # pred = np.argmax(pred_proba, axis=1)

    elif model == "lr":
        from models import LR

        model = LR()
        model.fit(x_train, y_train)
        model = model.get_model()

        # save the model to disk
        pickle.dump(model, open(results + "/model.pkl", "wb"))

        if wandbflag:
            wandb.sklearn.plot_learning_curve(model, x_train, y_train)

        # Evaluation
        importances = model.coef_
        for i in range(len(importances)):
            plot_importances(
                model,
                importances[i, :],
                x_train_masses,
                results + "/feature_importance_trainmodel_class" + str(i) + ".png",
                wandbflag=wandbflag,
            )
        plot_importances(
            model,
            np.mean(importances, axis=0),
            x_train_masses,
            results + "/feature_importance_trainmodel_mean_all_classes.png",
            wandbflag=wandbflag,
        )

        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
        model = LR()
        model.fit(np.vstack((x_train, x_test)), np.hstack((y_train, y_test)))
        model = model.get_model()
        pickle.dump(model, open(results + "/model_all.pkl", "wb"))
        importances = model.coef_
        for i in range(len(importances)):
            plot_importances(
                model,
                importances[i, :],
                x_train_masses,
                results + "/feature_importance_completemodel_class" + str(i) + ".png",
                wandbflag=wandbflag,
            )
        plot_importances(
            model,
            np.mean(importances, axis=0),
            x_train_masses,
            results + "/feature_importance_completemodel_mean_all_classes.png",
            wandbflag=wandbflag,
        )

    elif model == "dt":
        from models import DecisionTree

        model = DecisionTree(max_depth=depth)
        model.fit(x_train, y_train)
        model = model.get_model()

        # save the model to disk
        pickle.dump(model, open(results + "/model.pkl", "wb"))

        if wandbflag:
            wandb.sklearn.plot_learning_curve(model, x_train, y_train)

        # Evaluation
        importances = model.feature_importances_
        plot_importances(
            model,
            importances,
            x_train_masses,
            results + "/feature_importance_trainmodel.png",
            wandbflag=wandbflag,
        )

        pred = model.predict(x_test)
        pred_proba = model.predict_proba(x_test)

        multi_class_evaluation(
            y_test,
            pred,
            pred_proba,
            results_path=results,
            wandbflag=wandbflag,
        )
        # Get which has failed
        failed = np.where(pred != y_test)[0]
        # Print the original label and the predicted label
        print("ID\tOriginal\tPredicted")
        for i in failed:
            print(id_test[i], "\t", y_test_original[i], "\t", pred[i])

        # model = DecisionTree(max_depth=depth)
        # model.fit(np.vstack((x_train, x_test)), np.hstack((y_train, y_test)))
        # model = model.get_model()
        # pickle.dump(model, open(results + "/model_all.pkl", "wb"))
        # importances = model.feature_importances_
        # plot_importances(
        #     model,
        #     importances,
        #     x_total_masses,
        #     results + "/feature_importance_completemodel.png",
        #     wandbflag=wandbflag,
        # )
        # print("Plotting final tree...")
        # plot_tree(
        #     model,
        #     np.vstack((x_train, x_test)),
        #     np.hstack((y_train, y_test)),
        #     x_total_masses,
        #     results + "/complete_tree.svg",
        #     wandbflag=wandbflag,
        # )

    elif model == "favae":
        raise ValueError("Model not implemented")
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

    # python main_trainer.py --model rf --config config.yaml
