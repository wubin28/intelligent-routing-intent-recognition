#!/usr/bin/env python3
"""Generate human-reviewable Approved Scenarios fixtures for intent routing."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    slug: str
    title: str
    fact: str
    question: str
    domain_nm: str
    domain_id: str


SCENARIOS = (
    Scenario("01-repayment-installment", "还款分期咨询", "用户询问信用卡账单分期方式，应路由到\"还款\"领域。", "我这张信用卡账单分几期还比较划算，怎么申请分期？", "还款", "110003"),
    Scenario("02-repayment-record", "还款到账查询", "用户查询还款是否到账，应路由到\"还款\"领域。", "上个月的还款有没有到账，怎么查还款记录？", "还款", "110003"),
    Scenario("03-apply-card-no-fee", "免年费信用卡咨询", "用户咨询可申请的信用卡产品，应路由到\"申卡\"领域。", "现在有哪些年费全免的信用卡可以申请？", "申卡", "110004"),
    Scenario("04-apply-card-compare", "信用卡对比咨询", "用户对比不同信用卡产品，应路由到\"申卡\"领域。", "我想对比一下旅游卡和加油卡，哪张更划算？", "申卡", "110004"),
    Scenario("05-utility-bill-property", "物业费缴纳咨询", "用户咨询物业费是否可在云闪付缴纳，应路由到\"公缴\"领域。", "小区物业费可以在云闪付上交吗？", "公缴", "110005"),
    Scenario("06-utility-bill-broadband", "宽带账单查询", "用户查询宽带续费账单，应路由到\"公缴\"领域。", "我家宽带续费账单在哪里查询缴纳？", "公缴", "110005"),
    Scenario("07-spending-analysis-category", "餐饮消费分析", "用户查询某类消费的统计金额，应路由到\"收支分析\"领域。", "帮我看看这半年在餐饮上花了多少钱", "收支分析", "110006"),
    Scenario("08-spending-analysis-export", "消费明细导出", "用户希望导出消费明细账单，应路由到\"收支分析\"领域。", "我想导出上个月的消费明细账单", "收支分析", "110006"),
    Scenario("09-promotion-discount", "满减活动咨询", "用户咨询优惠活动，应路由到\"优惠（聚优惠）\"领域。", "最近有没有超市满减的优惠活动", "优惠（聚优惠）", "110007"),
    Scenario("10-promotion-points", "积分兑换咨询", "用户咨询积分兑换方式，应路由到\"优惠（聚优惠）\"领域。", "我攒的积分怎么兑换礼品", "优惠（聚优惠）", "110007"),
    Scenario("11-card-detail-validity", "卡有效期查询", "用户查询卡的有效期与等级信息，应路由到\"卡详情\"领域。", "帮我查一下这张卡的有效期和卡等级", "卡详情", "110008"),
    Scenario("12-card-detail-face-edit", "卡面编辑咨询", "用户希望更换卡面样式，应路由到\"卡详情\"领域。", "我想把卡面换成新款式，在哪里操作", "卡详情", "110008"),
    Scenario("13-benefit-lounge", "机场贵宾厅权益咨询", "用户咨询已有卡的权益使用方式，应路由到\"权益\"领域。", "这张白金卡有机场贵宾厅权益吗，怎么用", "权益", "110002"),
    Scenario("14-benefit-transfer", "接送机权益预订", "用户希望预订卡片附带的接送机权益，应路由到\"权益\"领域。", "我想预订一次接送机服务，用卡里的权益", "权益", "110002"),
    Scenario("15-elderly-care-mode", "适老大字版开通", "用户为父母开通适老关爱模式，应路由到\"适老（关爱版）\"领域。", "我想给我父母的账户开通大字版和防诈骗提醒", "适老（关爱版）", "110009"),
    Scenario("16-elderly-family-guard", "老年防诈骗守护", "用户咨询老年人防诈骗守护功能，应路由到\"适老（关爱版）\"领域。", "老年人怎么开启亲情守护，防止被骗转账", "适老（关爱版）", "110009"),
    Scenario("17-fallback-weather", "无关问题：天气", "与全部8个领域均无关，应兜底返回空领域。", "今天上海天气怎么样，适合出门吗", "", ""),
    Scenario("18-fallback-chitchat", "无关问题：闲聊", "与全部8个领域均无关，应兜底返回空领域。", "你能陪我聊聊天吗，最近心情不太好", "", ""),
)


def render(scenario: Scenario, number: int) -> str:
    """Render one reviewable business-fact fixture."""
    top1 = f"{scenario.domain_nm}（{scenario.domain_id}）" if scenario.domain_nm else "兜底（空领域）"
    return f'''# 场景 {number}：{scenario.title}

{scenario.fact}

规格：spec.md 第3节「领域匹配规则」

## 输入
```text
问题：{scenario.question}
```

## Top1领域
```text
{top1}
```

## 格式校验
```text
PASS
```
'''


def generate(output_dir: Path) -> list[Path]:
    """Write every scenario to output_dir and return generated paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for number, scenario in enumerate(SCENARIOS, start=1):
        path = output_dir / f"{scenario.slug}.approved.md"
        path.write_text(render(scenario, number), encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated-approved"),
        help="directory for generated fixtures (default: generated-approved)",
    )
    args = parser.parse_args()
    paths = generate(args.output_dir)
    print(f"generated {len(paths)} fixtures in {args.output_dir}")


if __name__ == "__main__":
    main()
