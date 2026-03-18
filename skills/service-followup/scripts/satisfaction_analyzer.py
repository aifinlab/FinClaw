#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
满意度分析器

功能：
1. 满意度评分计算
2. NPS 计算
3. 满意度趋势分析
4. 问题分类统计

使用示例：
    from satisfaction_analyzer import SatisfactionAnalyzer
    
    analyzer = SatisfactionAnalyzer()
    
    # 添加满意度调查数据
    analyzer.add_response("张三", {"attitude": 5, "professional": 4, "response": 5, "overall": 5, "feedback": "很好"})
    analyzer.add_response("李四", {"attitude": 3, "professional": 3, "response": 2, "overall": 3, "feedback": "响应太慢"})
    
    print(analyzer.calculate_satisfaction_score())
    print(analyzer.calculate_nps())
    print(analyzer.generate_satisfaction_report())
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SurveyResponse:
    """满意度调查回复"""
    customer_name: str
    date: str
    scores: Dict[str, int]  # 各项评分
    feedback: str
    nps_score: int  # 0-10


class SatisfactionAnalyzer:
    """满意度分析器"""
    
    # 评分维度
    SCORE_DIMENSIONS = {
        "attitude": "服务态度",
        "professional": "专业能力",
        "response": "响应速度",
        "communication": "沟通效果",
        "overall": "整体满意",
    }
    
    # NPS 分类
    NPS_PROMOTERS = 9  # 推荐者 9-10 分
    NPS_PASSIVES = 7   # 被动者 7-8 分
    NPS_DETRACTORS = 6 # 贬损者 0-6 分
    
    def __init__(self):
        self.responses: List[SurveyResponse] = []
    
    def add_response(self, customer_name: str, scores: Dict[str, int], feedback: str = "", nps_score: int = None) -> None:
        """
        添加满意度回复
        
        Args:
            customer_name: 客户姓名
            scores: 各项评分
            feedback: 文字反馈
            nps_score: NPS 评分（0-10）
        """
        if nps_score is None:
            nps_score = scores.get("overall", 5) * 2 - 2  # 转换为 0-10
        
        response = SurveyResponse(
            customer_name=customer_name,
            date=datetime.now().strftime("%Y-%m-%d"),
            scores=scores,
            feedback=feedback,
            nps_score=nps_score,
        )
        self.responses.append(response)
    
    def calculate_dimension_averages(self) -> Dict[str, float]:
        """计算各维度平均分"""
        if not self.responses:
            return {}
        
        dimension_totals = defaultdict(float)
        dimension_counts = defaultdict(int)
        
        for response in self.responses:
            for dimension, score in response.scores.items():
                dimension_totals[dimension] += score
                dimension_counts[dimension] += 1
        
        return {
            dimension: dimension_totals[dimension] / dimension_counts[dimension]
            for dimension in dimension_totals
        }
    
    def calculate_satisfaction_score(self) -> float:
        """计算整体满意度（平均分）"""
        if not self.responses:
            return 0
        
        overall_scores = [r.scores.get("overall", 0) for r in self.responses]
        return sum(overall_scores) / len(overall_scores)
    
    def calculate_nps(self) -> Dict:
        """
        计算 NPS（净推荐值）
        
        Returns:
            NPS 计算结果
        """
        if not self.responses:
            return {"nps": 0, "promoters": 0, "passives": 0, "detractors": 0}
        
        promoters = 0
        passives = 0
        detractors = 0
        
        for response in self.responses:
            nps = response.nps_score
            if nps >= self.NPS_PROMOTERS:
                promoters += 1
            elif nps >= self.NPS_PASSIVES:
                passives += 1
            else:
                detractors += 1
        
        total = len(self.responses)
        nps = (promoters - detractors) / total * 100
        
        return {
            "nps": round(nps, 1),
            "promoters": promoters,
            "promoters_pct": promoters / total * 100,
            "passives": passives,
            "passives_pct": passives / total * 100,
            "detractors": detractors,
            "detractors_pct": detractors / total * 100,
            "total": total,
        }
    
    def analyze_feedback(self) -> Dict:
        """分析文字反馈"""
        positive_keywords = ["好", "满意", "不错", "专业", "及时", "感谢", "推荐"]
        negative_keywords = ["差", "慢", "不满", "失望", "投诉", "改进", "问题"]
        
        positive_count = 0
        negative_count = 0
        feedback_list = []
        
        for response in self.responses:
            feedback = response.feedback.lower()
            is_positive = any(kw in feedback for kw in positive_keywords)
            is_negative = any(kw in feedback for kw in negative_keywords)
            
            feedback_list.append({
                "customer": response.customer_name,
                "feedback": response.feedback,
                "sentiment": "正面" if is_positive and not is_negative else ("负面" if is_negative else "中性"),
            })
            
            if is_positive:
                positive_count += 1
            if is_negative:
                negative_count += 1
        
        return {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "feedback_list": feedback_list[:10],  # 返回前 10 条
        }
    
    def generate_satisfaction_report(self) -> str:
        """
        生成满意度报告
        
        Returns:
            格式化报告文本
        """
        lines = []
        lines.append("=" * 70)
        lines.append("客户满意度分析报告")
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 70)
        lines.append("")
        
        # 样本统计
        lines.append("【样本统计】")
        lines.append(f"  回收问卷：{len(self.responses)} 份")
        lines.append("")
        
        # 满意度评分
        lines.append("【满意度评分】(5 分制)")
        dimension_avgs = self.calculate_dimension_averages()
        
        for dimension, name in self.SCORE_DIMENSIONS.items():
            avg = dimension_avgs.get(dimension, 0)
            bar = "★" * int(round(avg)) + "☆" * (5 - int(round(avg)))
            lines.append(f"  {name}: {avg:.2f} {bar}")
        
        lines.append("")
        
        # NPS
        nps_result = self.calculate_nps()
        lines.append("【NPS 净推荐值】")
        lines.append(f"  NPS: {nps_result['nps']}")
        lines.append(f"  推荐者 (9-10 分): {nps_result['promoters']} 人 ({nps_result['promoters_pct']:.1f}%)")
        lines.append(f"  被动者 (7-8 分): {nps_result['passives']} 人 ({nps_result['passives_pct']:.1f}%)")
        lines.append(f"  贬损者 (0-6 分): {nps_result['detractors']} 人 ({nps_result['detractors_pct']:.1f}%)")
        lines.append("")
        
        # 反馈分析
        feedback_analysis = self.analyze_feedback()
        lines.append("【反馈分析】")
        lines.append(f"  正面反馈：{feedback_analysis['positive_count']} 条")
        lines.append(f"  负面反馈：{feedback_analysis['negative_count']} 条")
        lines.append("")
        
        if feedback_analysis['feedback_list']:
            lines.append("  部分反馈:")
            for fb in feedback_analysis['feedback_list'][:5]:
                lines.append(f"    - {fb['customer']}: {fb['feedback']} [{fb['sentiment']}]")
        lines.append("")
        
        # 改进建议
        lines.append("【改进建议】")
        if nps_result['nps'] >= 50:
            lines.append("  ✅ NPS 表现优秀，继续保持")
        elif nps_result['nps'] >= 30:
            lines.append("  ⚠️ NPS 表现良好，关注贬损者反馈")
        else:
            lines.append("  ❌ NPS 需要改进，重点解决客户痛点")
        
        if dimension_avgs.get("response", 5) < 4:
            lines.append("  ⚠️ 响应速度需要提升")
        if dimension_avgs.get("professional", 5) < 4:
            lines.append("  ⚠️ 专业能力需要加强")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    analyzer = SatisfactionAnalyzer()
    
    # 模拟数据
    import random
    
    for i in range(20):
        name = f"客户{i + 1}"
        scores = {
            "attitude": random.randint(3, 5),
            "professional": random.randint(3, 5),
            "response": random.randint(2, 5),
            "communication": random.randint(3, 5),
            "overall": random.randint(3, 5),
        }
        feedback = random.choice(["很好", "不错", "满意", "响应太慢", "需要改进", "专业"])
        analyzer.add_response(name, scores, feedback)
    
    print(analyzer.generate_satisfaction_report())
