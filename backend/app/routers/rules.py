"""规则管理 API（内置规则，不可编辑）"""
import uuid

from fastapi import APIRouter, HTTPException

from app.data.rules_data import BUILTIN_RULES
from app.models.schemas import Rule, RuleCreate

router = APIRouter(prefix="/api/rules", tags=["rules"])

# 内置规则，不可编辑
_rules: dict[str, Rule] = {}


def _init_defaults():
    for r in BUILTIN_RULES:
        rid = str(uuid.uuid4())
        _rules[rid] = Rule(id=rid, **r.model_dump())


_init_defaults()


@router.get("")
def list_rules():
    """获取所有规则"""
    return {"items": list(_rules.values())}


@router.get("/{rule_id}")
def get_rule(rule_id: str):
    """获取单条规则"""
    if rule_id not in _rules:
        raise HTTPException(status_code=404, detail="规则不存在")
    return _rules[rule_id]


@router.post("")
def create_rule(rule: RuleCreate):
    """内置规则，不支持创建"""
    raise HTTPException(status_code=403, detail="内置规则，不支持创建")


@router.put("/{rule_id}")
def update_rule(rule_id: str, rule: RuleCreate):
    """内置规则，不支持修改"""
    raise HTTPException(status_code=403, detail="内置规则，不支持修改")


@router.delete("/{rule_id}")
def delete_rule(rule_id: str):
    """内置规则，不支持删除"""
    raise HTTPException(status_code=403, detail="内置规则，不支持删除")
