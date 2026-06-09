"""
Business use cases - Billers
============================
Orchestrates biller-related use cases. DataFrame transformations live in ETL.
"""

from ..etl.billers_processor import (
    extract_unique_users_from_dataframes,
    extract_unique_users_from_master,
    find_biller_info,
)
from ..etl.loaders import load_billers_master

DEFAULT_SESSION_DATASET_KEYS = (
    "legalizations_df",
    "billing_df",
)


def get_billers_list(billers_df=None, dataframes=None, session_state=None):
    """
    Return available billers list.
    """
    if dataframes is not None:
        return extract_unique_users_from_dataframes(dataframes)

    if billers_df is not None:
        return extract_unique_users_from_master(billers_df)

    if session_state is not None:
        dataset_frames = [session_state.get(key) for key in DEFAULT_SESSION_DATASET_KEYS]
        return extract_unique_users_from_dataframes(dataset_frames)

    return []


def get_biller_info(user, billers_df=None):
    """
    Return detailed biller information by user name/identifier.
    """
    if user is None:
        return None

    if billers_df is None:
        billers_df = load_billers_master()

    return find_biller_info(user, billers_df)
