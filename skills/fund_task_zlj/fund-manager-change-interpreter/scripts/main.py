#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from datetime import datetime

SKILL_META = {
    "display_name": "基金经理变更公告解读助手",
    "domain": "基金投研",
    "scene": "公告解读",
    "description": "基金经理变更公告解读助手 - 基金投研/公告解读"
}
CATEGORIES = ["fund", "announcement", "research"]

# 基金经理变更相关关键词
MANAGER_CHANGE_KEYWORDS = [
    "基金经理", "离任", "增聘", "变更", "调整", "共同管理", "接任", "卸任",
    "任职", "管理", "公告", "生效", "日期", "原因", "工作安排"
]

# 基金信息正则模式
FUND_CODE_PATTERN = r"\b\d{6}\b"
FUND_NAME_PATTERN = r"([一-鿿A-Za-z0-9]+(基金|FOF|ETF|REITs|混合|股票|债券|货币))"

# 日期正则模式
DATE_PATTERN = r"\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}"

# 经理姓名模式（中文姓名）
MANAGER_NAME_PATTERN = r"[赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厓聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公万俟司马上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子车颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父谷梁晋楚闫法汝鄢涂钦段干百里东郭南门呼延归海羊舌微生岳帅缑亢况后有琴梁丘左丘东门西门商牟佘佴伯赏南宫墨哈谯笪年爱阳佟第五言福百家姓续]"

def load_text(path: str, raw_text: str) -> str:
    """加载文本内容"""
    if raw_text:
        return raw_text
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def extract_fund_info(text: str, fund_code: str, fund_name: str) -> dict:
    """提取基金基本信息"""
    if not fund_code:
        match = re.search(FUND_CODE_PATTERN, text)
        fund_code = match.group(0) if match else ""
    
    if not fund_name:
        name_match = re.search(FUND_NAME_PATTERN, text)
        fund_name = name_match.group(0) if name_match else ""
    
    # 提取基金简称
    fund_short_name = fund_name
    if "(" in fund_name and ")" in fund_name:
        # 尝试提取括号内的简称
        short_match = re.search(r"\(([^)]+)\)", fund_name)
        if short_match:
            fund_short_name = short_match.group(1)
    
    return {
        "fund_name": fund_name,
        "fund_code": fund_code,
        "fund_short_name": fund_short_name,
        "text_length": len(text),
    }

def extract_dates(text: str) -> dict:
    """提取日期信息"""
    dates = re.findall(DATE_PATTERN, text)
    
    # 尝试识别公告日期和生效日期
    announcement_date = ""
    effective_date = ""
    
    if dates:
        # 第一个日期通常为公告日期
        announcement_date = dates[0]
        # 尝试标准化日期格式
        announcement_date = normalize_date(announcement_date)
        
        if len(dates) > 1:
            effective_date = dates[1]
            effective_date = normalize_date(effective_date)
    
    return {
        "announcement_date": announcement_date,
        "effective_date": effective_date,
        "all_dates_found": dates
    }

def normalize_date(date_str: str) -> str:
    """标准化日期格式为YYYY-MM-DD"""
    if not date_str:
        return ""
    
    # 处理中文日期格式
    if "年" in date_str and "月" in date_str and "日" in date_str:
        match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
    
    # 处理其他格式
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"]:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_str

def extract_manager_names(text: str) -> dict:
    """提取经理姓名"""
    # 查找中文姓名
    name_matches = re.findall(MANAGER_NAME_PATTERN + r"{2,3}", text)
    
    # 去重
    unique_names = list(set(name_matches))
    
    # 尝试识别离任经理和新任经理
    departing_managers = []
    new_managers = []
    
    # 基于上下文关键词判断
    for name in unique_names:
        # 查找姓名周围的上下文
        name_pattern = re.escape(name)
        context_match = re.search(rf".{{0,50}}{name_pattern}.{{0,50}}", text)
        if context_match:
            context = context_match.group(0)
            if any(keyword in context for keyword in ["离任", "卸任", "不再担任", "辞去"]):
                departing_managers.append(name)
            elif any(keyword in context for keyword in ["增聘", "新任", "接任", "担任"]):
                new_managers.append(name)
    
    return {
        "all_managers_found": unique_names,
        "departing_managers": departing_managers,
        "new_managers": new_managers,
        "co_managers": [name for name in unique_names if name not in departing_managers + new_managers]
    }

def determine_event_type(text: str, managers_info: dict) -> str:
    """确定事件类型"""
    text_lower = text.lower()
    
    if "离任" in text and "增聘" in text:
        return "离任兼增聘"
    elif "离任" in text:
        return "离任"
    elif "增聘" in text:
        return "增聘"
    elif "变更" in text:
        return "变更"
    elif "调整" in text:
        return "调整"
    
    # 根据经理信息推断
    if managers_info["departing_managers"] and managers_info["new_managers"]:
        return "离任兼增聘"
    elif managers_info["departing_managers"]:
        return "离任"
    elif managers_info["new_managers"]:
        return "增聘"
    
    return "未知"

def extract_change_reason(text: str) -> str:
    """提取变更原因"""
    reason_keywords = [
        "工作安排", "个人原因", "公司安排", "内部调整", "岗位变动",
        "职业发展", "退休", "离职", "调动", "其他原因"
    ]
    
    for keyword in reason_keywords:
        if keyword in text:
            # 提取包含关键词的句子
            pattern = rf"[^。！？]*{keyword}[^。！？]*[。！？]"
            match = re.search(pattern, text)
            if match:
                return match.group(0)
    
    return "公告未明确说明"

def analyze_management_stability(event_type: str, managers_info: dict) -> str:
    """分析管理稳定性"""
    if event_type == "增聘":
        return "管理团队得到补充，稳定性增强。"
    elif event_type == "离任":
        if managers_info["new_managers"]:
            return "虽有经理离任，但已有接替安排，管理连续性相对可控。"
        else:
            return "经理离任且无明确接替安排，管理连续性可能受影响。"
    elif event_type == "离任兼增聘":
        return "管理安排已完成衔接，短期管理连续性相对可控。"
    else:
        return "基于公告信息，管理稳定性需进一步观察。"

def analyze_style_continuity(event_type: str, text: str) -> str:
    """分析风格延续性"""
    if "投资框架" in text or "投资理念" in text or "投资策略" in text:
        if "延续" in text or "保持一致" in text or "继承" in text:
            return "公告提及投资框架/理念将延续，风格扰动可能较小。"
        elif "调整" in text or "变化" in text or "优化" in text:
            return "公告提及投资框架可能调整，风格或有变化。"
    
    if event_type == "离任":
        return "原经理离任可能带来一定风格扰动，需观察新任经理管理风格。"
    elif event_type == "增聘":
        return "增聘经理可能带来新的投研视角，但核心框架可能保持稳定。"
    
    return "公告未明确提及风格延续性，需结合后续持仓变化观察。"

def assess_impact_level(event_type: str, managers_info: dict) -> str:
    """评估影响等级"""
    if event_type == "离任" and not managers_info["new_managers"]:
        return "高"
    elif event_type == "离任兼增聘":
        return "中"
    elif event_type == "增聘":
        return "低"
    elif event_type == "变更" or event_type == "调整":
        return "中"
    else:
        return "待评估"

def generate_follow_up_suggestions(event_type: str, impact_level: str) -> list:
    """生成跟踪建议"""
    suggestions = []
    
    if impact_level in ["高", "中"]:
        suggestions.append("跟踪后续季报持仓变化")
    
    if event_type in ["离任", "离任兼增聘", "增聘"]:
        suggestions.append("核查新任经理过往管理产品经历")
    
    suggestions.append("观察基金公司后续人事稳定性")
    
    if impact_level == "高":
        suggestions.append("评估是否调整投资组合配置")
    
    return suggestions

def build_output(text: str, fund_code: str, fund_name: str) -> dict:
    """构建输出结果"""
    # 提取基本信息
    fund_info = extract_fund_info(text, fund_code, fund_name)
    dates_info = extract_dates(text)
    managers_info = extract_manager_names(text)
    
    # 确定事件类型和原因
    event_type = determine_event_type(text, managers_info)
    change_reason = extract_change_reason(text)
    
    # 投研分析
    management_stability = analyze_management_stability(event_type, managers_info)
    style_continuity = analyze_style_continuity(event_type, text)
    impact_level = assess_impact_level(event_type, managers_info)
    
    # 生成事件摘要
    event_summary = generate_event_summary(event_type, fund_info, managers_info)
    
    # 生成跟踪建议
    follow_up_suggestions = generate_follow_up_suggestions(event_type, impact_level)
    
    # 构建完整输出
    output = {
        "skill": SKILL_META["display_name"],
        "domain": SKILL_META["domain"],
        "scene": SKILL_META["scene"],
        "input_summary": {
            "text_length": len(text),
            "contains_manager_change": any(keyword in text for keyword in MANAGER_CHANGE_KEYWORDS)
        },
        "fund_info": fund_info,
        "announcement_info": {
            **dates_info,
            "event_type": event_type,
            "change_reason": change_reason
        },
        "manager_change": {
            "departing_managers": managers_info["departing_managers"],
            "new_managers": managers_info["new_managers"],
            "co_managers": managers_info["co_managers"],
            "all_managers_found": managers_info["all_managers_found"]
        },
        "event_summary": event_summary,
        "research_interpretation": {
            "management_stability": management_stability,
            "style_continuity": style_continuity,
            "team_support": "变更后管理安排需结合基金公司投研平台综合评估。",
            "overall_judgement": f"基于公告文本，本次事件影响倾向{impact_level}。"
        },
        "impact_level": impact_level,
        "tags": generate_tags(event_type, managers_info, impact_level),
        "follow_up_suggestions": follow_up_suggestions,
        "limitations": "以上结论仅基于公告文本，未结合历史业绩、持仓和公司投研平台进行扩展验证。"
    }
    
    return output

def generate_event_summary(event_type: str, fund_info: dict, managers_info: dict) -> str:
    """生成事件摘要"""
    fund_name = fund_info.get("fund_short_name", fund_info.get("fund_name", ""))
    
    if event_type == "离任" and managers_info["departing_managers"]:
        managers = "、".join(managers_info["departing_managers"])
        return f"{fund_name}基金经理{managers}离任。"
    elif event_type == "增聘" and managers_info["new_managers"]:
        managers = "、".join(managers_info["new_managers"])
        return f"{fund_name}增聘基金经理{managers}。"
    elif event_type == "离任兼增聘":
        departing = "、".join(managers_info["departing_managers"]) if managers_info["departing_managers"] else ""
        new = "、".join(managers_info["new_managers"]) if managers_info["new_managers"] else ""
        if departing and new:
            return f"{fund_name}基金经理{departing}离任，同时增聘{new}。"
    
    return f"{fund_name}发生基金经理{event_type}事件。"

def generate_tags(event_type: str, managers_info: dict, impact_level: str) -> list:
    """生成标签"""
    tags = [event_type]
    
    if managers_info["departing_managers"]:
        tags.append("经理离任")
    if managers_info["new_managers"]:
        tags.append("经理增聘")
    if len(managers_info["all_managers_found"]) > 1:
        tags.append("多经理管理")
    
    tags.append(f"影响{impact_level}")
    
    return tags

def main():
    parser = argparse.ArgumentParser(description=SKILL_META["description"])
    parser.add_argument("--text", type=str, help="公告文本内容")
    parser.add_argument("--file", type=str, help="公告文件路径")
    parser.add_argument("--fund_code", type=str, default="", help="基金代码")
    parser.add_argument("--fund_name", type=str, default="", help="基金名称")
    parser.add_argument("--output", type=str, default="output.json", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 加载文本
    text = load_text(args.file, args.text)
    
    if not text:
        print("错误：未提供公告文本")
        return
    
    # 处理文本
    result = build_output(text, args.fund_code, args.fund_name)
    
    # 输出结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"分析完成，结果已保存至 {args.output}")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()