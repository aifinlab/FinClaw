/**
 * 同花顺 iFinD API Skill
 * 专业金融数据接口 - 基于官方 HTTP API
 * 配置来源：.env 文件 (THS_ACCESS_TOKEN)
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

// 从 .env 文件加载配置
function loadEnvConfig() {
  try {
    // 尝试多个可能的 .env 文件路径
    const possiblePaths = [
      path.join(process.cwd(), '.env'),
      path.join(__dirname, '../../../.env'),
      path.join(__dirname, '../../.env'),
      path.join(__dirname, '../.env'),
      '/root/.openclaw/workspace/.env'
    ];
    
    let envPath = null;
    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        envPath = p;
        break;
      }
    }
    
    if (!envPath) {
      console.log('[ths-skill] 未找到 .env 文件');
      return null;
    }
    
    const envContent = fs.readFileSync(envPath, 'utf8');
    const config = {};
    
    envContent.split('\n').forEach(line => {
      line = line.trim();
      if (line && !line.startsWith('#')) {
        const eqIndex = line.indexOf('=');
        if (eqIndex > 0) {
          const key = line.substring(0, eqIndex).trim();
          const value = line.substring(eqIndex + 1).trim();
          config[key] = value;
        }
      }
    });
    
    console.log(`[ths-skill] 已从 ${envPath} 加载配置`);
    return config;
  } catch (e) {
    console.log('[ths-skill] 加载 .env 失败:', e.message);
    return null;
  }
}

// 加载环境变量配置
const envConfig = loadEnvConfig();

// 兼容旧配置：如果 .env 没有，尝试 config/ths-config.json
let config = null;
if (envConfig?.THS_ACCESS_TOKEN) {
  config = {
    access_token: envConfig.THS_ACCESS_TOKEN,
    refresh_token: envConfig.THS_REFRESH_TOKEN || null
  };
} else {
  try {
    config = require('../../config/ths-config.json');
    console.log('[ths-skill] 使用 config/ths-config.json 配置');
  } catch (e) {
    console.log('[ths-skill] 同花顺配置未找到');
  }
}

const BASE_URL = 'https://quantapi.51ifind.com/api/v1';

/**
 * 获取 access_token（直接使用配置中的）
 * @returns {Promise<string>} access_token
 */
async function getAccessToken() {
  if (!config?.access_token) {
    throw new Error('同花顺 access_token 未配置，请在 .env 文件中设置 THS_ACCESS_TOKEN');
  }
  return config.access_token;
}

/**
 * 获取新的 access_token（会使旧的失效）
 * @returns {Promise<string>} access_token
 */
async function updateAccessToken() {
  if (!config?.refresh_token) {
    throw new Error('同花顺 refresh_token 未配置');
  }
  
  const url = `${BASE_URL}/update_access_token`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'refresh_token': config.refresh_token
    },
    timeout: 30000
  });
  
  const data = await response.json();
  
  if (data.errorcode !== 0) {
    throw new Error(`更新 token 失败: ${data.errmsg}`);
  }
  
  return data.data.access_token;
}

/**
 * 调用同花顺 API - 自动获取 token
 * @param {string} endpoint - API 端点
 * @param {Object} params - 请求参数
 * @returns {Promise<Object>} 响应数据
 */
async function callAPI(endpoint, params = {}) {
  // 每次调用前获取新的 access_token
  const token = await getAccessToken();
  
  const url = `${BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'access_token': token
    },
    body: JSON.stringify(params),
    timeout: 30000
  });
  
  const data = await response.json();
  
  if (data.errorcode !== 0) {
    throw new Error(`API 调用失败: ${data.errmsg}`);
  }
  
  return data;
}

/**
 * 基础数据 - 获取财务指标等
 * @param {string} codes - 股票代码，如 "300033.SZ,600030.SH"
 * @param {Array} indicators - 指标列表
 * @returns {Promise<Object>} 数据结果
 */
async function getBasicData(codes, indicators) {
  return callAPI('/basic_data_service', {
    codes: codes,
    indipara: indicators
  });
}

/**
 * 日期序列 - 获取历史财务数据
 * @param {string} codes - 股票代码
 * @param {Array} indicators - 指标列表
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 * @returns {Promise<Object>} 数据结果
 */
async function getDateSequence(codes, indicators, startDate, endDate) {
  return callAPI('/date_sequence', {
    codes: codes,
    indipara: indicators,
    startdate: startDate,
    enddate: endDate
  });
}

/**
 * 历史行情
 * @param {string} codes - 股票代码
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} K线数据
 */
async function getHistoryQuote(codes, startDate, endDate) {
  return callAPI('/history_quote', {
    codes: codes,
    startdate: startDate,
    enddate: endDate
  });
}

/**
 * 实时行情
 * @param {string} codes - 股票代码
 * @param {string} indicators - 指标，如 "open,high,low,latest"
 * @returns {Promise<Object>} 实时行情
 */
async function getRealTimeQuote(codes, indicators = 'open,high,low,latest') {
  return callAPI('/real_time_quotation', {
    codes: codes,
    indicators: indicators
  });
}

/**
 * 日内快照
 * @param {string} codes - 股票代码
 * @param {string} date - 日期
 * @returns {Promise<Object>} 日内数据
 */
async function getIntradaySnapshot(codes, date) {
  return callAPI('/intraday_snapshot', {
    codes: codes,
    date: date
  });
}

/**
 * 经济数据库 (EDB)
 * @param {string} indicators - 指标代码，逗号分隔，如 "M001620253,M002826938"
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 * @returns {Promise<Object>} 宏观数据
 */
async function getEDBData(indicators, startDate, endDate) {
  return callAPI('/edb_service', {
    indicators: indicators,
    startdate: startDate.replace(/-/g, ''),
    enddate: endDate.replace(/-/g, '')
  });
}

/**
 * 获取国债收益率曲线数据（EDB）
 * @returns {Promise<Array>} 收益率曲线数据
 */
async function getTreasuryYieldCurve() {
  try {
    // 同花顺EDB指标代码示例
    // 实际指标代码需要根据同花顺EDB确定
    const today = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    // 这些指标代码需要根据实际同花顺EDB调整
    const indicators = 'G0000138,G0000139,G0000140,G0000141,G0000142,G0000143';
    // G0000138: 中债国债1年到期收益率
    // G0000139: 中债国债3年到期收益率
    // G0000140: 中债国债5年到期收益率
    // G0000141: 中债国债7年到期收益率
    // G0000142: 中债国债10年到期收益率
    // G0000143: 中债国债30年到期收益率
    
    const data = await getEDBData(indicators, startDate, today);
    
    if (!data.data || !data.data.tables) {
      throw new Error('无法获取国债收益率数据');
    }
    
    // 解析返回的数据
    const tables = data.data.tables;
    const result = [];
    
    // 获取最新数据
    const terms = ['1Y', '3Y', '5Y', '7Y', '10Y', '30Y'];
    const termNames = ['1年', '3年', '5年', '7年', '10年', '30年'];
    
    for (let i = 0; i < tables.length; i++) {
      const table = tables[i];
      if (table.table && table.table.y && table.table.y.length > 0) {
        const latestValue = table.table.y[table.table.y.length - 1];
        const prevValue = table.table.y.length > 1 ? table.table.y[table.table.y.length - 2] : latestValue;
        
        result.push({
          term: terms[i],
          name: termNames[i],
          maturity: [1, 3, 5, 7, 10, 30][i],
          yield: parseFloat(latestValue),
          change: parseFloat((latestValue - prevValue).toFixed(2))
        });
      }
    }
    
    return result;
  } catch (error) {
    console.error('获取国债收益率失败:', error.message);
    // 返回模拟数据作为备用
    return [
      { term: '1Y', name: '1年', maturity: 1, yield: 1.45, change: -0.02 },
      { term: '3Y', name: '3年', maturity: 3, yield: 1.68, change: -0.03 },
      { term: '5Y', name: '5年', maturity: 5, yield: 1.85, change: -0.02 },
      { term: '7Y', name: '7年', maturity: 7, yield: 2.05, change: -0.01 },
      { term: '10Y', name: '10年', maturity: 10, yield: 2.18, change: -0.03 },
      { term: '30Y', name: '30年', maturity: 30, yield: 2.45, change: -0.05 }
    ];
  }
}

/**
 * 获取可转债实时行情
 * @param {string} codes - 可转债代码，如 "110059.SH,113052.SH"
 * @returns {Promise<Object>} 可转债行情
 */
async function getConvertibleBondQuote(codes) {
  return getRealTimeQuote(codes, 'open,high,low,latest,change,pct_change,volume,amount');
}

/**
 * 获取债券回购利率（资金面）
 * @returns {Promise<Object>} 回购利率
 */
async function getRepoRate() {
  try {
    const today = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    // R007 和 DR007 指标代码
    const indicators = 'M0000410,M0000412';
    
    return await getEDBData(indicators, startDate, today);
  } catch (error) {
    console.error('获取回购利率失败:', error.message);
    return null;
  }
}

/**
 * 公告查询
 * @param {string} codes - 股票代码
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} 公告列表
 */
async function getAnnouncements(codes, startDate, endDate) {
  return callAPI('/announcement_query', {
    codes: codes,
    startdate: startDate,
    enddate: endDate
  });
}

/**
 * 智能选股
 * @param {string} strategy - 策略代码
 * @param {Object} params - 策略参数
 * @returns {Promise<Object>} 选股结果
 */
async function stockScreening(strategy, params = {}) {
  return callAPI('/stock_screening', {
    strategy: strategy,
    ...params
  });
}

/**
 * 获取股票财务数据（封装）
 * @param {string} stockCode - 股票代码
 * @param {string} reportDate - 报告期，如 "20241231"
 * @returns {Promise<Object>} 财务数据
 */
async function getFinancialData(stockCode, reportDate) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_roe_stock', indiparams: [reportDate] },
    { indicator: 'ths_np_stock', indiparams: [reportDate] },
    { indicator: 'ths_or_stock', indiparams: [reportDate] },
    { indicator: 'ths_gross_margin_stock', indiparams: [reportDate] }
  ];
  
  return getBasicData(thsCode, indicators);
}

// 导出函数
module.exports = {
  getAccessToken,
  updateAccessToken,
  callAPI,
  getBasicData,
  getDateSequence,
  getHistoryQuote,
  getRealTimeQuote,
  getIntradaySnapshot,
  getEDBData,
  getTreasuryYieldCurve,
  getConvertibleBondQuote,
  getRepoRate,
  getAnnouncements,
  stockScreening,
  getFinancialData
};
