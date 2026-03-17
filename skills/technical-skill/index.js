/**
 * Technical Analysis Module
 * 技术指标计算模块
 * 
 * 支持指标：
 * - MA: 移动平均线
 * - MACD: 指数平滑异同平均线
 * - KDJ: 随机指标
 * - RSI: 相对强弱指标
 * - BOLL: 布林带
 */

/**
 * 计算简单移动平均线 (SMA)
 * @param {Array<number>} data - 价格数组
 * @param {number} period - 周期
 * @returns {Array<number>} 移动平均线
 */
function calculateSMA(data, period) {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
      continue;
    }
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j];
    }
    result.push(sum / period);
  }
  return result;
}

/**
 * 计算指数移动平均线 (EMA)
 * @param {Array<number>} data - 价格数组
 * @param {number} period - 周期
 * @returns {Array<number>} EMA数组
 */
function calculateEMA(data, period) {
  const result = [];
  const multiplier = 2 / (period + 1);
  
  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push(data[i]);
    } else {
      const ema = (data[i] - result[i - 1]) * multiplier + result[i - 1];
      result.push(ema);
    }
  }
  return result;
}

/**
 * 计算 MACD 指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} fastPeriod - 快线周期，默认12
 * @param {number} slowPeriod - 慢线周期，默认26
 * @param {number} signalPeriod - 信号线周期，默认9
 * @returns {Object} MACD指标 { dif, dea, macd }
 */
function calculateMACD(closes, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
  const ema12 = calculateEMA(closes, fastPeriod);
  const ema26 = calculateEMA(closes, slowPeriod);
  
  // DIF = EMA12 - EMA26
  const dif = ema12.map((v, i) => v !== null && ema26[i] !== null ? v - ema26[i] : null);
  
  // DEA = DIF的EMA9
  const validDif = dif.filter(v => v !== null);
  const deaValues = calculateEMA(validDif, signalPeriod);
  const dea = new Array(dif.length - validDif.length).fill(null).concat(deaValues);
  
  // MACD = (DIF - DEA) * 2
  const macd = dif.map((v, i) => v !== null && dea[i] !== null ? (v - dea[i]) * 2 : null);
  
  return {
    dif: dif[dif.length - 1],
    dea: dea[dea.length - 1],
    macd: macd[macd.length - 1],
    history: { dif, dea, macd }
  };
}

/**
 * 计算 KDJ 指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} n - RSV周期，默认9
 * @param {number} m1 - K平滑因子，默认3
 * @param {number} m2 - D平滑因子，默认3
 * @returns {Object} KDJ指标 { k, d, j }
 */
function calculateKDJ(highs, lows, closes, n = 9, m1 = 3, m2 = 3) {
  const k = [];
  const d = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < n - 1) {
      k.push(null);
      d.push(null);
      continue;
    }
    
    // 计算N日内的最高价和最低价
    let highN = highs[i];
    let lowN = lows[i];
    for (let j = 1; j < n; j++) {
      highN = Math.max(highN, highs[i - j]);
      lowN = Math.min(lowN, lows[i - j]);
    }
    
    // RSV = (收盘价 - N日内最低价) / (N日内最高价 - N日内最低价) * 100
    let rsv = 0;
    if (highN !== lowN) {
      rsv = ((closes[i] - lowN) / (highN - lowN)) * 100;
    }
    
    // K = (2/3) * 昨日K + (1/3) * 今日RSV
    // D = (2/3) * 昨日D + (1/3) * 今日K
    if (i === n - 1 || k.length === 0 || k[k.length - 1] === null) {
      k.push(rsv);
      d.push(rsv);
    } else {
      const kValue = Math.max(0, Math.min(100, (2 / 3) * k[k.length - 1] + (1 / 3) * rsv));
      const dValue = Math.max(0, Math.min(100, (2 / 3) * d[d.length - 1] + (1 / 3) * kValue));
      k.push(kValue);
      d.push(dValue);
    }
  }
  
  // J = 3K - 2D
  const j = k.map((v, i) => v !== null && d[i] !== null ? 3 * v - 2 * d[i] : null);
  
  return {
    k: k[k.length - 1],
    d: d[d.length - 1],
    j: j[j.length - 1],
    history: { k, d, j }
  };
}

/**
 * 计算 RSI 相对强弱指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object} RSI指标 { rsi }
 */
function calculateRSI(closes, period = 14) {
  const gains = [];
  const losses = [];
  
  // 计算涨跌
  for (let i = 1; i < closes.length; i++) {
    const change = closes[i] - closes[i - 1];
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? -change : 0);
  }
  
  const rsi = [];
  let avgGain = 0;
  let avgLoss = 0;
  
  for (let i = 0; i < gains.length; i++) {
    if (i < period - 1) {
      rsi.push(null);
      continue;
    }
    
    if (i === period - 1) {
      // 初始平均值
      avgGain = gains.slice(0, period).reduce((a, b) => a + b, 0) / period;
      avgLoss = losses.slice(0, period).reduce((a, b) => a + b, 0) / period;
    } else {
      // 平滑移动平均
      avgGain = (avgGain * (period - 1) + gains[i]) / period;
      avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
    }
    
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }
  
  return {
    rsi: rsi[rsi.length - 1],
    history: rsi
  };
}

/**
 * 计算布林带 (BOLL)
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认20
 * @param {number} stdDev - 标准差倍数，默认2
 * @returns {Object} BOLL指标 { upper, middle, lower }
 */
function calculateBOLL(closes, period = 20, stdDev = 2) {
  const middle = calculateSMA(closes, period);
  const upper = [];
  const lower = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period - 1) {
      upper.push(null);
      lower.push(null);
      continue;
    }
    
    // 计算标准差
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += Math.pow(closes[i - j] - middle[i], 2);
    }
    const std = Math.sqrt(sum / period);
    
    upper.push(middle[i] + stdDev * std);
    lower.push(middle[i] - stdDev * std);
  }
  
  return {
    upper: upper[upper.length - 1],
    middle: middle[middle.length - 1],
    lower: lower[lower.length - 1],
    history: { upper, middle, lower }
  };
}

/**
 * 获取技术指标信号
 * @param {Object} indicators - 技术指标对象
 * @returns {Object} 买卖信号
 */
function getSignals(indicators) {
  const signals = {
    macd: 'neutral',
    kdj: 'neutral',
    rsi: 'neutral',
    boll: 'neutral',
    overall: 'neutral'
  };
  
  // MACD信号
  if (indicators.macd && indicators.macd.macd > 0 && indicators.macd.dif > indicators.macd.dea) {
    signals.macd = 'bullish';
  } else if (indicators.macd && indicators.macd.macd < 0 && indicators.macd.dif < indicators.macd.dea) {
    signals.macd = 'bearish';
  }
  
  // KDJ信号
  if (indicators.kdj) {
    if (indicators.kdj.j < 0) signals.kdj = 'oversold';
    else if (indicators.kdj.j > 100) signals.kdj = 'overbought';
    else if (indicators.kdj.k > indicators.kdj.d) signals.kdj = 'bullish';
    else signals.kdj = 'bearish';
  }
  
  // RSI信号
  if (indicators.rsi) {
    if (indicators.rsi.rsi < 30) signals.rsi = 'oversold';
    else if (indicators.rsi.rsi > 70) signals.rsi = 'overbought';
    else signals.rsi = 'neutral';
  }
  
  // 综合信号
  const bullishCount = [signals.macd, signals.kdj, signals.rsi].filter(s => s === 'bullish' || s === 'oversold').length;
  const bearishCount = [signals.macd, signals.kdj, signals.rsi].filter(s => s === 'bearish' || s === 'overbought').length;
  
  if (bullishCount >= 2) signals.overall = 'bullish';
  else if (bearishCount >= 2) signals.overall = 'bearish';
  
  return signals;
}

/**
 * 计算 CCI 顺势指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object} CCI指标 { cci }
 */
function calculateCCI(highs, lows, closes, period = 14) {
  const tp = []; // Typical Price = (High + Low + Close) / 3
  for (let i = 0; i < closes.length; i++) {
    tp.push((highs[i] + lows[i] + closes[i]) / 3);
  }
  
  const cci = [];
  for (let i = 0; i < tp.length; i++) {
    if (i < period - 1) {
      cci.push(null);
      continue;
    }
    
    // 计算SMA
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += tp[i - j];
    }
    const sma = sum / period;
    
    // 计算平均绝对偏差
    let madSum = 0;
    for (let j = 0; j < period; j++) {
      madSum += Math.abs(tp[i - j] - sma);
    }
    const mad = madSum / period;
    
    // CCI = (TP - SMA) / (0.015 * MAD)
    if (mad === 0) {
      cci.push(0);
    } else {
      cci.push((tp[i] - sma) / (0.015 * mad));
    }
  }
  
  return {
    cci: cci[cci.length - 1],
    history: cci
  };
}

/**
 * 计算威廉指标 (WR)
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object} WR指标 { wr }
 */
function calculateWR(highs, lows, closes, period = 14) {
  const wr = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period - 1) {
      wr.push(null);
      continue;
    }
    
    // N日最高价和最低价
    let highN = highs[i];
    let lowN = lows[i];
    for (let j = 1; j < period; j++) {
      highN = Math.max(highN, highs[i - j]);
      lowN = Math.min(lowN, lows[i - j]);
    }
    
    // WR = (HN - C) / (HN - LN) * -100
    if (highN === lowN) {
      wr.push(-50);
    } else {
      wr.push(((highN - closes[i]) / (highN - lowN)) * -100);
    }
  }
  
  return {
    wr: wr[wr.length - 1],
    history: wr
  };
}

/**
 * 计算 OBV 能量潮指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {Array<number>} volumes - 成交量数组
 * @returns {Object} OBV指标 { obv, obvMA }
 */
function calculateOBV(closes, volumes) {
  const obv = [volumes[0]];
  
  for (let i = 1; i < closes.length; i++) {
    if (closes[i] > closes[i - 1]) {
      obv.push(obv[i - 1] + volumes[i]);
    } else if (closes[i] < closes[i - 1]) {
      obv.push(obv[i - 1] - volumes[i]);
    } else {
      obv.push(obv[i - 1]);
    }
  }
  
  // OBV的MA30
  const obvMA = calculateSMA(obv, 30);
  
  return {
    obv: obv[obv.length - 1],
    obvMA: obvMA[obvMA.length - 1],
    history: obv
  };
}

/**
 * 计算 DMI 趋向指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object} DMI指标 { pdi, mdi, adx }
 */
function calculateDMI(highs, lows, closes, period = 14) {
  const tr = []; // True Range
  const plusDM = []; // +DM
  const minusDM = []; // -DM
  
  for (let i = 1; i < closes.length; i++) {
    // TR = max(|High - Low|, |High - Close_prev|, |Low - Close_prev|)
    const tr1 = highs[i] - lows[i];
    const tr2 = Math.abs(highs[i] - closes[i - 1]);
    const tr3 = Math.abs(lows[i] - closes[i - 1]);
    tr.push(Math.max(tr1, tr2, tr3));
    
    // +DM = High - High_prev (if > 0 and > Low_prev - Low)
    const upMove = highs[i] - highs[i - 1];
    const downMove = lows[i - 1] - lows[i];
    plusDM.push(upMove > downMove && upMove > 0 ? upMove : 0);
    minusDM.push(downMove > upMove && downMove > 0 ? downMove : 0);
  }
  
  // 计算平滑移动平均
  const atr = calculateEMA(tr, period);
  const plusDI = calculateEMA(plusDM, period).map((v, i) => atr[i] > 0 ? (v / atr[i]) * 100 : 0);
  const minusDI = calculateEMA(minusDM, period).map((v, i) => atr[i] > 0 ? (v / atr[i]) * 100 : 0);
  
  // DX = |+DI - -DI| / (+DI + -DI) * 100
  const dx = plusDI.map((v, i) => {
    const sum = v + minusDI[i];
    return sum > 0 ? (Math.abs(v - minusDI[i]) / sum) * 100 : 0;
  });
  
  // ADX = DX的EMA
  const adx = calculateEMA(dx, period);
  
  return {
    pdi: plusDI[plusDI.length - 1],
    mdi: minusDI[minusDI.length - 1],
    adx: adx[adx.length - 1],
    history: { pdi: plusDI, mdi: minusDI, adx }
  };
}

/**
 * 计算 SAR 抛物线转向指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {number} af - 加速因子，默认0.02
 * @param {number} maxAf - 最大加速因子，默认0.2
 * @returns {Object} SAR指标 { sar, trend }
 */
function calculateSAR(highs, lows, af = 0.02, maxAf = 0.2) {
  const sar = [];
  let isLong = true; // 是否多头
  let ep = highs[0]; // 极值点
  let currentAf = af;
  let currentSAR = lows[0];
  
  for (let i = 0; i < highs.length; i++) {
    if (i === 0) {
      sar.push(currentSAR);
      continue;
    }
    
    // 计算SAR
    currentSAR = currentSAR + currentAf * (ep - currentSAR);
    
    // 限制SAR在当前周期高低点之间
    if (isLong) {
      currentSAR = Math.min(currentSAR, lows[i - 1], lows[i] || lows[i - 1]);
      if (lows[i] < currentSAR) {
        // 转空
        isLong = false;
        currentSAR = ep;
        ep = lows[i];
        currentAf = af;
      } else if (highs[i] > ep) {
        ep = highs[i];
        currentAf = Math.min(currentAf + af, maxAf);
      }
    } else {
      currentSAR = Math.max(currentSAR, highs[i - 1], highs[i] || highs[i - 1]);
      if (highs[i] > currentSAR) {
        // 转多
        isLong = true;
        currentSAR = ep;
        ep = highs[i];
        currentAf = af;
      } else if (lows[i] < ep) {
        ep = lows[i];
        currentAf = Math.min(currentAf + af, maxAf);
      }
    }
    
    sar.push(currentSAR);
  }
  
  return {
    sar: sar[sar.length - 1],
    trend: isLong ? 'bullish' : 'bearish',
    history: sar
  };
}

/**
 * 计算 VR 成交量比率
 * @param {Array<number>} closes - 收盘价数组
 * @param {Array<number>} volumes - 成交量数组
 * @param {number} period - 周期，默认24
 * @returns {Object} VR指标 { vr }
 */
function calculateVR(closes, volumes, period = 24) {
  const vr = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period) {
      vr.push(null);
      continue;
    }
    
    let upVolume = 0;
    let downVolume = 0;
    let flatVolume = 0;
    
    for (let j = 0; j < period; j++) {
      const idx = i - j;
      if (closes[idx] > closes[idx - 1]) {
        upVolume += volumes[idx];
      } else if (closes[idx] < closes[idx - 1]) {
        downVolume += volumes[idx];
      } else {
        flatVolume += volumes[idx];
      }
    }
    
    const denominator = downVolume + flatVolume / 2;
    if (denominator === 0) {
      vr.push(100);
    } else {
      vr.push((upVolume + flatVolume / 2) / denominator * 100);
    }
  }
  
  return {
    vr: vr[vr.length - 1],
    history: vr
  };
}

/**
 * 计算 ATR 真实波幅指标
 * @param {Array<number>} highs - 最高价数组
 * @param {Array<number>} lows - 最低价数组
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认14
 * @returns {Object} ATR指标 { atr }
 */
function calculateATR(highs, lows, closes, period = 14) {
  const tr = []; // True Range
  
  for (let i = 0; i < closes.length; i++) {
    if (i === 0) {
      tr.push(highs[i] - lows[i]);
    } else {
      const tr1 = highs[i] - lows[i];
      const tr2 = Math.abs(highs[i] - closes[i - 1]);
      const tr3 = Math.abs(lows[i] - closes[i - 1]);
      tr.push(Math.max(tr1, tr2, tr3));
    }
  }
  
  // ATR = TR的EMA
  const atr = calculateEMA(tr, period);
  
  return {
    atr: atr[atr.length - 1],
    history: atr
  };
}

/**
 * 计算 PSY 心理线指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认12
 * @returns {Object} PSY指标 { psy }
 */
function calculatePSY(closes, period = 12) {
  const psy = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period) {
      psy.push(null);
      continue;
    }
    
    let upDays = 0;
    for (let j = 0; j < period; j++) {
      if (closes[i - j] > closes[i - j - 1]) {
        upDays++;
      }
    }
    
    psy.push((upDays / period) * 100);
  }
  
  return {
    psy: psy[psy.length - 1],
    history: psy
  };
}

/**
 * 计算 MTM 动量指标
 * @param {Array<number>} closes - 收盘价数组
 * @param {number} period - 周期，默认12
 * @returns {Object} MTM指标 { mtm, mtmMA }
 */
function calculateMTM(closes, period = 12) {
  const mtm = [];
  
  for (let i = 0; i < closes.length; i++) {
    if (i < period) {
      mtm.push(null);
    } else {
      mtm.push(closes[i] - closes[i - period]);
    }
  }
  
  // MTM的MA6
  const mtmMA = calculateSMA(mtm.filter(v => v !== null), 6);
  const validMtm = mtm.filter(v => v !== null);
  const padding = mtm.length - validMtm.length;
  const fullMtmMA = new Array(padding).fill(null).concat(mtmMA);
  
  return {
    mtm: mtm[mtm.length - 1],
    mtmMA: fullMtmMA[fullMtmMA.length - 1],
    history: mtm
  };
}

// 导出函数
module.exports = {
  calculateSMA,
  calculateEMA,
  calculateMACD,
  calculateKDJ,
  calculateRSI,
  calculateBOLL,
  calculateCCI,
  calculateWR,
  calculateOBV,
  calculateDMI,
  calculateSAR,
  calculateVR,
  calculateATR,
  calculatePSY,
  calculateMTM,
  getSignals
};
