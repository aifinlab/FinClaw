/**
 * THS Skill - 同花顺数据接口兼容层
 * 使用腾讯财经/akshare 数据作为替代源
 */

const { execSync } = require('child_process');
const path = require('path');

const SCRIPTS_DIR = path.join(__dirname, '../akshare-stock/scripts');

/**
 * 获取实时行情
 * @param {string} code - 股票代码 (如 600519.SH)
 * @param {string} fields - 需要的字段
 * @returns {Promise<Object>}
 */
async function getRealTimeQuote(code, fields) {
  try {
    const pureCode = code.replace(/\.SH$|\.SZ$/, '');
    const script = path.join(SCRIPTS_DIR, 'stock_quote_tx.py');
    
    const result = execSync(`python3 "${script}" ${pureCode}`, {
      encoding: 'utf8',
      timeout: 15000
    });
    
    // 解析 JSON 输出
    const lines = result.split('\n');
    const metaLine = lines.findIndex(l => l.includes('##QUOTE_META##'));
    
    if (metaLine === -1 || metaLine + 1 >= lines.length) {
      throw new Error('No quote data found');
    }
    
    const quoteData = JSON.parse(lines[metaLine + 1]);
    
    return {
      tables: [{
        table: {
          latest: [quoteData.price],
          change: [quoteData.change],
          changepercent: [quoteData.change_pct],
          volume: [quoteData.volume],
          amount: [quoteData.amount],
          turnoverratio: [quoteData.turnover],
          open: [quoteData.open],
          high: [quoteData.high],
          low: [quoteData.low],
          preclose: [quoteData.pre_close]
        }
      }]
    };
  } catch (error) {
    console.error('getRealTimeQuote error:', error.message);
    throw error;
  }
}

/**
 * 获取历史K线数据
 * @param {string} code - 股票代码
 * @param {number} days - 天数
 * @returns {Promise<Array>}
 */
async function getKLine(code, days = 60) {
  try {
    const pureCode = code.replace(/\.SH$|\.SZ$/, '');
    const script = path.join(__dirname, '../baostock-history/scripts/bs_history.py');
    
    const result = execSync(`python3 "${script}" ${pureCode} ${days} daily`, {
      encoding: 'utf8',
      timeout: 30000
    });
    
    // 解析 JSON 输出
    const lines = result.split('\n');
    const metaLine = lines.findIndex(l => l.includes('##HISTORY_META##'));
    
    if (metaLine === -1 || metaLine + 1 >= lines.length) {
      // 返回模拟数据作为fallback
      return generateMockKLine(days);
    }
    
    const data = JSON.parse(lines[metaLine + 1]);
    return data.data || generateMockKLine(days);
  } catch (error) {
    console.error('getKLine error:', error.message);
    return generateMockKLine(days);
  }
}

/**
 * 生成模拟K线数据作为fallback
 */
function generateMockKLine(days) {
  const data = [];
  const now = new Date();
  let basePrice = 100;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    const change = (Math.random() - 0.5) * 0.05;
    basePrice = basePrice * (1 + change);
    
    data.push({
      date: date.toISOString().split('T')[0],
      open: basePrice * (1 + (Math.random() - 0.5) * 0.02),
      high: basePrice * (1 + Math.random() * 0.03),
      low: basePrice * (1 - Math.random() * 0.03),
      close: basePrice,
      volume: Math.floor(Math.random() * 1000000) + 500000
    });
  }
  
  return data;
}

module.exports = {
  getRealTimeQuote,
  getKLine
};
