"""8-domain knowledge base for the cloud QuickPass (云闪付) intelligent router.

Business fact, not implementation detail: domainId values and boundaries are
fixed by the challenge spec appendix 2. Do not renumber.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    domain_nm: str
    domain_id: str
    domain_desc: str


DOMAINS: list[Domain] = [
    Domain("权益", "110002", "已有卡的权益查询、使用、预订"),
    Domain("还款", "110003", "信用卡账单管理、还款操作"),
    Domain("申卡", "110004", "找卡、选卡、对比卡、申请信用卡"),
    Domain("公缴", "110005", "公用事业账单查询、公缴缴费"),
    Domain("收支分析", "110006", "交易分析与账单查询"),
    Domain("优惠（聚优惠）", "110007", "优惠券、积分、平台补贴等泛优惠管理"),
    Domain("卡详情", "110008", "卡号、卡等级、卡状态、余额查询，卡面编辑"),
    Domain("适老（关爱版）", "110009", "支付安全守护、资金安全查询、业务导航"),
]

DOMAIN_BY_NAME = {d.domain_nm: d for d in DOMAINS}
