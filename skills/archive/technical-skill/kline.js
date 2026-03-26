/**
 * KLine Data Module
 * 获取股票历史K线数据
 */

const fetch = require('node-fetch');
const iconv = require('iconv-lite');

/**
 * 获取股票历史K线数据（腾讯财经）
 * @param {string} stockCode - 股票代码
 * @param {number} days - 获取天数，默认60
 * @returns {Promise<Array>} K线数据 { date, open, high, low, close, volume }
 */
async function getKLineData(stockCode, days = 60) {
  const prefix = stockCode.startsWith('6') ? 'sh' : 'sz';
  const url = `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${prefix}${stockCode},day,,,${days},qfq`;
  
  const response = await fetch(url, { timeout: 15000 });
  const data = await response.json();
  
  const key = `${prefix}${stockCode}`;
  if (!data.data || !data.data[key] || !data.data[key].qfqday) {
    throw new Error(`未找到 ${stockCode} 的K线数据`);
  }
  
  const klines = data.data[key].qfqday;
  return klines.map(item => ({
    date: item[0],
    open: parseFloat(item[1]),
    close: parseFloat(item[2]),
    low: parseFloat(item[3]),
    high: parseFloat(item[4]),
    volume: parseInt(item[5])
  }));
}

/**
 * 获取股票实时数据
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 实时数据
 */
async function getRealTimeData(stockCode) {
  const prefix = stockCode.startsWith('6') ? 'sh' : 'sz';
  const url = `https://qt.gtimg.cn/q=${prefix}${stockCode}`;
  
  const response = await fetch(url, { timeout: 10000 });
  const buffer = await response.buffer();
  const text = iconv.decode(buffer, 'gb2312');
  
  const match = text.match(new RegExp(`v_${prefix}${stockCode}="([^"]+)"`));
  if (!match) {
    throw new Error(`未找到股票 ${stockCode} 的信息`);
  }
  
  const parts = match[1].split('~');
  return {
    code: stockCode,
    name: parts[1],
    price: parseFloat(parts[3]),
    change: parseFloat(parts[31]),
    changePercent: parseFloat(parts[32]),
    volume: parseInt(parts[36]),
    turnover: parseFloat(parts[37]),
    high: parseFloat(parts[33]),
    low: parseFloat(parts[34]),
    open: parseFloat(parts[5]),
    prevClose: parseFloat(parts[4]),
    marketCap: (parseFloat(parts[44]) || 0) * 1e8,
    pe: parseFloat(parts[39]) || null,
    pb: parseFloat(parts[46]) || null
  };
}

/**
 * 批量获取多只股票K线
 * @param {Array<string>} stockCodes - 股票代码列表
 * @param {number} days - 天数
 * @returns {Promise<Object>} 以股票代码为key的K线数据
 */
async function getBatchKLine(stockCodes, days = 60) {
  const result = {};
  for (const code of stockCodes) {
    try {
      result[code] = await getKLineData(code, days);
    } catch (error) {
      console.error(`获取 ${code} K线失败:`, error.message);
      result[code] = null;
    }
  }
  return result;
}

// 导出函数
module.exports = {
  getKLineData,
  getRealTimeData,
  getBatchKLine
};
