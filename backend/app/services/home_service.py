"""
Home Service - Business logic for dashboard home
"""

from datetime import date, timedelta
import pandas as pd

from ..repositories.parquet_repository import ParquetRepository
from ..repositories.administrative_process_repository import AdministrativeProcessRepository
from ..repositories.user_repository import UserRepository
from .productivity_service import ProductivityService
from ..etl.billing_electronic_processor import prepare_electronic_billing_df, VALUE_COLUMN
from ..etl.radicacion_processor import prepare_radicacion_df
from ..etl.transformers.legalizations_transformer import prepare_legalizations_dataframe
from ..etl.transformers.rips_transformer import prepare_rips_dataframe
from ..etl.validators import find_first_column_variant
from ..utils.config.settings import (
    COLUMN_NAMES_BILLING,
    COLUMN_NAMES_LEGALIZATIONS,
    COLUMN_NAMES_RIPS,
    SECONDS_PER_RECORD_BILLING,
    SECONDS_PER_RECORD_RIPS,
    SECONDS_PER_RECORD_LEGALIZATIONS,
)
from ..api.schemas.home import (
    HomeAdminResponse,
    HomeAdminKpis,
    HomeAdminModuleCount,
    HomeAdminTrendPoint,
    HomeAdminTopUser,
    HomeAdminModuleCompliance,
    HomeAdminAlert,
    HomeAdminInsight,
    HomeUserResponse,
    HomeUserKpis,
    HomeUserModuleCount,
    HomeUserTrendPoint,
    HomeUserPendiente,
    HomeUserAlert,
    HomeUserInsight,
)


class HomeService:
    def __init__(
        self,
        legalizations_repo: ParquetRepository,
        billing_repo: ParquetRepository,
        rips_repo: ParquetRepository,
        processes_repo: AdministrativeProcessRepository,
        user_repo: UserRepository,
        productivity_service: ProductivityService,
    ):
        self.legalizations_repo = legalizations_repo
        self.billing_repo = billing_repo
        self.rips_repo = rips_repo
        self.processes_repo = processes_repo
        self.user_repo = user_repo
        self.productivity_service = productivity_service

    def _load_and_prepare_data(
        self,
        start_date: date,
        end_date: date,
        filter_user: str | None = None,
    ) -> dict:
        """Carga y prepara todos los dataframes filtrados por fecha y usuario."""
        data = {}

        # Legalizaciones
        try:
            leg_df = self.legalizations_repo.load()
            if leg_df is not None and not leg_df.empty:
                leg_df = prepare_legalizations_dataframe(leg_df)
                if leg_df is not None:
                    date_col = find_first_column_variant(leg_df, ["FECHA REAL", "FECHA_REAL"])
                    if date_col:
                        leg_df[date_col] = pd.to_datetime(leg_df[date_col], errors="coerce")
                        leg_df = leg_df[
                            (leg_df[date_col].dt.date >= start_date)
                            & (leg_df[date_col].dt.date <= end_date)
                        ]
                    if filter_user:
                        user_col = find_first_column_variant(leg_df, COLUMN_NAMES_LEGALIZATIONS.get("usuario", ["USUARIO"]))
                        if user_col:
                            leg_df = leg_df[leg_df[user_col].astype(str).str.strip().str.upper() == filter_user.upper()]
                    data["legalizations"] = leg_df
                else:
                    data["legalizations"] = pd.DataFrame()
            else:
                data["legalizations"] = pd.DataFrame()
        except Exception:
            data["legalizations"] = pd.DataFrame()

        # Billing
        try:
            bill_df = self.billing_repo.load()
            if bill_df is not None and not bill_df.empty:
                bill_df = prepare_electronic_billing_df(bill_df)
                if bill_df is not None:
                    date_col = find_first_column_variant(bill_df, COLUMN_NAMES_BILLING.get("fecha", ["FECHA FACTURA"]))
                    if date_col:
                        bill_df[date_col] = pd.to_datetime(bill_df[date_col], errors="coerce")
                        bill_df = bill_df[
                            (bill_df[date_col].dt.date >= start_date)
                            & (bill_df[date_col].dt.date <= end_date)
                        ]
                    if filter_user:
                        user_col = find_first_column_variant(bill_df, COLUMN_NAMES_BILLING.get("usuario", ["USUARIO"]))
                        if user_col:
                            bill_df = bill_df[bill_df[user_col].astype(str).str.strip().str.upper() == filter_user.upper()]
                    data["billing"] = bill_df
                else:
                    data["billing"] = pd.DataFrame()
            else:
                data["billing"] = pd.DataFrame()
        except Exception:
            data["billing"] = pd.DataFrame()

        # RIPS
        try:
            rips_df = self.rips_repo.load()
            if rips_df is not None and not rips_df.empty:
                rips_df = prepare_rips_dataframe(rips_df)
                if rips_df is not None:
                    date_col = find_first_column_variant(rips_df, COLUMN_NAMES_RIPS.get("fecha", ["FECHA_COMPLETADO_RIPS"]))
                    if date_col:
                        rips_df[date_col] = pd.to_datetime(rips_df[date_col], errors="coerce")
                        rips_df = rips_df[
                            (rips_df[date_col].dt.date >= start_date)
                            & (rips_df[date_col].dt.date <= end_date)
                        ]
                    if filter_user:
                        user_col = "NOMBRE_USUARIO" if "NOMBRE_USUARIO" in rips_df.columns else find_first_column_variant(rips_df, COLUMN_NAMES_RIPS.get("documento", ["USUARIO_QUE_COMPLETA_RIPS"]))
                        if user_col:
                            rips_df = rips_df[rips_df[user_col].astype(str).str.strip().str.upper() == filter_user.upper()]
                    data["rips"] = rips_df
                else:
                    data["rips"] = pd.DataFrame()
            else:
                data["rips"] = pd.DataFrame()
        except Exception:
            data["rips"] = pd.DataFrame()

        # Procesos administrativos
        try:
            user_id = None
            if filter_user:
                user = self.user_repo.get_by_username(filter_user)
                if user:
                    user_id = user.id
            
            processes = self.processes_repo.list(
                fecha_desde=start_date,
                fecha_hasta=end_date,
                usuario_id=user_id,
            )
            if processes:
                proc_data = [
                    {
                        "FECHA": p.fecha,
                        "NOMBRE": p.nombre,
                        "PROCESO": p.proceso,
                        "CANTIDAD": p.cantidad,
                    }
                    for p in processes
                ]
                data["processes"] = pd.DataFrame(proc_data)
            else:
                data["processes"] = pd.DataFrame()
        except Exception:
            data["processes"] = pd.DataFrame()

        return data

    def _count_records(self, df: pd.DataFrame) -> int:
        return len(df) if df is not None and not df.empty else 0

    def _count_today(self, df: pd.DataFrame, date_col_variants: list[str]) -> int:
        if df is None or df.empty:
            return 0
        date_col = find_first_column_variant(df, date_col_variants)
        if not date_col:
            return 0
        try:
            today = date.today()
            dates = pd.to_datetime(df[date_col], errors="coerce").dt.date
            return int((dates == today).sum())
        except Exception:
            return 0

    def _get_unique_users(self, df: pd.DataFrame, user_col_variants: list[str]) -> int:
        if df is None or df.empty:
            return 0
        user_col = find_first_column_variant(df, user_col_variants)
        if not user_col:
            return 0
        try:
            return int(df[user_col].dropna().astype(str).str.strip().nunique())
        except Exception:
            return 0

    def _sum_valor_tercero(self, df: pd.DataFrame) -> float:
        if df is None or df.empty:
            return 0.0
        if VALUE_COLUMN in df.columns:
            try:
                return float(pd.to_numeric(df[VALUE_COLUMN], errors="coerce").sum())
            except Exception:
                return 0.0
        return 0.0

    def _compute_compliance(self, total_records: int, start_date: date, end_date: date) -> float:
        """Calcula % de cumplimiento basado en actividad diaria vs promedio esperado."""
        if total_records == 0:
            return 0.0
        
        days = (end_date - start_date).days + 1
        if days <= 0:
            return 0.0
        
        # Promedio diario esperado (asumiendo 5 días hábiles por semana)
        working_days = int(days * 5 / 7)
        if working_days == 0:
            return 0.0
        
        daily_avg_expected = total_records / working_days
        
        # Registros de hoy
        today = date.today()
        # Nota: esto es simplificado, en producción se debería calcular con datos reales
        daily_avg_actual = total_records / days if days > 0 else 0
        
        compliance = (daily_avg_actual / daily_avg_expected * 100) if daily_avg_expected > 0 else 0
        return min(max(compliance, 0), 100)

    def _compute_daily_trend_admin(
        self,
        data: dict,
        start_date: date,
        end_date: date,
    ) -> list[HomeAdminTrendPoint]:
        """Calcula tendencia diaria para admin (últimos 7 días)."""
        today = date.today()
        trend_days = 7
        trend = []

        for i in range(trend_days - 1, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")

            leg_count = 0
            bill_count = 0
            rips_count = 0
            proc_count = 0

            # Legalizaciones
            leg_df = data.get("legalizations")
            if leg_df is not None and not leg_df.empty:
                date_col = find_first_column_variant(leg_df, ["FECHA REAL", "FECHA_REAL"])
                if date_col:
                    dates = pd.to_datetime(leg_df[date_col], errors="coerce").dt.date
                    leg_count = int((dates == day).sum())

            # Billing
            bill_df = data.get("billing")
            if bill_df is not None and not bill_df.empty:
                date_col = find_first_column_variant(bill_df, COLUMN_NAMES_BILLING.get("fecha", ["FECHA FACTURA"]))
                if date_col:
                    dates = pd.to_datetime(bill_df[date_col], errors="coerce").dt.date
                    bill_count = int((dates == day).sum())

            # RIPS
            rips_df = data.get("rips")
            if rips_df is not None and not rips_df.empty:
                date_col = find_first_column_variant(rips_df, COLUMN_NAMES_RIPS.get("fecha", ["FECHA_COMPLETADO_RIPS"]))
                if date_col:
                    dates = pd.to_datetime(rips_df[date_col], errors="coerce").dt.date
                    rips_count = int((dates == day).sum())

            # Procesos
            proc_df = data.get("processes")
            if proc_df is not None and not proc_df.empty:
                if "FECHA" in proc_df.columns:
                    dates = pd.to_datetime(proc_df["FECHA"], errors="coerce").dt.date
                    proc_count = int((dates == day).sum())

            trend.append(
                HomeAdminTrendPoint(
                    fecha=day_str,
                    legalizaciones=leg_count,
                    facturacion=bill_count,
                    rips=rips_count,
                    radicacion=bill_count,  # Radicación usa los mismos datos de billing
                    procesos=proc_count,
                )
            )

        return trend

    def _compute_top_users(self, data: dict, top_n: int = 5) -> list[HomeAdminTopUser]:
        """Calcula top N usuarios por registros totales."""
        user_counts = {}

        # Legalizaciones
        leg_df = data.get("legalizations")
        if leg_df is not None and not leg_df.empty:
            user_col = find_first_column_variant(leg_df, COLUMN_NAMES_LEGALIZATIONS.get("usuario", ["USUARIO"]))
            if user_col:
                counts = leg_df[user_col].value_counts().to_dict()
                for user, count in counts.items():
                    user_counts[user] = user_counts.get(user, 0) + count

        # Billing
        bill_df = data.get("billing")
        if bill_df is not None and not bill_df.empty:
            user_col = find_first_column_variant(bill_df, COLUMN_NAMES_BILLING.get("usuario", ["USUARIO"]))
            if user_col:
                counts = bill_df[user_col].value_counts().to_dict()
                for user, count in counts.items():
                    user_counts[user] = user_counts.get(user, 0) + count

        # RIPS
        rips_df = data.get("rips")
        if rips_df is not None and not rips_df.empty:
            user_col = "NOMBRE_USUARIO" if "NOMBRE_USUARIO" in rips_df.columns else find_first_column_variant(rips_df, COLUMN_NAMES_RIPS.get("documento", ["USUARIO_QUE_COMPLETA_RIPS"]))
            if user_col:
                counts = rips_df[user_col].value_counts().to_dict()
                for user, count in counts.items():
                    user_counts[user] = user_counts.get(user, 0) + count

        # Procesos
        proc_df = data.get("processes")
        if proc_df is not None and not proc_df.empty:
            if "NOMBRE" in proc_df.columns:
                counts = proc_df["NOMBRE"].value_counts().to_dict()
                for user, count in counts.items():
                    user_counts[user] = user_counts.get(user, 0) + count

        # Ordenar y tomar top N
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [HomeAdminTopUser(usuario=user, registros=count) for user, count in sorted_users]

    def _compute_module_compliance(self, data: dict) -> list[HomeAdminModuleCompliance]:
        """Calcula % de cumplimiento por módulo."""
        modules = []
        
        total = sum([
            self._count_records(data.get("legalizations")),
            self._count_records(data.get("billing")),
            self._count_records(data.get("rips")),
            self._count_records(data.get("processes")),
        ])

        if total == 0:
            return [
                HomeAdminModuleCompliance(modulo="Legalizaciones", porcentaje=0),
                HomeAdminModuleCompliance(modulo="Facturación", porcentaje=0),
                HomeAdminModuleCompliance(modulo="RIPS", porcentaje=0),
                HomeAdminModuleCompliance(modulo="Radicación", porcentaje=0),
                HomeAdminModuleCompliance(modulo="Procesos", porcentaje=0),
            ]

        leg_pct = (self._count_records(data.get("legalizations")) / total * 100 * 5) if total > 0 else 0
        bill_pct = (self._count_records(data.get("billing")) / total * 100 * 5) if total > 0 else 0
        rips_pct = (self._count_records(data.get("rips")) / total * 100 * 5) if total > 0 else 0
        proc_pct = (self._count_records(data.get("processes")) / total * 100 * 5) if total > 0 else 0

        modules.append(HomeAdminModuleCompliance(modulo="Legalizaciones", porcentaje=min(leg_pct, 100)))
        modules.append(HomeAdminModuleCompliance(modulo="Facturación", porcentaje=min(bill_pct, 100)))
        modules.append(HomeAdminModuleCompliance(modulo="RIPS", porcentaje=min(rips_pct, 100)))
        modules.append(HomeAdminModuleCompliance(modulo="Radicación", porcentaje=min(bill_pct, 100)))
        modules.append(HomeAdminModuleCompliance(modulo="Procesos", porcentaje=min(proc_pct, 100)))

        return modules

    def _detect_admin_alerts(self, data: dict) -> list[HomeAdminAlert]:
        """Detecta alertas críticas para admin."""
        alerts = []

        # Facturas sin radicar >5 días
        bill_df = data.get("billing")
        if bill_df is not None and not bill_df.empty:
            try:
                bill_df = prepare_radicacion_df(bill_df)
                if bill_df is not None and "VENCIDA" in bill_df.columns:
                    vencidas = int(bill_df["VENCIDA"].sum())
                    if vencidas > 0:
                        alerts.append(
                            HomeAdminAlert(
                                icon="🔴",
                                text=f"{vencidas} facturas vencidas sin radicar",
                                severity="critical",
                            )
                        )
            except Exception:
                pass

        # Módulos sin datos
        if data.get("legalizations") is None or data.get("legalizations").empty:
            alerts.append(
                HomeAdminAlert(
                    icon="🟠",
                    text="Módulo de Legalizaciones sin datos",
                    severity="warning",
                )
            )

        if data.get("rips") is None or data.get("rips").empty:
            alerts.append(
                HomeAdminAlert(
                    icon="🟠",
                    text="Módulo de RIPS sin datos",
                    severity="warning",
                )
            )

        return alerts

    def _generate_admin_insights(self, data: dict, kpis: HomeAdminKpis) -> list[HomeAdminInsight]:
        """Genera 4-5 insights para admin."""
        insights = []

        # Módulo con mayor volumen
        module_counts = {
            "Legalizaciones": self._count_records(data.get("legalizations")),
            "Facturación": self._count_records(data.get("billing")),
            "RIPS": self._count_records(data.get("rips")),
            "Procesos": self._count_records(data.get("processes")),
        }
        
        if module_counts:
            top_module = max(module_counts, key=module_counts.get)
            top_count = module_counts[top_module]
            total = sum(module_counts.values())
            pct = (top_count / total * 100) if total > 0 else 0
            insights.append(
                HomeAdminInsight(
                    text=f"{top_module} representa el {pct:.0f}% del total procesado"
                )
            )

        # Usuario más productivo
        top_users = self._compute_top_users(data, top_n=1)
        if top_users:
            insights.append(
                HomeAdminInsight(
                    text=f"{top_users[0].usuario} fue el usuario más productivo con {top_users[0].registros} registros"
                )
            )

        # Cumplimiento
        if kpis.compliance >= 80:
            insights.append(
                HomeAdminInsight(
                    text=f"Cumplimiento global en {kpis.compliance:.0f}% - meta dentro del rango"
                )
            )
        elif kpis.compliance >= 60:
            insights.append(
                HomeAdminInsight(
                    text=f"Cumplimiento global en {kpis.compliance:.0f}% - requiere atención"
                )
            )
        else:
            insights.append(
                HomeAdminInsight(
                    text=f"Cumplimiento global en {kpis.compliance:.0f}% - crítico"
                )
            )

        # Usuarios activos
        if kpis.active_users > 0:
            insights.append(
                HomeAdminInsight(
                    text=f"{kpis.active_users} usuarios activos en el periodo"
                )
            )

        return insights[:5]

    def get_admin_summary(
        self,
        start_date: date,
        end_date: date,
        filter_user: str | None = None,
    ) -> HomeAdminResponse:
        """Retorna resumen completo para dashboard admin."""
        data = self._load_and_prepare_data(start_date, end_date, filter_user)

        # KPIs
        total_records = (
            self._count_records(data.get("legalizations"))
            + self._count_records(data.get("billing"))
            + self._count_records(data.get("rips"))
            + self._count_records(data.get("processes"))
        )

        records_today = (
            self._count_today(data.get("legalizations"), ["FECHA REAL", "FECHA_REAL"])
            + self._count_today(data.get("billing"), COLUMN_NAMES_BILLING.get("fecha", ["FECHA FACTURA"]))
            + self._count_today(data.get("rips"), COLUMN_NAMES_RIPS.get("fecha", ["FECHA_COMPLETADO_RIPS"]))
            + self._count_today(data.get("processes"), ["FECHA"])
        )

        active_users = max([
            self._get_unique_users(data.get("legalizations"), COLUMN_NAMES_LEGALIZATIONS.get("usuario", ["USUARIO"])),
            self._get_unique_users(data.get("billing"), COLUMN_NAMES_BILLING.get("usuario", ["USUARIO"])),
            self._get_unique_users(data.get("rips"), ["NOMBRE_USUARIO"]),
            self._get_unique_users(data.get("processes"), ["NOMBRE"]),
        ])

        total_valor = self._sum_valor_tercero(data.get("billing"))
        compliance = self._compute_compliance(total_records, start_date, end_date)

        kpis = HomeAdminKpis(
            total_records=total_records,
            records_today=records_today,
            active_users=active_users,
            total_valor_tercero=total_valor,
            compliance=compliance,
        )

        # Module counts
        modules = HomeAdminModuleCount(
            legalizaciones=self._count_records(data.get("legalizations")),
            facturacion=self._count_records(data.get("billing")),
            rips=self._count_records(data.get("rips")),
            radicacion=self._count_records(data.get("billing")),
            procesos=self._count_records(data.get("processes")),
        )

        # Trend
        trend = self._compute_daily_trend_admin(data, start_date, end_date)

        # Top users
        top_users = self._compute_top_users(data, top_n=5)

        # Module compliance
        module_compliance = self._compute_module_compliance(data)

        # Alerts
        alerts = self._detect_admin_alerts(data)

        # Insights
        insights = self._generate_admin_insights(data, kpis)

        return HomeAdminResponse(
            kpis=kpis,
            modules=modules,
            trend=trend,
            top_users=top_users,
            module_compliance=module_compliance,
            alerts=alerts,
            insights=insights,
        )

    def get_user_summary(
        self,
        biller_name: str,
        start_date: date,
        end_date: date,
    ) -> HomeUserResponse:
        """Retorna resumen completo para dashboard de facturador."""
        data = self._load_and_prepare_data(start_date, end_date, filter_user=biller_name)

        # KPIs
        registros_hoy = (
            self._count_today(data.get("legalizations"), ["FECHA REAL", "FECHA_REAL"])
            + self._count_today(data.get("billing"), COLUMN_NAMES_BILLING.get("fecha", ["FECHA FACTURA"]))
            + self._count_today(data.get("rips"), COLUMN_NAMES_RIPS.get("fecha", ["FECHA_COMPLETADO_RIPS"]))
            + self._count_today(data.get("processes"), ["FECHA"])
        )

        # Radicaciones pendientes (facturas sin radicar >2 días)
        radicaciones_pendientes = 0
        bill_df = data.get("billing")
        if bill_df is not None and not bill_df.empty:
            try:
                bill_df = prepare_radicacion_df(bill_df)
                if bill_df is not None and "VENCIDA" in bill_df.columns:
                    radicaciones_pendientes = int(bill_df["VENCIDA"].sum())
            except Exception:
                pass

        # Horas productivas
        leg_count = self._count_records(data.get("legalizations"))
        bill_count = self._count_records(data.get("billing"))
        rips_count = self._count_records(data.get("rips"))
        proc_count = self._count_records(data.get("processes"))

        total_seconds = (
            leg_count * SECONDS_PER_RECORD_LEGALIZATIONS
            + bill_count * SECONDS_PER_RECORD_BILLING
            + rips_count * SECONDS_PER_RECORD_RIPS
            + proc_count * 60  # Estimado 60s por proceso
        )
        horas_productivas = round(total_seconds / 3600, 1)

        kpis = HomeUserKpis(
            registros_hoy=registros_hoy,
            radicaciones_pendientes=radicaciones_pendientes,
            horas_productivas=horas_productivas,
        )

        # Module counts
        valor_facturado = self._sum_valor_tercero(data.get("billing"))
        modules = HomeUserModuleCount(
            legalizaciones=leg_count,
            facturacion=bill_count,
            rips=rips_count,
            radicacion=bill_count,
            procesos=proc_count,
            valor_facturado=valor_facturado,
        )

        # Trend semanal
        today = date.today()
        trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_count = 0

            for df_key in ["legalizations", "billing", "rips", "processes"]:
                df = data.get(df_key)
                if df is not None and not df.empty:
                    date_col_variants = {
                        "legalizations": ["FECHA REAL", "FECHA_REAL"],
                        "billing": COLUMN_NAMES_BILLING.get("fecha", ["FECHA FACTURA"]),
                        "rips": COLUMN_NAMES_RIPS.get("fecha", ["FECHA_COMPLETADO_RIPS"]),
                        "processes": ["FECHA"],
                    }
                    date_col = find_first_column_variant(df, date_col_variants[df_key])
                    if date_col:
                        try:
                            dates = pd.to_datetime(df[date_col], errors="coerce").dt.date
                            day_count += int((dates == day).sum())
                        except Exception:
                            pass

            trend.append(HomeUserTrendPoint(fecha=day_str, registros=day_count))

        # Pendientes
        pendientes = []
        if radicaciones_pendientes > 0:
            pendientes.append(
                HomeUserPendiente(
                    icon="🔴",
                    text=f"{radicaciones_pendientes} facturas vencidas sin radicar",
                    count=radicaciones_pendientes,
                )
            )
        if proc_count > 0:
            pendientes.append(
                HomeUserPendiente(
                    icon="🟠",
                    text=f"{proc_count} procesos administrativos activos",
                    count=proc_count,
                )
            )
        if not pendientes:
            pendientes.append(
                HomeUserPendiente(icon="✅", text="Sin tareas pendientes", count=0)
            )

        # Alerts
        alerts = []
        if registros_hoy == 0:
            alerts.append(
                HomeUserAlert(icon="⚠️", text="Aún no has registrado actividad hoy")
            )
        if radicaciones_pendientes > 0:
            alerts.append(
                HomeUserAlert(
                    icon="⚠️",
                    text=f"{radicaciones_pendientes} facturas próximas a vencer",
                )
            )
        if not alerts:
            alerts.append(HomeUserAlert(icon="✅", text="Sin alertas activas"))

        # Insights
        insights = []
        module_counts = {
            "Legalizaciones": leg_count,
            "Facturación": bill_count,
            "RIPS": rips_count,
            "Procesos": proc_count,
        }
        if module_counts:
            top_module = max(module_counts, key=module_counts.get)
            top_count = module_counts[top_module]
            if top_count > 0:
                insights.append(
                    HomeUserInsight(
                        text=f"Tu módulo con mayor volumen es {top_module} con {top_count} registros"
                    )
                )

        if radicaciones_pendientes > 0:
            insights.append(
                HomeUserInsight(
                    text=f"Llevas {radicaciones_pendientes} facturas sin radicar - atención prioritaria"
                )
            )

        total = sum(module_counts.values())
        if total > 0:
            insights.append(
                HomeUserInsight(
                    text=f"Total de {total} registros en el periodo"
                )
            )

        return HomeUserResponse(
            kpis=kpis,
            modules=modules,
            trend=trend,
            pendientes=pendientes,
            alerts=alerts,
            insights=insights[:3],
        )
