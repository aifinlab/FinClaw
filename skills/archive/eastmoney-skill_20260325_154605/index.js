/**
 * Eastmoney Skill - 东方财富数据接口兼容层
 * 使用 akshare-stock 数据作为替代源
 */

const { execSync } = require('child_process');
const path = require('path');

const SCRIPTS_DIR = path.join(__dirname, '../akshare-stock/scripts');

/**
 * 获取股票基本信息
 * @param {string} code - 股票代码
 * @returns {Promise<Object>}
 */
async function getStockInfo(code) {
  try {
    const script = path.join(SCRIPTS_DIR, 'stock_quote_tx.py');
    
    const result = execSync(`python3 "${script}" ${code}`, {
      encoding: 'utf8',
      timeout: 15000
    });
    
    // 解析 JSON 输出
    const lines = result.split('\n');
    const metaLine = lines.findIndex(l => l.includes('##QUOTE_META##'));
    
    if (metaLine === -1 || metaLine + 1 >= lines.length) {
      throw new Error('No stock info found');
    }
    
    const quoteData = JSON.parse(lines[metaLine + 1]);
    
    return {
      code: quoteData.code,
      name: quoteData.name,
      price: quoteData.price,
      industry: '未知', // 腾讯接口不返回行业
      market: code.startsWith('6') ? 'SH' : 'SZ'
    };
  } catch (error) {
    console.error('getStockInfo error:', error.message);
    // Fallback
    return {
      code: code,
      name: code,
      price: 0,
      industry: '未知',
      market: code.startsWith('6') ? 'SH' : 'SZ'
    };
  }
}

module.exports = {
  getStockInfo
};
