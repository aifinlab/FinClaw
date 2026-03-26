/** @format */
/**
 * Eastmoney Fund Daily - 天天基金网数据接口
 * 提供基金实时估值、历史净值、持仓结构等真实数据
 * 数据来源: fund.eastmoney.com / fundgz.1234567.com.cn
 */

const fetch = require('node-fetch');

/**
 * 获取基金详细数据（天天基金网）
 * @param {string} fundCode - 基金代码
 * @returns {Promise<Object>} 基金详细数据
 */
async function getFundDetailFromEastmoney(fundCode) {
  try {
    const url = `http://fund.eastmoney.com/pingzhongdata/${fundCode}.js`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': `http://fund.eastmoney.com/${fundCode}.html`
      },
      timeout: 30000
    });
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    
    const text = await response.text();
    
    // 解析基金名称
    const nameMatch = text.match(/var fS_name = "(.+?)"/);
    const name = nameMatch ? nameMatch[1] : '';
    
    // 解析基金代码
    const codeMatch = text.match(/var fS_code = "(.+?)"/);
    const code = codeMatch ? codeMatch[1] : fundCode;
    
    // 解析历史净值 - 使用更简单的正则
    let netWorthTrend = [];
    const netWorthMatch = text.match(/Data_netWorthTrend = (\[.+?\]);/);
    if (netWorthMatch) {
      try {
        netWorthTrend = JSON.parse(netWorthMatch[1]);
      } catch (e) {
        console.error('解析净值数据失败:', e.message);
      }
    }
    
    // 解析同类排名百分比
    let rankData = [];
    const rankMatch = text.match(/Data_rateInSimilarPersent = (\[.+?\]);/);
    if (rankMatch) {
      try {
        rankData = JSON.parse(rankMatch[1]);
      } catch (e) {
        console.error('解析排名数据失败:', e.message);
      }
    }
    
    // 解析规模变动
    let scaleData = null;
    const scaleMatch = text.match(/Data_fluctuationScale = ({.+?});/);
    if (scaleMatch) {
      try {
        scaleData = JSON.parse(scaleMatch[1]);
      } catch (e) {
        console.error('解析规模数据失败:', e.message);
      }
    }
    
    // 解析基金经理
    let managers = [];
    const managerMatch = text.match(/Data_currentFundManager = (\[.+?\]);/);
    if (managerMatch) {
      try {
        managers = JSON.parse(managerMatch[1]);
      } catch (e) {
        console.error('解析基金经理数据失败:', e.message);
      }
    }
    
    // 计算最新净值和近期收益
    const latest = netWorthTrend.length > 0 ? netWorthTrend[netWorthTrend.length - 1] : null;
    const latestNav = latest ? latest.y : 0;
    const latestDate = latest ? new Date(latest.x).toISOString().split('T')[0] : '';
    
    // 计算各周期收益
    const growth1m = calculateGrowth(netWorthTrend, 30);
    const growth3m = calculateGrowth(netWorthTrend, 90);
    const growth6m = calculateGrowth(netWorthTrend, 180);
    const growth1y = calculateGrowth(netWorthTrend, 365);
    
    // 获取最新排名
    const latestRank = rankData.length > 0 ? rankData[rankData.length - 1] : null;
    const rankPercent = latestRank ? latestRank[1] : 50;
    
    // 获取最新规模
    let latestScale = 0;
    if (scaleData && scaleData.series && scaleData.series.length > 0) {
      const scaleSeries = scaleData.series[scaleData.series.length - 1];
      latestScale = scaleSeries.y || 0;
    }
    
    // 获取基金经理信息
    const manager = managers.length > 0 ? managers[0] : null;
    
    return {
      code: code,
      name: name,
      nav: latestNav,
      navDate: latestDate,
      scale: latestScale,
      growth1m: growth1m,
      growth3m: growth3m,
      growth6m: growth6m,
      growth1y: growth1y,
      rankPercent: rankPercent,
      manager: manager ? manager.name : '',
      managerInfo: manager,
      netWorthTrend: netWorthTrend.slice(-30),
      rawData: {
        netWorthTrend,
        rankData,
        scaleData,
        managers
      }
    };
  } catch (error) {
    console.error('获取天天基金数据失败:', error.message);
    return null;
  }
}

/**
 * 计算区间收益
 * @param {Array} trend - 净值趋势数据
 * @param {number} days - 天数
 * @returns {number} 收益率(%)
 */
function calculateGrowth(trend, days) {
  if (!trend || trend.length === 0) return 0;
  
  const endIndex = trend.length - 1;
  const startIndex = Math.max(0, endIndex - days);
  
  const endValue = trend[endIndex].y;
  const startValue = trend[startIndex].y;
  
  if (startValue === 0) return 0;
  
  return ((endValue - startValue) / startValue * 100).toFixed(2);
}

/**
 * 获取基金实时估值
 * @param {string} fundCode - 基金代码
 * @returns {Promise<Object>} 实时估值数据
 */
async function getFundRealtimeValue(fundCode) {
  try {
    const url = `http://fundgz.1234567.com.cn/js/${fundCode}.js`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': `http://fund.eastmoney.com/${fundCode}.html`
      },
      timeout: 30000
    });
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    
    const text = await response.text();
    
    // 解析JSONP响应
    const match = text.match(/jsonpgz\((.+?)\);/);
    if (!match) {
      throw new Error('无法解析估值数据');
    }
    
    const data = JSON.parse(match[1]);
    
    return {
      code: data.fundcode,
      name: data.name,
      nav: parseFloat(data.dwjz),
      navDate: data.jzrq,
      estimateNav: parseFloat(data.gsz),
      estimateGrowth: parseFloat(data.gszzl),
      estimateTime: data.gztime
    };
  } catch (error) {
    console.error('获取实时估值失败:', error.message);
    return null;
  }
}

/**
 * 获取基金历史净值列表
 * @param {string} fundCode - 基金代码
 * @param {number} pageSize - 每页数量
 * @returns {Promise<Array>} 历史净值列表
 */
async function getFundHistoryNav(fundCode, pageSize = 20) {
  try {
    const detail = await getFundDetailFromEastmoney(fundCode);
    if (!detail || !detail.rawData || !detail.rawData.netWorthTrend) {
      return [];
    }
    
    return detail.rawData.netWorthTrend
      .slice(-pageSize)
      .map(item => ({
        date: new Date(item.x).toISOString().split('T')[0],
        nav: item.y,
        growth: item.y * (item.sc ? parseFloat(item.sc) / 100 : 0)
      }))
      .reverse();
  } catch (error) {
    console.error('获取历史净值失败:', error.message);
    return [];
  }
}

/**
 * 搜索基金
 * @param {string} keyword - 搜索关键词
 * @returns {Promise<Array>} 搜索结果
 */
async function searchFunds(keyword) {
  try {
    // 使用天天基金的搜索API
    const url = `http://fund.eastmoney.com/js/fundcode_search.js`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 30000
    });
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    
    const text = await response.text();
    
    // 解析JSONP响应
    const match = text.match(/var r = (.+?);/);
    if (!match) {
      throw new Error('无法解析基金列表');
    }
    
    const allFunds = JSON.parse(match[1]);
    
    // 过滤搜索结果
    const filtered = allFunds.filter(fund => {
      const code = fund[0];
      const name = fund[2];
      const pinyin = fund[1];
      return code.includes(keyword) || 
             name.includes(keyword) || 
             pinyin.toLowerCase().includes(keyword.toLowerCase());
    });
    
    return filtered.slice(0, 10).map(fund => ({
      code: fund[0],
      pinyin: fund[1],
      name: fund[2],
      type: fund[3]
    }));
  } catch (error) {
    console.error('搜索基金失败:', error.message);
    return [];
  }
}

module.exports = {
  getFundDetailFromEastmoney,
  getFundRealtimeValue,
  getFundHistoryNav,
  searchFunds,
  calculateGrowth
};
