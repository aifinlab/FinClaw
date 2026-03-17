/**
 * Eastmoney Financial Report API
 * 东方财富财报数据接口
 */

const fetch = require('node-fetch');

/**
 * 获取股票财务数据（主要财务指标）
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Array>} 财务数据列表
 */
async function getFinancialData(stockCode) {
  const market = stockCode.startsWith('6') ? 'SH' : 'SZ';
  
  try {
    // 东方财富主要财务指标接口
    const url = `https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYFXListV2?code=${market}${stockCode}&type=3`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 15000
    });
    
    const data = await response.json();
    
    if (!data.data || !Array.isArray(data.data)) {
      return [];
    }
    
    return data.data.map(item => ({
      reportDate: item.REPORT_DATE,
      revenue: item.TOTAL_OPERATE_INCOME_SQ,
      revenueYoy: item.TOI_YOY,
      netProfit: item.NETPROFIT_SQ,
      netProfitYoy: item.NETPROFIT_SQ_YOY,
      grossMargin: item.GROSS_PROFIT_RATIO,
      roe: item.ROE,
      eps: item.BPS,
      debtRatio: item.DEBT_ASSET_RATIO
    }));
  } catch (error) {
    console.error(`获取 ${stockCode} 财务数据失败:`, error.message);
    return [];
  }
}

/**
 * 获取最新一期财务数据
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 最新财务数据
 */
async function getLatestFinancialData(stockCode) {
  const data = await getFinancialData(stockCode);
  return data.length > 0 ? data[0] : null;
}

/**
 * 获取业绩快报/预告
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 业绩快报数据
 */
async function getPerformancePreview(stockCode) {
  const market = stockCode.startsWith('6') ? 'SH' : 'SZ';
  
  try {
    // 业绩快报接口
    const url = `https://emweb.securities.eastmoney.com/PC_HSF10/PerformanceForecast/PerformanceForecastAjax?code=${market}${stockCode}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 15000
    });
    
    const data = await response.json();
    
    if (!data.data || data.data.length === 0) {
      return null;
    }
    
    const latest = data.data[0];
    return {
      title: `业绩${latest.FORECAST_TYPE === '1' ? '预告' : '快报'}`,
      type: latest.FORECAST_TYPE === '1' ? '业绩预告' : '业绩快报',
      date: latest.NOTICE_DATE,
      forecastType: latest.FORECAST_TYPE_NAME,
      profitChange: latest.PROFIT_CHANGE,
      profitMin: latest.PROFIT_MIN,
      profitMax: latest.PROFIT_MAX
    };
  } catch (error) {
    console.error(`获取 ${stockCode} 业绩快报失败:`, error.message);
    return null;
  }
}

/**
 * 获取分红配送信息
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Array>} 分红配送列表
 */
async function getDividendInfo(stockCode) {
  const market = stockCode.startsWith('6') ? 'SH' : 'SZ';
  
  try {
    const url = `https://emweb.securities.eastmoney.com/PC_HSF10/BonusFinancing/BonusFinancingAjax?code=${market}${stockCode}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 15000
    });
    
    const data = await response.json();
    
    if (!data.data || !data.data.fh) {
      return [];
    }
    
    return data.data.fh.map(item => ({
      reportDate: item.REPORT_DATE,
      dividend: item.BONUS_IT_RATIO, // 每股分红
      shares: item.BONUS_SECURITY_RATIO, // 每股送股
      exDate: item.EX_DIVIDEND_DATE, // 除权除息日
      recordDate: item.EQUITY_RECORD_DATE // 股权登记日
    }));
  } catch (error) {
    console.error(`获取 ${stockCode} 分红信息失败:`, error.message);
    return [];
  }
}

/**
 * 模拟获取公告列表（由于反爬限制，使用模拟数据）
 * @param {string} stockCode - 股票代码
 * @param {number} pageSize - 数量
 * @returns {Promise<Array>} 公告列表
 */
async function getAnnouncements(stockCode, pageSize = 20) {
  // 获取真实的财务数据
  const [financialData, performance, dividends] = await Promise.all([
    getFinancialData(stockCode),
    getPerformancePreview(stockCode),
    getDividendInfo(stockCode)
  ]);
  
  const announcements = [];
  
  // 添加财报公告
  if (financialData.length > 0) {
    for (const data of financialData.slice(0, 4)) {
      const reportType = getReportType(data.reportDate);
      announcements.push({
        title: `${data.reportDate.substring(0, 4)}年${reportType}`,
        type: reportType.includes('年报') ? '年报' : 
              reportType.includes('半年报') ? '半年报' : '季报',
        date: data.reportDate.split(' ')[0],
        stockCode: stockCode,
        stockName: '',
        isReal: true
      });
    }
  }
  
  // 添加业绩快报/预告
  if (performance) {
    announcements.push({
      title: performance.title,
      type: performance.type,
      date: performance.date ? performance.date.split(' ')[0] : '',
      stockCode: stockCode,
      stockName: '',
      isReal: true
    });
  }
  
  // 添加分红公告
  if (dividends.length > 0) {
    const latestDiv = dividends[0];
    if (latestDiv.dividend > 0) {
      announcements.push({
        title: `分红方案：每10股派${(latestDiv.dividend * 10).toFixed(2)}元`,
        type: '分红派息',
        date: latestDiv.reportDate ? latestDiv.reportDate.split(' ')[0] : '',
        stockCode: stockCode,
        stockName: '',
        isReal: true
      });
    }
  }
  
  // 按日期排序
  return announcements
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, pageSize);
}

/**
 * 判断报告类型
 */
function getReportType(reportDate) {
  const date = new Date(reportDate);
  const month = date.getMonth() + 1;
  
  if (month === 3 || month === 4) return '年度报告';
  if (month === 8 || month === 9) return '半年度报告';
  if (month === 10 || month === 11) return '第三季度报告';
  if (month === 5 || month === 6) return '第一季度报告';
  return '定期报告';
}

/**
 * 获取财报类公告
 * @param {string} stockCode - 股票代码
 * @param {number} pageSize - 数量
 * @returns {Promise<Array>} 财报公告列表
 */
async function getFinancialReports(stockCode, pageSize = 10) {
  const all = await getAnnouncements(stockCode, pageSize * 2);
  
  const reportTypes = ['年报', '半年报', '季报', '业绩快报', '业绩预告'];
  return all.filter(item => reportTypes.includes(item.type));
}

/**
 * 批量获取多只股票最新公告
 * @param {Array<string>} stockCodes - 股票代码列表
 * @returns {Promise<Object>} 公告数据
 */
async function getBatchAnnouncements(stockCodes) {
  const result = {};
  for (const code of stockCodes) {
    try {
      result[code] = await getAnnouncements(code, 5);
    } catch (error) {
      console.error(`获取 ${code} 公告失败:`, error.message);
      result[code] = [];
    }
  }
  return result;
}

/**
 * 获取今日新增公告
 * @param {Array<string>} stockCodes - 监控的股票列表
 * @param {string} lastCheckDate - 上次检查日期 YYYY-MM-DD
 * @returns {Promise<Array>} 新增公告
 */
async function getNewAnnouncements(stockCodes, lastCheckDate) {
  const newAnnouncements = [];
  const today = new Date().toISOString().split('T')[0];
  
  for (const code of stockCodes) {
    try {
      const announcements = await getAnnouncements(code, 10);
      const newOnes = announcements.filter(a => {
        return a.date >= lastCheckDate && a.date <= today;
      });
      newAnnouncements.push(...newOnes);
    } catch (error) {
      console.error(`检查 ${code} 新公告失败:`, error.message);
    }
  }
  
  return newAnnouncements.sort((a, b) => new Date(b.date) - new Date(a.date));
}

// 导出函数
module.exports = {
  getAnnouncements,
  getFinancialReports,
  getPerformancePreview: getPerformancePreview,
  getBatchAnnouncements,
  getNewAnnouncements,
  getFinancialData,
  getLatestFinancialData,
  getDividendInfo
};
