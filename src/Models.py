import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
 
from sklearn.cluster import KMeans
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    r2_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    KFold,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
 
warnings.filterwarnings("ignore", category=ConvergenceWarning)
 
RANDOM_STATE = 42
RESULTS_PATH = Path("output/ml_results.json")



def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df=df.dropna(subset=["Artist","Release_Year","PlayCount"]).copy()
    df["Release_Year"]=df["Release_Year"].astype(int)
    df["decade"]=(df["Release_Year"]//10)*10

    artist_stats=df.groupby("Artist").agg(
        artist_avg_plays=("PlayCount","mean")
        artist_num_songs=("PlayCount","count")
        artist_first_year=("Release_Year","min")

    ).reset_index()

    df=df.merge(artist_stats,on="Artist",how="left")
    df["career_year"]=df["Release_Year"]-df["artist_first_year"]
    df["log_plays"]=np.log1p(df["PlayCount"])
    return df

def _save_results(experiment_name: str, results: dict) -> None:
    
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if RESULTS_PATH.exists():
        try:
            existing = json.loads(RESULTS_PATH.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing[experiment_name] = results
    RESULTS_PATH.write_text(json.dumps(existing, indent=2, default=str))
    log.info("ML results saved → %s", RESULTS_PATH) # type: ignore

def _build_candidate_pipelines(
    candidate_names: list[str],
    task: str,
    random_state: int,
) -> dict:
    
    all_regression = {
        "linear":{
            "pipeline":Pipeline([
                ("scaler",StandardScaler()),
                ("model",LinearRegression())
            ]),
            "param_grid":{}
        },
        "ridge": {
            "pipeline":Pipeline([
                ("scalar":StandardScalar()),
                ("model":Ridge()),
            ]),
            "param_grid"={
                "model__alpha":{0.01,0.1,1.0,10.0,100.0}
            }
        },
        "gradient_boosting":{
            "pipline":Pipeline([
                ("scalar",StandardScalar()),
                ("model",GradientBoostingRegressor(Random_state=random_state)),
            ]),
            "param_grid"={
                "model__n_estimators":[50,100,200],
                "model__learning_rate":[0.05,0.1,0.2],
                "model__max_depth":[2,3,4],
            },
        },   
    }

    all_classification = {
        "logistic":{
            "pipeline": Pipeline([
                ("scalar",StandardScaler()),
                ("model",LogisticRegression(random_state=random_state,max_iter=1000)),
            ]),
            "param_grid":{
                "model__C":[0.01,0.1,1.0,10.0],
            },
        },

        "random_forest":{
            "pipeline":Pipeline([
                ("scalar",StandardScaler()),
                ("model",RandomForestClassifier(random_state=random_state)),
        ]),
        "param_grid":{
            "model__n_estimators":[50,100,200],
            "model__max_depth":[None,3,5],
            "model_min_samples_split":[2,5],
        },
        },
        "gradient_boodting":{
            "pipleine":Pipeline([
                ("scalar",StandardScaler()),
                ("model",GradientBoostingClassifier(random_state=random_state)),
            ]),
            "param_grid":{
                "model__n_estimators":[50,100],
                "model__learning_rate":[0.05,0.1,0.2],
                "model__max_depth":[2,3],
            },
        },
        
    }

