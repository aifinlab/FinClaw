/** @format */
/**
 * Tencent Bond API - 腾讯财经债券数据接口
 * 提供债券实时行情数据
 */

const fetch = require('node-fetch');

/**
 * 获取债券实时行情
 * @param {string} code - 债券代码 (如 sh019547, sz123001)
 * @returns {Promise<Object>} 债券行情
 */
async function getBondQuote(code) {
  try {
    // 腾讯行情接口
    // code格式: sh+代码(上海) 或 sz+代码(深圳)
    const url = `https://qt.gtimg.cn/q=${code}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 10000
    });
    
    const text = await response.text();
    
    // 解析腾讯返回的数据格式
    // v_sh019547="1~16国债19~019547~115.140~115.238~115.221~..."
    const match = text.match(/v_\w+="([^"]+)"/);
    if (!match) {
      throw new Error('无法解析行情数据');
    }
    
    const fields = match[1].split('~');
    
    return {
      success: true,
      code: fields[2],
      name: fields[1],
      price: parseFloat(fields[3]) || 0,
      close: parseFloat(fields[4]) || 0,
      open: parseFloat(fields[5]) || 0,
      high: parseFloat(fields[33]) || 0,
      low: parseFloat(fields[34]) || 0,
      volume: parseInt(fields[6]) || 0,
      amount: parseInt(fields[37]) || 0,
      updateTime: fields[30],
    };
  } catch (error) {
    console.error('获取债券行情失败:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 批量获取债券行情
 * @param {Array<string>} codes - 债券代码数组
 * @returns {Promise<Array>} 债券行情列表
 */
async function getBatchBondQuotes(codes) {
  try {
    const codeStr = codes.join(',');
    const url = `https://qt.gtimg.cn/q=${codeStr}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 10000
    });
    
    const text = await response.text();
    const results = [];
    
    // 解析多行返回
    const lines = text.trim().split('\n');
    for (const line of lines) {
      const match = line.match(/v_(\w+)=\"([^\"]+)\"/);
      if (match) {
        const fields = match[2].split('~');
        results.push({
          code: fields[2],
          name: fields[1],
          price: parseFloat(fields[3]) || 0,
          close: parseFloat(fields[4]) || 0,
          open: parseFloat(fields[5]) || 0,
          change: parseFloat(fields[3] || 0) - parseFloat(fields[4] || 0),
          changePercent: ((parseFloat(fields[3] || 0) - parseFloat(fields[4] || 0)) / parseFloat(fields[4] || 1) * 100).toFixed(2),
          high: parseFloat(fields[33]) || 0,
          low: parseFloat(fields[34]) || 0,
          volume: parseInt(fields[6]) || 0,
          amount: parseInt(fields[37]) || 0,
          updateTime: fields[30],
        });
      }
    }
    
    return results;
  } catch (error) {
    console.error('批量获取债券行情失败:', error.message);
    return [];
  }
}

/**
 * 获取可转债指数行情
 * @returns {Promise<Object>} 可转债指数行情
 */
async function getConvertibleBondIndex() {
  try {
    // 中证转债指数代码: sh000832
    const result = await getBondQuote('sh000832');
    if (result.success) {
      return {
        index: result.price.toFixed(2),
        change: (result.price - result.close).toFixed(2),
        changePercent: ((result.price - result.close) / result.close * 100).toFixed(2),
        volume: result.volume,
        amount: result.amount,
        high: result.high.toFixed(2),
        low: result.low.toFixed(2),
      };
    }
    throw new Error('获取指数失败');
  } catch (error) {
    console.error('获取可转债指数失败:', error.message);
    return null;
  }
}

module.exports = {
  getBondQuote,
  getBatchBondQuotes,
  getConvertibleBondIndex,
};
