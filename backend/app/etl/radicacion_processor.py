import pandas as pd

from ..utils.config.settings import COLUMN_NAMES_RADICACION, RADICACION_DAYS_THRESHOLD
from .utils.dataframe_helpers import normalize_column_names


def _find_column(df: pd.DataFrame, variants_key: str) -> str | None:
    variants = COLUMN_NAMES_RADICACION.get(variants_key, [])
    for v in variants:
        if v in df.columns:
            return v
    return None


def _has_numeric_value(val) -> bool:
    try:
        x = float(val)
        return not pd.isna(x)
    except (ValueError, TypeError):
        return False


def prepare_radicacion_df(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None

    result_df = normalize_column_names(df)

    factura_col = _find_column(result_df, "factura")
    if factura_col is None:
        return None

    user_col = _find_column(result_df, "usuario")
    fecha_col = _find_column(result_df, "fecha")
    rad_panacea = _find_column(result_df, "radicado_panacea")
    rad_externo = _find_column(result_df, "radicado_externo")

    if user_col and user_col in result_df.columns:
        result_df[user_col] = result_df[user_col].astype(str).str.strip()
        result_df = result_df[result_df[user_col].notna() & (result_df[user_col] != "")]
    else:
        return None

    if fecha_col:
        result_df[fecha_col] = pd.to_datetime(result_df[fecha_col], errors="coerce")
        result_df = result_df.dropna(subset=[fecha_col])

    result_df = result_df.drop_duplicates(subset=[factura_col])

    result_df["RADICADO"] = False
    if rad_panacea and rad_panacea in result_df.columns:
        result_df["RADICADO"] = result_df["RADICADO"] | result_df[rad_panacea].apply(_has_numeric_value)
    if rad_externo and rad_externo in result_df.columns:
        result_df["RADICADO"] = result_df["RADICADO"] | result_df[rad_externo].apply(_has_numeric_value)

    today = pd.Timestamp.now().normalize()
    days_since_invoice = (today - result_df[fecha_col]).dt.days if fecha_col else pd.Series([0] * len(result_df))
    result_df["DIAS_SIN_RADICAR"] = days_since_invoice
    result_df["VENCIDA"] = (~result_df["RADICADO"]) & (days_since_invoice > RADICACION_DAYS_THRESHOLD)

    return result_df
