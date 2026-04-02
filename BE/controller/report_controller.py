from fastapi import APIRouter, Depends, HTTPException

from BE.services.report_service import ReportService
from BE.database.dependencies import get_db
from BE.database.db import DatabaseManager


# =====================================================
# DEPENDENCY INJECTION
# =====================================================
def get_report_service(db: DatabaseManager = Depends(get_db)):
    return ReportService(db)


# =====================================================
# ROUTER
# =====================================================
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# =====================================================
# 1. REVENUE
# =====================================================
@router.get("/revenue")
def get_revenue(
    start_date: str = None,
    end_date: str = None,
    service: ReportService = Depends(get_report_service)
):
    try:
        revenue = service.get_revenue(start_date, end_date)

        return {
            "success": True,
            "data": {
                "revenue": revenue
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 2. TOP PRODUCTS
# =====================================================
@router.get("/top-products")
def get_top_products(
    limit: int = 5,
    service: ReportService = Depends(get_report_service)
):
    try:
        data = service.get_top_products(limit)

        return {
            "success": True,
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 3. TOP VARIANTS
# =====================================================
@router.get("/top-variants")
def get_top_variants(
    limit: int = 5,
    service: ReportService = Depends(get_report_service)
):
    try:
        data = service.get_top_variants(limit)

        return {
            "success": True,
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 4. PROFIT
# =====================================================
@router.get("/profit")
def get_profit(
    start_date: str = None,
    end_date: str = None,
    service: ReportService = Depends(get_report_service)
):
    try:
        profit = service.get_profit(start_date, end_date)

        return {
            "success": True,
            "data": {
                "profit": profit
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 5. REVENUE BY DAY (CHART)
# =====================================================
@router.get("/revenue-by-day")
def get_revenue_by_day(
    start_date: str = None,
    end_date: str = None,
    service: ReportService = Depends(get_report_service)
):
    try:
        data = service.get_revenue_by_day(start_date, end_date)

        return {
            "success": True,
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 6. INVENTORY VALUE
# =====================================================
@router.get("/inventory-value")
def get_inventory_value(
    service: ReportService = Depends(get_report_service)
):
    try:
        value = service.get_inventory_value()

        return {
            "success": True,
            "data": {
                "inventory_value": value
            }
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# 7. DASHBOARD (ALL-IN-ONE)
# =====================================================
@router.get("/dashboard")
def get_dashboard(
    service: ReportService = Depends(get_report_service)
):
    try:
        data = service.get_dashboard()

        return {
            "success": True,
            "data": data
        }

    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")