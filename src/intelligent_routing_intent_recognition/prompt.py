"""System prompt assembly: domain knowledge base + output contract + few-shot examples.

Few-shot examples below are synthetic training-only data (虚构数据，非真实客户数据),
handcrafted from the challenge's appendix-2 domain boundaries because the real
train.jsonl dataset was not available at training-prep time.
"""

from .domains import DOMAINS

_FEW_SHOT = [
    ("我这个月的信用卡账单还有多久到期，怎么分期还款？", "还款", "110003"),
    ("帮我推荐一张餐饮优惠多的信用卡", "申卡", "110004"),
    ("我的水电燃气账单在哪里查询缴费", "公缴", "110005"),
    ("帮我看看这张卡这个月刷了多少钱，都花在哪了", "收支分析", "110006"),
    ("我有张优惠券快过期了，能在哪些商户核销", "优惠（聚优惠）", "110007"),
    ("查一下我这张卡的卡号和当前状态", "卡详情", "110008"),
    ("我爸妈年纪大了，想开启支付安全守护功能", "适老（关爱版）", "110009"),
    ("这张卡有哪些权益可以用，怎么预订机场贵宾厅", "权益", "110002"),
    ("今天天气怎么样", "", ""),
]


def _domain_kb_block() -> str:
    lines = [f"- {d.domain_nm}（domainId={d.domain_id}）：{d.domain_desc}" for d in DOMAINS]
    return "\n".join(lines)


def _few_shot_block() -> str:
    parts = []
    for question, domain_nm, domain_id in _FEW_SHOT:
        answer = (
            f'[{{"domainNm":"{domain_nm}","domainId":"{domain_id}","trust":"0.9x"}},'
            f'{{"domainNm":"...","domainId":"...","trust":"0.0x"}}]'
        )
        parts.append(f"问：{question}\n答：{answer}")
    return "\n\n".join(parts)


SYSTEM_PROMPT = f"""你是云闪付智能路由的意图识别引擎。你的唯一任务：把用户的一句自然语言问题，
路由到最匹配的业务领域（Top2，按置信度降序）。

## 领域知识库（8个领域，domainId 固定，不可编造）
{_domain_kb_block()}

## 输出格式（严格遵守，任何偏离都判为不合规）
- 只输出一个 JSON 数组本身，不得有多余文字、换行说明或 Markdown 代码块标记（不要用 ```）。
- 数组恰好包含 2 个对象，按置信度从高到低排列。
- 每个对象字段：domainNm（领域名称，须与知识库完全一致的字符串）、domainId（对应领域ID）、
  trust（[0,1] 区间的置信度，字符串形式，保留两位小数）。
- 若问题与全部 8 个领域都不相关，两个对象的 domainNm 与 domainId 均为空字符串 ""，
  trust 仍需给出 [0,1] 内的数值。

## 示例
{_few_shot_block()}

现在请仅输出 JSON 数组，不要输出任何其他文字。"""


def build_user_message(question: str) -> str:
    return question
