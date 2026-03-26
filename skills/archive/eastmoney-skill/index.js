/**
 * Eastmoney API Client
 * 东方财富/腾讯财经免费数据接口
 */

const fetch = require('node-fetch');
const iconv = require('iconv-lite');

/**
 * 获取股票基本信息 - 使用腾讯财经接口
 * @param {string} stockCode - 股票代码，如 '600519'
 * @returns {Promise<Object>} 股票基本信息
 */
async function getStockInfo(stockCode) {
  // 腾讯财经接口
  const prefix = stockCode.startsWith('6') ? 'sh' : 'sz';
  const url = `https://qt.gtimg.cn/q=${prefix}${stockCode}`;
  
  const response = await fetch(url, { timeout: 10000 });
  const buffer = await response.buffer();
  const text = iconv.decode(buffer, 'gb2312');
  
  // 解析返回数据
  const match = text.match(new RegExp(`v_${prefix}${stockCode}="([^"]+)"`));
  if (!match) {
    throw new Error(`未找到股票 ${stockCode} 的信息`);
  }
  
  const parts = match[1].split('~');
  return {
    code: stockCode,
    name: parts[1],                    // 股票名称
    price: parseFloat(parts[3]),       // 当前价格
    change: parseFloat(parts[31]) || 0,      // 涨跌额
    changePercent: parseFloat(parts[32]) || 0, // 涨跌幅
    volume: parseInt(parts[6]) || 0,   // 成交量
    turnover: parseFloat(parts[7]) || 0, // 成交额
    marketCap: (parseFloat(parts[44]) || 0) * 1e8, // 总市值（亿转元）
    pe: parseFloat(parts[39]) || null, // 市盈率
    pb: parseFloat(parts[46]) || null, // 市净率
    high: parseFloat(parts[33]) || 0,  // 最高价
    low: parseFloat(parts[34]) || 0,   // 最低价
    open: parseFloat(parts[5]) || 0,   // 开盘价
    prevClose: parseFloat(parts[4]) || 0 // 昨收
  };
}

/**
 * 获取主要财务指标 - 使用东方财富网页版接口
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 财务指标数据
 */
async function getMainFinance(stockCode) {
  const market = stockCode.startsWith('6') ? 'SH' : 'SZ';
  
  try {
    // 使用东方财富主要指标接口
    const url = `https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYFXListV2?code=${market}${stockCode}&type=3`;
    
    const response = await fetch(url, { 
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    const data = await response.json();
    
    if (!data.data || !data.data.length) {
      // 如果接口失败，使用同花顺备用数据
      return getTHSFinanceData(stockCode);
    }
    
    // 取最新一期数据
    const latest = data.data[0];
    
    return {
      code: stockCode,
      reportDate: latest.REPORT_DATE || '2024-09-30',  // 报告期
      revenue: parseFloat(latest.TOTAL_OPERATE_INCOME_SQ) || 0,     // 营业总收入
      revenueYoy: parseFloat(latest.TOTAL_OPERATE_INCOME_SQ_YOY) || 0, // 营收同比增长
      netProfit: parseFloat(latest.NETPROFIT_SQ) || 0,              // 净利润
      netProfitYoy: parseFloat(latest.NETPROFIT_SQ_YOY) || 0,       // 净利润同比增长
      grossMargin: parseFloat(latest.GROSS_PROFIT_RATIO) || 0,      // 毛利率
      roe: parseFloat(latest.ROE) || 0,                             // 净资产收益率
      eps: parseFloat(latest.BPS) || 0,                             // 每股收益
      debtRatio: parseFloat(latest.DEBT_ASSET_RATIO) || 0           // 资产负债率
    };
  } catch (error) {
    console.log(`东方财富财务数据获取失败，使用同花顺备用: ${error.message}`);
    return getTHSFinanceData(stockCode);
  }
}

/**
 * 从同花顺获取财务数据（当东方财富接口失败时使用）
 */
async function getTHSFinanceData(stockCode) {
  try {
    const ths = require('../ths-skill');
    const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
    
    const indicators = [
      { indicator: 'ths_roe_stock', indiparams: ['20241231'] },
      { indicator: 'ths_np_stock', indiparams: ['20241231'] },
      { indicator: 'ths_np_yoy_stock', indiparams: ['20241231'] },
      { indicator: 'ths_or_yoy_stock', indiparams: ['20241231'] }
    ];
    
    const data = await ths.getBasicData(thsCode, indicators);
    const table = data.tables[0]?.table || {};
    
    return {
      code: stockCode,
      reportDate: '2024-12-31',
      revenue: 0,
      revenueYoy: table.ths_or_yoy_stock?.[0] || 0,
      netProfit: table.ths_np_stock?.[0] || 0,
      netProfitYoy: table.ths_np_yoy_stock?.[0] || 0,
      grossMargin: 0,
      roe: table.ths_roe_stock?.[0] || 0,
      eps: 0,
      debtRatio: 0
    };
  } catch (error) {
    console.error(`同花顺备用数据获取失败: ${error.message}`);
    // 返回空数据而不是模拟数据
    return {
      code: stockCode,
      reportDate: '-',
      revenue: 0,
      revenueYoy: 0,
      netProfit: 0,
      netProfitYoy: 0,
      grossMargin: 0,
      roe: 0,
      eps: 0,
      debtRatio: 0
    };
  }
}

/**
 * 获取公司公告列表
 * @param {string} stockCode - 股票代码
 * @param {Object} options - 选项
 * @param {number} options.pageSize - 返回条数，默认 10
 * @returns {Promise<Array>} 公告列表
 */
async function getAnnouncements(stockCode, options = {}) {
  const { pageSize = 10 } = options;
  
  try {
    const url = `https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=NOTICE_DATE&sortTypes=-1&pageSize=${pageSize}&pageNumber=1&reportName=RPT_WEB_ANNOUNCECELIST&columns=ALL&filter=(SECURITY_CODE%3D%22${stockCode}%22)`;
    
    const response = await fetch(url, { timeout: 10000 });
    const data = await response.json();
    
    if (!data.result || !data.result.data) {
      return [];
    }
    
    return data.result.data.map(item => ({
      title: item.NOTICE_TITLE,
      type: item.NOTICE_TYPE,
      date: item.NOTICE_DATE,
      url: item.URL || item.NOTICE_URL
    }));
  } catch (error) {
    return [];
  }
}

/**
 * 批量获取多只股票的财务摘要
 * @param {Array<string>} stockCodes - 股票代码列表
 * @returns {Promise<Array>} 财务摘要列表
 */
async function getBatchFinance(stockCodes) {
  const results = [];
  for (const code of stockCodes) {
    try {
      const info = await getStockInfo(code);
      const finance = await getMainFinance(code);
      results.push({
        code,
        name: info.name,
        price: info.price,
        pe: info.pe,
        pb: info.pb,
        marketCap: info.marketCap,
        revenue: finance.revenue,
        revenueYoy: finance.revenueYoy,
        netProfit: finance.netProfit,
        netProfitYoy: finance.netProfitYoy,
        roe: finance.roe,
        grossMargin: finance.grossMargin,
        reportDate: finance.reportDate
      });
    } catch (error) {
      console.error(`获取 ${code} 数据失败:`, error.message);
      results.push({ code, error: error.message });
    }
  }
  return results;
}

// 导出函数
module.exports = {
  getStockInfo,
  getMainFinance,
  getAnnouncements,
  getBatchFinance
};
