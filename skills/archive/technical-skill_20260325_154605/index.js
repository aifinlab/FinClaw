/**
 * Technical Skill - 技术指标计算
 * 提供常用技术分析指标计算
 */

/**
 * 计算RSI指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object}
 */
function calculateRSI(closes, period = 14) {
  if (closes.length < period + 1) {
    return { rsi: 50, gain: 0, loss: 0 };
  }
  
  let gains = 0;
  let losses = 0;
  
  // 计算初始平均涨跌
  for (let i = 1; i <= period; i++) {
    const change = closes[closes.length - i] - closes[closes.length - i - 1];
    if (change > 0) gains += change;
    else losses += Math.abs(change);
  }
  
  const avgGain = gains / period;
  const avgLoss = losses / period;
  
  if (avgLoss === 0) return { rsi: 100, gain: avgGain, loss: 0 };
  
  const rs = avgGain / avgLoss;
  const rsi = 100 - (100 / (1 + rs));
  
  return { rsi: Math.round(rsi * 100) / 100, gain: avgGain, loss: avgLoss };
}

/**
 * 计算KDJ指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @returns {Object}
 */
function calculateKDJ(highs, lows, closes, n = 9, m1 = 3, m2 = 3) {
  if (closes.length < n) {
    return { k: 50, d: 50, j: 50 };
  }
  
  const RSVs = [];
  for (let i = n - 1; i < closes.length; i++) {
    const sliceHighs = highs.slice(i - n + 1, i + 1);
    const sliceLows = lows.slice(i - n + 1, i + 1);
    const close = closes[i];
    
    const highest = Math.max(...sliceHighs);
    const lowest = Math.min(...sliceLows);
    
    const rsv = highest === lowest ? 50 : ((close - lowest) / (highest - lowest)) * 100;
    RSVs.push(rsv);
  }
  
  // 计算K, D, J
  let k = 50;
  let d = 50;
  
  for (let i = 0; i < RSVs.length; i++) {
    k = (2 / 3) * k + (1 / 3) * RSVs[i];
    d = (2 / 3) * d + (1 / 3) * k;
  }
  
  const j = 3 * k - 2 * d;
  
  return {
    k: Math.round(k * 100) / 100,
    d: Math.round(d * 100) / 100,
    j: Math.round(j * 100) / 100
  };
}

/**
 * 计算MACD指标
 * @param {Array<number>} closes - 收盘价数组
 * @returns {Object}
 */
function calculateMACD(closes, short = 12, long = 26, signal = 9) {
  if (closes.length < long) {
    return { dif: 0, dea: 0, macd: 0 };
  }
  
  const ema = (data, period) => {
    const k = 2 / (period + 1);
    let emaValue = data[0];
    const emas = [emaValue];
    
    for (let i = 1; i < data.length; i++) {
      emaValue = data[i] * k + emaValue * (1 - k);
      emas.push(emaValue);
    }
    
    return emas;
  };
  
  const emaShort = ema(closes, short);
  const emaLong = ema(closes, long);
  
  const difs = [];
  for (let i = 0; i < emaShort.length; i++) {
    difs.push(emaShort[i] - emaLong[i]);
  }
  
  const deaList = ema(difs, signal);
  const dif = difs[difs.length - 1];
  const dea = deaList[deaList.length - 1];
  const macd = (dif - dea) * 2;
  
  return {
    dif: Math.round(dif * 1000) / 1000,
    dea: Math.round(dea * 1000) / 1000,
    macd: Math.round(macd * 1000) / 1000
  };
}

/**
 * 计算布林带(BOLL)指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认20
 * @param {number} stdDev - 标准差倍数，默认2
 * @returns {Object}
 */
function calculateBOLL(closes, period = 20, stdDev = 2) {
  if (closes.length < period) {
    const last = closes[closes.length - 1] || 100;
    return { upper: last * 1.05, middle: last, lower: last * 0.95 };
  }
  
  const recent = closes.slice(-period);
  const middle = recent.reduce((a, b) => a + b, 0) / period;
  
  const variance = recent.reduce((sum, price) => sum + Math.pow(price - middle, 2), 0) / period;
  const std = Math.sqrt(variance);
  
  return {
    upper: Math.round((middle + stdDev * std) * 100) / 100,
    middle: Math.round(middle * 100) / 100,
    lower: Math.round((middle - stdDev * std) * 100) / 100
  };
}

/**
 * 计算简单移动平均(SMA)
 * @param {Array<number>} data - 数据数组
 * @param {number} period - 周期
 * @returns {number}
 */
function calculateSMA(data, period) {
  if (data.length < period) return data[data.length - 1] || 0;
  const sum = data.slice(-period).reduce((a, b) => a + b, 0);
  return Math.round((sum / period) * 100) / 100;
}

module.exports = {
  calculateRSI,
  calculateKDJ,
  calculateMACD,
  calculateBOLL,
  calculateSMA
};
