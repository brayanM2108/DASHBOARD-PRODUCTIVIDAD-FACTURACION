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


def resolve_document_to_name(billers_df, document_value, doc_column="DOCUMENTO", name_column="NOMBRE"):
    """Look up the name for a given document number in the billers master."""
    if billers_df is None or billers_df.empty:
        return str(document_value)
    if doc_column not in billers_df.columns or name_column not in billers_df.columns:
        return str(document_value)

    doc_str = str(document_value).strip()
    match = billers_df[billers_df[doc_column].astype(str).str.strip() == doc_str]
    if match.empty:
        return str(document_value)
    return str(match.iloc[0][name_column])


def filter_by_billers_document(
    df, billers_df,
    source_column="USUARIO_QUE_COMPLETA_RIPS",
    biller_doc_column="DOCUMENTO",
    biller_name_column="NOMBRE",
):
    """
    Filter a DataFrame to only include rows where source_column matches
    the DOCUMENTO column in the billers master. Enriches with
    NOMBRE_USUARIO (official name) and TIPO_USUARIO (ROL).
    Falls back to source_column value when no biller name is available.
    """
    if df is None or df.empty:
        return df

    if billers_df is None or billers_df.empty:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = result_df[source_column] if source_column in result_df.columns else None
        result_df["TIPO_USUARIO"] = None
        return result_df

    if source_column not in df.columns or biller_doc_column not in billers_df.columns:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = result_df[source_column] if source_column in result_df.columns else None
        result_df["TIPO_USUARIO"] = None
        return result_df

    valid_docs = set(
        billers_df[biller_doc_column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
    )

    if not valid_docs:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = result_df[source_column] if source_column in result_df.columns else None
        result_df["TIPO_USUARIO"] = None
        return result_df

    result_df = df.copy()
    result_df["_doc_norm"] = result_df[source_column].astype(str).str.strip().str.upper()
    result_df = result_df[result_df["_doc_norm"].isin(valid_docs)].copy()

    billers_map = (
        billers_df[[biller_doc_column, biller_name_column, "ROL"]]
        .dropna(subset=[biller_doc_column])
        .copy()
    )
    billers_map["_doc_key"] = billers_map[biller_doc_column].astype(str).str.strip().str.upper()
    billers_map = billers_map.drop_duplicates(subset=["_doc_key"])

    result_df = result_df.merge(
        billers_map[["_doc_key", biller_name_column, "ROL"]].rename(
            columns={biller_name_column: "NOMBRE_USUARIO", "ROL": "TIPO_USUARIO"}
        ),
        left_on="_doc_norm",
        right_on="_doc_key",
        how="left",
    ).drop(columns=["_doc_norm", "_doc_key"])

    if source_column in result_df.columns:
        result_df["NOMBRE_USUARIO"] = result_df["NOMBRE_USUARIO"].fillna(
            result_df[source_column].astype(str)
        )

    return result_df


def filter_by_billers_master(
    df, billers_df,
    document_column="USUARIO_QUE_LEGALIZO",
    biller_doc_column="DOCUMENTO",
    biller_name_column="NOMBRE",
):
    """
    Filter a DataFrame to only include rows where document_column matches
    billers_df[biller_doc_column]. Enriches with NOMBRE_USUARIO (official
    name) and TIPO_USUARIO (ROL) from billers master.
    """
    if df is None or df.empty:
        return df

    if billers_df is None or billers_df.empty:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = None
        result_df["TIPO_USUARIO"] = None
        return result_df

    if document_column not in df.columns or biller_doc_column not in billers_df.columns:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = None
        result_df["TIPO_USUARIO"] = None
        return result_df

    valid_docs = set(
        billers_df[biller_doc_column]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
    )

    if not valid_docs:
        result_df = df.copy()
        result_df["NOMBRE_USUARIO"] = None
        result_df["TIPO_USUARIO"] = None
        return result_df

    result_df = df.copy()
    result_df["_doc_norm"] = result_df[document_column].astype(str).str.strip().str.upper()
    result_df = result_df[result_df["_doc_norm"].isin(valid_docs)].copy()

    billers_map = (
        billers_df[[biller_doc_column, biller_name_column, "ROL"]]
        .dropna(subset=[biller_doc_column])
        .copy()
    )
    billers_map["_doc_key"] = billers_map[biller_doc_column].astype(str).str.strip().str.upper()
    billers_map = billers_map.drop_duplicates(subset=["_doc_key"])

    result_df = result_df.merge(
        billers_map[["_doc_key", biller_name_column, "ROL"]].rename(
            columns={biller_name_column: "NOMBRE_USUARIO", "ROL": "TIPO_USUARIO"}
        ),
        left_on="_doc_norm",
        right_on="_doc_key",
        how="left",
    ).drop(columns=["_doc_norm", "_doc_key"])

    return result_df
