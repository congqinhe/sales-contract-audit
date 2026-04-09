"""规则管理 API — 方案B：按模块组织的结构化规则"""
from fastapi import APIRouter

from app.data.rules_data import BUILTIN_RULES, MODULES, get_rules_by_module

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("")
def list_rules():
    """获取所有规则（扁平列表）"""
    return {"items": [r.model_dump() for r in BUILTIN_RULES]}


@router.get("/modules")
def list_modules():
    """获取所有模块名称"""
    return {"modules": list(MODULES)}


@router.get("/by-module")
def rules_by_module(company: str = None):
    """按模块分组返回规则"""
    result = {}
    for module in MODULES:
        rules = get_rules_by_module(module, company)
        if rules:
            result[module] = [r.model_dump() for r in rules]
    return {"modules": result}


@router.get("/module/{module_name}")
def get_module_rules(module_name: str, company: str = None):
    """获取指定模块的规则"""
    rules = get_rules_by_module(module_name, company)
    return {"module": module_name, "rules": [r.model_dump() for r in rules]}
