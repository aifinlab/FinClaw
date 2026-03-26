#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资逻辑提炼工具
用于从长文本中提取投资逻辑、生成摘要、验证方法
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import re


class ThesisExtractor:
    """投资逻辑提取器"""

    # 逻辑强度关键词
    STRENGTH_KEYWORDS = {
        'strong': ['核心', '关键', '重大', '显著', '大幅', '翻倍'],
        'medium': ['有望', '预计', '可能', '或', '大概'],
        'weak': ['关注', '留意', '观察', '等待']
    }

    @staticmethod
    def extract_core_thesis(text: str, max_length: int = 50) -> str:
        """
        从文本中提取核心论点

        Args:
            text: 输入文本
            max_length: 最大长度

        Returns:
            核心论点
        """
        # 寻找关键句
        sentences = re.split(r'[。！？!?]', text)

        # 评分句子
        scored_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            score = 0
            # 包含投资建议关键词
            if any(kw in sentence for kw in ['建议', '推荐', '买入', '增持', '目标价']):
                score += 3
            # 包含核心判断词
            if any(kw in sentence for kw in ['核心', '关键', '主要', '逻辑']):
                score += 2
            # 包含数据
            if re.search(r'\d+%', sentence) or re.search(r'\d+亿', sentence):
                score += 1

            scored_sentences.append((score, sentence))

        # 排序取最高分
        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        if scored_sentences:
            thesis = scored_sentences[0][1]
            # 截断到最大长度
            if len(thesis) > max_length:
                thesis = thesis[:max_length] + '...'
            return thesis

        return "未提取到核心论点"

    @staticmethod
    def extract_arguments(text: str, max_count: int = 5) -> List[str]:
        """
        提取论据

        Args:
            text: 输入文本
            max_count: 最大数量

        Returns:
            论据列表
        """
        arguments = []

        # 寻找序号论据
        numbered = re.findall(r'[一二三四五六 123456][、\.](.*?)[。！？!?]', text)
        if numbered:
            arguments = numbered[:max_count]

        # 寻找 bullet points
        if not arguments:
            bullets = re.findall(r'•\s*(.*?)[。！？!?]', text)
            if bullets:
                arguments = bullets[:max_count]

        # 寻找包含数据的句子
        if not arguments:
            data_sentences = re.findall(r'([^。！？!?]*\d+%[^。！？!?]*|[^。！？!?]*\d+ 亿[^。！？!?]*)[。！？!?]', text)
            if data_sentences:
                arguments = data_sentences[:max_count]

        return arguments

    @staticmethod
    def extract_catalysts(text: str) -> List[Dict]:
        """
        提取催化剂

        Args:
            text: 输入文本

        Returns:
            催化剂列表
        """
        catalysts = []

        # 时间 + 事件模式
        patterns = [
            r'(\d{1,2}月 \d{1,2}日)[：:]\s*(.+?)[。！？!?]',
            r'(\d{4}年 \d{1,2}月)[：:]\s*(.+?)[。！？!?]',
            r'(近期 | 即将 | 预计)[：:]\s*(.+?)[。！？!?]',
            r'(催化剂 | 催化 | 事件)[：:]\s*(.+?)[。！？!?]'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    catalysts.append({
                        'time': match[0],
                        'event': match[1]
                    })

        return catalysts[:5]

    @staticmethod
    def extract_risks(text: str) -> List[str]:
        """
        提取风险因素

        Args:
            text: 输入文本

        Returns:
            风险列表
        """
        risks = []

        # 寻找风险相关段落
        risk_patterns = [
            r'风险 [：:](.+?)[。！？!?]',
            r'风险因素 [：:](.+?)[。！？!?]',
            r'风险提示 [：:](.+?)[。！？!?]',
            r'需关注 [：:](.+?)[。！？!?]'
        ]

        for pattern in risk_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 分割多个风险
                items = re.split(r'[、,]', match)
                risks.extend([item.strip() for item in items if item.strip()])

        return risks[:5]

    @staticmethod
    def generate_thesis_summary(company: str, thesis: str, arguments: List[str],
                                 catalysts: List[Dict], risks: List[str]) -> Dict:
        """
        生成投资逻辑摘要

        Args:
            company: 公司名称
            thesis: 核心论点
            arguments: 论据列表
            catalysts: 催化剂列表
            risks: 风险列表

        Returns:
            摘要字典
        """
        return {
            'company': company,
            'thesis': thesis,
            'arguments': arguments,
            'catalysts': catalysts,
            'risks': risks,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def format_thesis_to_markdown(summary: Dict) -> str:
        """
        格式化为 Markdown

        Args:
            summary: 摘要字典

        Returns:
            Markdown 文本
        """
        output = f"# 【{summary.get('company', '')} 投资逻辑】\n\n"

        # 核心论点
        output += f"## 核心论点\n{summary.get('thesis', '')}\n\n"

        # 关键论据
        output += "## 关键论据\n"
        for i, arg in enumerate(summary.get('arguments', []), 1):
            output += f"{i}. {arg}\n"
        output += "\n"

        # 催化剂
        catalysts = summary.get('catalysts', [])
        if catalysts:
            output += "## 催化剂\n"
            for cat in catalysts:
                output += f"- {cat.get('time', '')}: {cat.get('event', '')}\n"
            output += "\n"

        # 风险因素
        risks = summary.get('risks', [])
        if risks:
            output += "## 风险因素\n"
            for risk in risks:
                output += f"- {risk}\n"

        return output

    @staticmethod
    def validate_thesis(summary: Dict) -> Dict:
        """
        验证投资逻辑完整性

        Args:
            summary: 摘要字典

        Returns:
            验证结果
        """
        issues = []

        # 检查核心论点
        thesis = summary.get('thesis', '')
        if not thesis:
            issues.append('缺少核心论点')
        elif len(thesis) < 10:
            issues.append('核心论点过短')
        elif len(thesis) > 100:
            issues.append('核心论点过长')

        # 检查论据
        arguments = summary.get('arguments', [])
        if len(arguments) < 2:
            issues.append('论据不足（建议至少 2 条）')

        # 检查催化剂
        catalysts = summary.get('catalysts', [])
        if not catalysts:
            issues.append('缺少催化剂')

        # 检查风险
        risks = summary.get('risks', [])
        if not risks:
            issues.append('缺少风险提示')

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'score': max(0, 100 - len(issues) * 20)
        }


def main():
    """测试函数"""
    # 测试文本
    test_text = """
    我们看好 XX 公司的投资价值。核心逻辑：公司作为行业龙头，受益于行业集中度提升，预计未来 3 年营收 CAGR 超过 30%。

    关键论据：
    1. 市场份额从 15% 提升至 25%，行业第一
    2. 新产品毛利率达 50%，显著高于行业平均
    3. 在手订单充足，覆盖明年营收 80%

    催化剂：
    - 3 月 20 日：年报发布
    - 4 月：新产品上市

    风险因素：行业竞争加剧、原材料价格上涨、宏观经济下行
    """

    # 提取核心论点
    thesis = ThesisExtractor.extract_core_thesis(test_text)
    print(f"核心论点：{thesis}\n")

    # 提取论据
    arguments = ThesisExtractor.extract_arguments(test_text)
    print(f"论据：{arguments}\n")

    # 提取催化剂
    catalysts = ThesisExtractor.extract_catalysts(test_text)
    print(f"催化剂：{catalysts}\n")

    # 提取风险
    risks = ThesisExtractor.extract_risks(test_text)
    print(f"风险：{risks}\n")

    # 生成摘要
    summary = ThesisExtractor.generate_thesis_summary('XX 公司', thesis, arguments, catalysts, risks)

    # 格式化输出
    markdown = ThesisExtractor.format_thesis_to_markdown(summary)
    print("\n格式化输出:")
    print(markdown)

    # 验证
    validation = ThesisExtractor.validate_thesis(summary)
    print(f"\n验证结果：{validation}")


if __name__ == "__main__":
    main()
