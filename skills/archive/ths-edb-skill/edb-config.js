/** @format */
/**
 * THS EDB 指标配置
 * 同花顺EDB指标代码管理
 * 
 * 使用说明:
 * 1. 在同花顺SuperCommand客户端 -> 经济数据库 -> 查找指标
 * 2. 右键指标 -> 生成命令 -> 复制指标代码
 * 3. 将代码配置到下方 EDB_INDICATORS 对象中
 */

// EDB指标代码配置
// 注意: 这些代码需要根据实际同花顺EDB配置
const EDB_INDICATORS = {
  // 经济增长
  gdp: {
    gdp_yoy: '',      // GDP:同比 - 请配置实际代码
    gdp_quarter: '',  // GDP:当季值
    gdp_accum: '',    // GDP:累计值
  },
  // 价格指数
  price: {
    cpi_yoy: '',      // CPI:同比
    cpi_mom: '',      // CPI:环比
    ppi_yoy: '',      // PPI:同比
    ppi_mom: '',      // PPI:环比
  },
  // 货币供应
  money: {
    m2_yoy: '',       // M2:同比
    m1_yoy: '',       // M1:同比
    m0_yoy: '',       // M0:同比
    loan_yoy: '',     // 贷款余额:同比
  },
  // PMI
  pmi: {
    manufacturing: '',  // 制造业PMI
    non_manufacturing: '', // 非制造业PMI
    new_orders: '',     // PMI:新订单
    production: '',     // PMI:生产
  },
  // 利率
  rates: {
    lpr_1y: '',         // LPR:1年期
    lpr_5y: '',         // LPR:5年期
    shibor_overnight: '', // SHIBOR:隔夜
    shibor_1w: '',      // SHIBOR:1周
    r007: '',           // 银行间回购定盘利率:R007
    dr007: '',          // 存款类机构质押式回购加权利率:DR007
  },
  // 汇率
  fx: {
    usdcny: '',         // 美元兑人民币中间价
    usdcny_spot: '',    // 美元兑人民币即期
    usd_index: '',      // 美元指数
  },
  // 商品价格
  commodities: {
    gold: '',           // 伦敦金现
    gold_sh: '',        // 上海黄金
    brent: '',          // 布伦特原油
    wti: '',            // WTI原油
    copper: '',         // LME铜
    iron_ore: '',       // 铁矿石
  },
  // 国债收益率
  bonds: {
    yield_1y: '',       // 中债国债1年到期收益率
    yield_5y: '',       // 中债国债5年到期收益率
    yield_10y: '',      // 中债国债10年到期收益率
    yield_30y: '',      // 中债国债30年到期收益率
    spread_10y1y: '',   // 期限利差(10Y-1Y)
  },
  // 美国股市
  us_market: {
    sp500: '',          // 标普500
    nasdaq: '',         // 纳斯达克指数
    dowjones: '',       // 道琼斯指数
    vix: '',            // VIX波动率
  },
  // 美联储
  fed: {
    fed_rate: '',       // 联邦基金目标利率
    fed_balance: '',    // 美联储资产负债表
  },
};

/**
 * 获取指标代码（过滤空值）
 * @param {string} category - 类别
 * @param {string} indicator - 指标名
 * @returns {string|null} 指标代码
 */
function getIndicatorCode(category, indicator) {
  const categoryData = EDB_INDICATORS[category];
  if (!categoryData) return null;
  
  const code = categoryData[indicator];
  return code && code.trim() !== '' ? code : null;
}

/**
 * 获取类别下所有有效的指标代码
 * @param {string} category - 类别
 * @returns {Object} 有效指标代码对象
 */
function getValidIndicators(category) {
  const categoryData = EDB_INDICATORS[category];
  if (!categoryData) return {};
  
  const valid = {};
  for (const [key, value] of Object.entries(categoryData)) {
    if (value && value.trim() !== '') {
      valid[key] = value;
    }
  }
  return valid;
}

/**
 * 检查是否有配置有效的指标代码
 * @returns {boolean} 是否有有效配置
 */
function hasValidConfig() {
  for (const category of Object.values(EDB_INDICATORS)) {
    for (const code of Object.values(category)) {
      if (code && code.trim() !== '') {
        return true;
      }
    }
  }
  return false;
}

/**
 * 获取配置状态报告
 * @returns {Object} 配置状态
 */
function getConfigStatus() {
  const status = {
    total: 0,
    configured: 0,
    categories: {}
  };
  
  for (const [catName, catData] of Object.entries(EDB_INDICATORS)) {
    const catTotal = Object.keys(catData).length;
    const catConfigured = Object.values(catData).filter(v => v && v.trim() !== '').length;
    
    status.total += catTotal;
    status.configured += catConfigured;
    status.categories[catName] = {
      total: catTotal,
      configured: catConfigured,
      percentage: Math.round((catConfigured / catTotal) * 100)
    };
  }
  
  status.percentage = Math.round((status.configured / status.total) * 100);
  return status;
}

/**
 * 打印配置指南
 */
function printConfigGuide() {
  console.log(`
========================================
同花顺EDB指标代码配置指南
========================================

当前配置状态: ${getConfigStatus().percentage}%

如何获取正确的指标代码:
1. 打开同花顺SuperCommand客户端
2. 点击菜单: 经济数据库(EDB)
3. 搜索需要的指标(如"GDP")
4. 找到指标后右键 -> 生成命令
5. 复制命令中的指标代码(如 M001620253)
6. 编辑文件: skills/ths-edb-skill/edb-config.js
7. 将代码填入对应位置

示例配置:
  gdp: {
    gdp_yoy: 'M001620253',  // 替换为实际代码
    ...
  }

注意: EDB指标代码是同花顺商业数据，需要订阅才能使用。
========================================
`);
}

module.exports = {
  EDB_INDICATORS,
  getIndicatorCode,
  getValidIndicators,
  hasValidConfig,
  getConfigStatus,
  printConfigGuide,
};
