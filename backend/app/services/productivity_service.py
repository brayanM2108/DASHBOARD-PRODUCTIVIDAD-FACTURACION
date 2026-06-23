"""Reusable productivity business service."""

import pandas as pd

from ..etl.aggregations.productivity import (
    aggregate_by_convenio,
    aggregate_by_eps,
    aggregate_records_by_date,
    aggregate_records_by_user,
    aggregate_values_by_date,
)
from ..etl.validators import find_first_column_variant
from ..utils.config.settings import COLUMN_NAMES, COLUMN_NAMES_BILLING, COLUMN_NAMES_LEGALIZATIONS, WORKING_HOURS_PER_DAY, SECONDS_PER_RECORD_BILLING

VALUE_COLUMN = "VALOR TERCERO"


class ProductivityService:
    """Centralizes productivity metric use cases across modules."""

    @staticmethod
    def empty_record_metrics(category: str | None = None) -> dict:
        result = {
            "total": 0,
            "by_user": [],
            "by_date": [],
            "daily_average": 0,
            "tiempo_total_horas": 0.0,
            "tiempo_promedio_diario_horas": 0.0,
        }
        if category is not None:
            result["category"] = category
        return result

    @staticmethod
    def calculate_record_productivity(
            df: pd.DataFrame,
            user_column_variants=None,
            date_column_variants=None,
            category: str | None = None,
            seconds_per_record: int | None = None,
    ) -> dict:
        """Calculate row-count productivity metrics by user and date."""

        if df is None or df.empty:
            return ProductivityService.empty_record_metrics(
                category=category
            )

        user_variants = (
                user_column_variants
                or COLUMN_NAMES["usuario"]
        )

        date_variants = (
                date_column_variants
                or COLUMN_NAMES["fecha"]
        )

        user_col = find_first_column_variant(
            df,
            user_variants,
        )

        date_col = find_first_column_variant(
            df,
            date_variants,
        )

        by_user_df = (
            aggregate_records_by_user(
                df,
                user_col,
                date_col,
                group_by_date=False,
            )
            if user_col
            else None
        )

        by_date_df = (
            aggregate_records_by_date(
                df,
                date_col,
            )
            if date_col
            else None
        )

        daily_average = 0.0

        if by_date_df is not None and not by_date_df.empty:

            daily_average = float(
                by_date_df["COUNT"].mean()
            )

        if by_user_df is not None:

            by_user_df = by_user_df.rename(
                columns={
                    "COUNT": "REGISTROS",
                }
            )

            if seconds_per_record:
                by_user_df["TIEMPO_HORAS"] = (
                    by_user_df["REGISTROS"] * seconds_per_record / 3600
                ).round(2)

            by_user = by_user_df.to_dict(
                orient="records"
            )

        else:

            by_user = []

        if by_date_df is not None:

            by_date_df = by_date_df.rename(
                columns={
                    "COUNT": "REGISTROS",
                }
            )

            if seconds_per_record:
                by_date_df["TIEMPO_HORAS"] = (
                    by_date_df["REGISTROS"] * seconds_per_record / 3600
                ).round(2)

            by_date_df["DATE"] = (
                by_date_df["DATE"]
                .astype(str)
            )

            by_date = by_date_df.to_dict(
                orient="records"
            )

        else:

            by_date = []

        total_records = len(df)

        tiempo_total_horas = 0.0
        tiempo_promedio_diario_horas = 0.0
        if seconds_per_record:
            tiempo_total_horas = round(total_records * seconds_per_record / 3600, 2)
            num_days = len(by_date_df) if by_date_df is not None and not by_date_df.empty else 0
            tiempo_promedio_diario_horas = round(tiempo_total_horas / num_days, 2) if num_days > 0 else 0.0

        result = {
            "total": total_records,
            "daily_average": daily_average,
            "by_user": by_user,
            "by_date": by_date,
            "tiempo_total_horas": tiempo_total_horas,
            "tiempo_promedio_diario_horas": tiempo_promedio_diario_horas,
        }

        if category is not None:
            result["category"] = category

        return result

    @staticmethod
    def calculate_legalizations_productivity(df: pd.DataFrame, category: str = "PPL", seconds_per_record: int | None = None) -> dict:
        """Calculate legalizations productivity preserving existing response shape."""
        return ProductivityService.calculate_record_productivity(
            df,
            user_column_variants=COLUMN_NAMES_LEGALIZATIONS["usuario"],
            date_column_variants=list(COLUMN_NAMES_LEGALIZATIONS["fecha"]) + ["FECHA REAL"],
            category=category,
            seconds_per_record=seconds_per_record,
        )

    @staticmethod
    def empty_billing_metrics() -> dict:
        return {
            "total": 0,
            "by_user": None,
            "by_date": None,
            "daily_average": 0,
            "total_records": 0,
            "total_valor_tercero": 0.0,
            "by_user_dual": None,
            "by_date_dual": None,
            "daily_avg_records": 0.0,
            "daily_avg_valor_tercero": 0.0,
        }

    @staticmethod
    def calculate_electronic_billing_productivity(df: pd.DataFrame) -> dict:
        """Calculate electronic billing productivity using shared aggregators."""
        if df is None or df.empty:
            return ProductivityService.empty_billing_metrics()

        user_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))
        date_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))
        if VALUE_COLUMN not in df.columns:
            return ProductivityService.empty_billing_metrics()

        total_records = int(len(df))
        total_valor = float(df[VALUE_COLUMN].sum())

        by_user_dual = None
        by_user_legacy = None
        if user_col:
            by_user_dual = aggregate_records_by_user(
                df, user_col, value_column=VALUE_COLUMN,
            )
            if by_user_dual is not None and not by_user_dual.empty:
                by_user_dual = by_user_dual.rename(columns={"COUNT": "REGISTROS"})
                by_user_dual = by_user_dual.sort_values("VALOR_TERCERO", ascending=False)
                by_user_legacy = (
                    by_user_dual[[user_col, "VALOR_TERCERO"]]
                    .rename(columns={"VALOR_TERCERO": "COUNT"})
                    .sort_values("COUNT", ascending=False)
                )

        by_date_dual = None
        by_date_legacy = None
        if date_col:
            by_date_dual = aggregate_values_by_date(df, date_col, VALUE_COLUMN)
            if by_date_dual is not None and not by_date_dual.empty:
                by_date_dual = by_date_dual.sort_values("DATE")
                by_date_legacy = (
                    by_date_dual[["DATE", "VALOR_TERCERO"]]
                    .rename(columns={"VALOR_TERCERO": "COUNT"})
                    .sort_values("DATE")
                )

        daily_avg_records = 0.0
        daily_avg_valor = 0.0
        if by_date_dual is not None and not by_date_dual.empty:
            daily_avg_records = float(by_date_dual["REGISTROS"].mean())
            daily_avg_valor = float(by_date_dual["VALOR_TERCERO"].mean())

        return {
            "total": total_valor,
            "by_user": by_user_legacy,
            "by_date": by_date_legacy,
            "daily_average": daily_avg_valor,
            "total_records": total_records,
            "total_valor_tercero": total_valor,
            "by_user_dual": by_user_dual,
            "by_date_dual": by_date_dual,
            "daily_avg_records": daily_avg_records,
            "daily_avg_valor_tercero": daily_avg_valor,
        }

    @staticmethod
    def calculate_billing_summary(df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {
                "total_records": 0,
                "total_valor_tercero": 0.0,
                "active_users": 0,
                "active_eps": 0,
                "active_convenios": 0,
                "average_ticket": 0.0,
                "daily_avg_records": 0.0,
                "daily_avg_valor_tercero": 0.0,
            }

        user_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))
        date_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))
        eps_col = find_first_column_variant(df, ["EPS"])
        convenio_col = find_first_column_variant(df, ["CONVENIO"])

        total_records = int(len(df))
        total_valor = float(df[VALUE_COLUMN].sum())

        active_users = int(df[user_col].nunique()) if user_col and user_col in df.columns else 0
        active_eps = int(df[eps_col].nunique()) if eps_col else 0
        active_convenios = int(df[convenio_col].nunique()) if convenio_col else 0

        average_ticket = total_valor / total_records if total_records > 0 else 0.0

        daily_avg_records = 0.0
        daily_avg_valor = 0.0
        if date_col and date_col in df.columns:
            by_date = aggregate_values_by_date(df, date_col, VALUE_COLUMN)
            if by_date is not None and not by_date.empty:
                daily_avg_records = float(by_date["REGISTROS"].mean())
                daily_avg_valor = float(by_date["VALOR_TERCERO"].mean())

        tiempo_total_horas = round(total_records * SECONDS_PER_RECORD_BILLING / 3600, 2)
        tiempo_promedio_diario_horas = round(daily_avg_records * SECONDS_PER_RECORD_BILLING / 3600, 2)

        return {
            "total_records": total_records,
            "total_valor_tercero": total_valor,
            "active_users": active_users,
            "active_eps": active_eps,
            "active_convenios": active_convenios,
            "average_ticket": round(average_ticket, 2),
            "daily_avg_records": round(daily_avg_records, 1),
            "daily_avg_valor_tercero": round(daily_avg_valor, 2),
            "tiempo_total_horas": tiempo_total_horas,
            "tiempo_promedio_diario_horas": tiempo_promedio_diario_horas,
        }

    @staticmethod
    def calculate_billing_analytics(df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {
                "user_distribution": [],
                "daily_trend": [],
                "eps_distribution": [],
                "convenio_distribution": [],
                "rankings": {"top_records": [], "top_valor": []},
            }

        user_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("usuario", []))
        date_col = find_first_column_variant(df, COLUMN_NAMES_BILLING.get("fecha", []))
        eps_col = find_first_column_variant(df, ["EPS"])
        convenio_col = find_first_column_variant(df, ["CONVENIO"])

        total_records = len(df)
        total_valor = float(df[VALUE_COLUMN].sum())

        user_distribution = []
        if user_col and user_col in df.columns:
            by_user = aggregate_records_by_user(df, user_col, value_column=VALUE_COLUMN)
            if by_user is not None and not by_user.empty:
                by_user = by_user.rename(columns={"COUNT": "REGISTROS"})
                by_user["ticket_promedio"] = (
                    by_user["VALOR_TERCERO"] / by_user["REGISTROS"]
                ).round(2)
                by_user["participacion_records"] = (
                    by_user["REGISTROS"] / total_records * 100
                ).round(1)
                by_user["participacion_valor"] = (
                    by_user["VALOR_TERCERO"] / total_valor * 100
                ).round(1) if total_valor > 0 else 0.0
                by_user = by_user.sort_values("VALOR_TERCERO", ascending=False)
                by_user = by_user.rename(columns={user_col: "usuario"})
                by_user["records"] = by_user["REGISTROS"].astype(int)
                by_user["valor"] = by_user["VALOR_TERCERO"].round(2)
                user_distribution = by_user[
                    ["usuario", "records", "valor", "ticket_promedio", "participacion_records", "participacion_valor"]
                ].to_dict(orient="records")

        daily_trend = []
        if date_col and date_col in df.columns:
            by_date = aggregate_values_by_date(df, date_col, VALUE_COLUMN)
            if by_date is not None and not by_date.empty:
                by_date = by_date.sort_values("DATE")
                by_date["DATE"] = by_date["DATE"].astype(str)
                by_date["ticket_promedio"] = (
                    by_date["VALOR_TERCERO"] / by_date["REGISTROS"]
                ).round(2)
                daily_trend = by_date.rename(columns={
                    "DATE": "date", "REGISTROS": "records", "VALOR_TERCERO": "valor"
                })[["date", "records", "valor", "ticket_promedio"]].to_dict(orient="records")

        eps_distribution = []
        if eps_col and eps_col in df.columns:
            by_eps = aggregate_by_eps(df, eps_col, VALUE_COLUMN)
            if by_eps is not None and not by_eps.empty:
                by_eps = by_eps.rename(columns={eps_col: "eps", "REGISTROS": "records", "VALOR_TERCERO": "valor"})
                by_eps["valor"] = by_eps["valor"].round(2)
                eps_distribution = by_eps[["eps", "records", "valor"]].to_dict(orient="records")

        convenio_distribution = []
        if convenio_col and convenio_col in df.columns:
            by_convenio = aggregate_by_convenio(df, convenio_col, VALUE_COLUMN)
            if by_convenio is not None and not by_convenio.empty:
                by_convenio = by_convenio.rename(columns={convenio_col: "convenio", "REGISTROS": "records", "VALOR_TERCERO": "valor"})
                by_convenio["valor"] = by_convenio["valor"].round(2)
                convenio_distribution = by_convenio[["convenio", "records", "valor"]].to_dict(orient="records")

        top_records = []
        top_valor = []
        if user_distribution:
            sorted_by_records = sorted(user_distribution, key=lambda x: x["records"], reverse=True)
            top_records = [{"usuario": u["usuario"], "records": u["records"]} for u in sorted_by_records[:5]]
            sorted_by_valor = sorted(user_distribution, key=lambda x: x["valor"], reverse=True)
            top_valor = [{"usuario": u["usuario"], "valor": u["valor"]} for u in sorted_by_valor[:5]]

        return {
            "user_distribution": user_distribution,
            "daily_trend": daily_trend,
            "eps_distribution": eps_distribution,
            "convenio_distribution": convenio_distribution,
            "rankings": {
                "top_records": top_records,
                "top_valor": top_valor,
            },
        }

    @staticmethod
    def generate_billing_insights(analytics: dict, total_records: int, total_valor: float) -> list[dict]:
        insights = []
        user_dist = analytics.get("user_distribution", [])
        daily_trend = analytics.get("daily_trend", [])
        eps_dist = analytics.get("eps_distribution", [])

        if user_dist:
            top_user_records = max(user_dist, key=lambda u: u["records"])
            insights.append({
                "type": "success",
                "title": "Mayor productividad",
                "description": f"{top_user_records['usuario']} registr\u00f3 {top_user_records['records']:,} facturas.",
            })

            top_user_valor = max(user_dist, key=lambda u: u["valor"])
            insights.append({
                "type": "info",
                "title": "Mayor valor facturado",
                "description": f"{top_user_valor['usuario']} factur\u00f3 ${top_user_valor['valor']:,.0f}.",
            })

            top5_records = sum(u["records"] for u in sorted(user_dist, key=lambda u: u["records"], reverse=True)[:5])
            top5_pct = (top5_records / total_records * 100) if total_records > 0 else 0
            insights.append({
                "type": "info",
                "title": "Top 5",
                "description": f"El Top 5 representa el {top5_pct:.0f}% del total de registros.",
            })

        if daily_trend:
            best_day = max(daily_trend, key=lambda d: d["records"])
            insights.append({
                "type": "success",
                "title": "Mejor d\u00eda",
                "description": f"{best_day['date']} fue el d\u00eda con mayor facturaci\u00f3n ({best_day['records']:,} registros).",
            })

        if eps_dist:
            top_eps = max(eps_dist, key=lambda e: e["records"])
            insights.append({
                "type": "info",
                "title": "EPS principal",
                "description": f"{top_eps['eps']} concentra {top_eps['records']:,} registros.",
            })

        avg_ticket = total_valor / total_records if total_records > 0 else 0
        insights.append({
            "type": "info",
            "title": "Ticket promedio",
            "description": f"El ticket promedio es de ${avg_ticket:,.0f} por factura.",
        })

        return insights
