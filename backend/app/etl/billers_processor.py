"""
ETL - Billers
=============
DataFrame extraction and lookup helpers for billers master data.
"""

USER_LOOKUP_COLUMNS = "NOMBRE"


def normalize_text(value):
    """Normalize text values for robust comparisons."""
    return str(value).strip().upper()


def extract_unique_users_from_dataframes(dataframes):
    """Collect unique users from provided dataframes."""
    users = set()

    for df in dataframes:
        if df is None or df.empty:
            continue

        selected_col = USER_LOOKUP_COLUMNS if USER_LOOKUP_COLUMNS in df.columns else None
        if selected_col is None:
            continue

        normalized_values = (
            df[selected_col]
            .dropna()
            .astype(str)
            .map(normalize_text)
            .tolist()
        )
        users.update(normalized_values)

    return sorted(users)


def extract_unique_users_from_master(billers_df):
    """Collect unique users directly from billers master dataframe."""
    if billers_df is None or billers_df.empty:
        return []

    selected_col = USER_LOOKUP_COLUMNS if USER_LOOKUP_COLUMNS in billers_df.columns else None
    if selected_col is None:
        return []

    return sorted(
        billers_df[selected_col]
        .dropna()
        .astype(str)
        .map(normalize_text)
        .unique()
        .tolist()
    )


def find_biller_info(user, billers_df):
    """Return first matching biller row as dict."""
    if user is None or billers_df is None or billers_df.empty:
        return None

    lookup_col = USER_LOOKUP_COLUMNS if USER_LOOKUP_COLUMNS in billers_df.columns else None
    if lookup_col is None:
        return None

    user_norm = normalize_text(user)
    matches = billers_df[
        billers_df[lookup_col].astype(str).map(normalize_text) == user_norm
    ]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def filter_by_billers_master(df, billers_df, user_column="USUARIO", biller_name_column="NOMBRE"):
    """
    Filter a DataFrame to only include rows where the user column matches
    a biller name in the billers master.
    """
    if df is None or df.empty:
        return df
    if billers_df is None or billers_df.empty:
        return df
    if user_column not in df.columns or biller_name_column not in billers_df.columns:
        return df

    valid_names = set(
        billers_df[biller_name_column]
        .dropna()
        .astype(str)
        .map(normalize_text)
        .unique()
    )

    if not valid_names:
        return df

    result_df = df.copy()
    result_df[user_column] = result_df[user_column].astype(str).map(normalize_text)

    return result_df[result_df[user_column].isin(valid_names)].copy()
