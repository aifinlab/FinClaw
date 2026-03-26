/** @format */
/**
 * THS EDB Skill - 同花顺经济数据库接口
 * 提供宏观数据、行业数据、国际数据等
 * 基于同花顺EDB API: /api/v1/edb_service
 */

const thsAPI = require('../ths-skill/index.js');
const { getValidIndicators, hasValidConfig, getConfigStatus, printConfigGuide } = require('./edb-config');

/**
 * 获取EDB数据
 * @param {string} indicatorCodes - 指标代码，多个用逗号分隔
 * @param {string} startDate - 开始日期 YYYY-MM-DD
 * @param {string} endDate - 结束日期 YYYY-MM-DD
 * @returns {Promise<Object>} EDB数据
 */
async function getEDBData(indicatorCodes, startDate, endDate) {
  try {
    const data = await thsAPI.getEDBData(indicatorCodes, startDate, endDate);
    return parseEDBResponse(data);
  } catch (error) {
    console.error('EDB数据获取失败:', error.message);
    throw error;
  }
}

/**
 * 解析EDB响应数据
 * @param {Object} response - API响应
 * @returns {Object} 解析后的数据
 */
function parseEDBResponse(response) {
  if (!response || response.errorcode !== 0) {
    throw new Error(response?.errmsg || 'EDB响应错误');
  }
  
  const result = {
    errorcode: response.errorcode,
    indicators: response.indicators || [],
    data: {}
  };
  
  if (response.tables && response.tables.length > 0) {
    response.tables.forEach((table, index) => {
      const indicator = response.indicators?.[index] || `indicator_${index}`;
      
      if (table && table.table) {
        const times = table.table.x || [];
        const values = table.table.y || [];
        
        result.data[indicator] = {
          times: times,
          values: values,
          latest: values.length > 0 ? values[values.length - 1] : null,
          latestDate: times.length > 0 ? times[times.length - 1] : null,
          count: values.length
        };
      }
    });
  }
  
  return result;
}

/**
 * 获取GDP数据
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} GDP数据
 */
async function getGDPData(startDate, endDate) {
  const indicators = getValidIndicators('gdp');
  if (Object.keys(indicators).length === 0) {
    console.log('GDP指标未配置，请在edb-config.js中设置');
    return null;
  }
  
  try {
    const codes = Object.values(indicators).join(',');
    const data = await getEDBData(codes, startDate, endDate);
    
    const result = {};
    for (const [key, code] of Object.entries(indicators)) {
      result[key] = data.data[code];
    }
    return result;
  } catch (error) {
    console.error('GDP数据获取失败:', error.message);
    return null;
  }
}

/**
 * 获取价格指数数据
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} 价格数据
 */
async function getPriceData(startDate, endDate) {
  const indicators = getValidIndicators('price');
  if (Object.keys(indicators).length === 0) {
    console.log('价格指数未配置，请在edb-config.js中设置');
    return null;
  }
  
  try {
    const codes = Object.values(indicators).join(',');
    const data = await getEDBData(codes, startDate, endDate);
    
    const result = {};
    for (const [key, code] of Object.entries(indicators)) {
      result[key] = data.data[code];
    }
    return result;
  } catch (error) {
    console.error('价格数据获取失败:', error.message);
    return null;
  }
}

/**
 * 获取货币供应数据
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} 货币数据
 */
async function getMoneySupplyData(startDate, endDate) {
  const indicators = getValidIndicators('money');
  if (Object.keys(indicators).length === 0) {
    console.log('货币供应指标未配置，请在edb-config.js中设置');
    return null;
  }
  
  try {
    const codes = Object.values(indicators).join(',');
    const data = await getEDBData(codes, startDate, endDate);
    
    const result = {};
    for (const [key, code] of Object.entries(indicators)) {
      result[key] = data.data[code];
    }
    return result;
  } catch (error) {
    console.error('货币供应数据获取失败:', error.message);
    return null;
  }
}

/**
 * 获取PMI数据
 * @param {string} startDate - 开始日期
 * @param {string} endDate - 结束日期
 * @returns {Promise<Object>} PMI数据
 */
async function getPMIData(startDate, endDate) {
  const indicators = getValidIndicators('pmi');
  if (Object.keys(indicators).length === 0) {
    console.log('PMI指标未配置，请在edb-config.js中设置');
    return null;
  }
  
  try {
    const codes = Object.values(indicators).join(',');
    const data = await getEDBData(codes, startDate, endDate);
    
    const result = {};
    for (const [key, code] of Object.entries(indicators)) {
      result[key] = data.data[code];
    }
    return result;
  } catch (error) {
    console.error('PMI数据获取失败:', error.message);
    return null;
  }
}

/**
 * 获取完整宏观数据面板
 * @returns {Promise<Object>} 完整宏观数据
 */
async function getMacroDashboard() {
  if (!hasValidConfig()) {
    console.log('\n========================================');
    console.log('警告: EDB指标代码未配置');
    console.log('========================================');
    printConfigGuide();
    return null;
  }
  
  const today = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  const [
    gdpData,
    priceData,
    moneyData,
    pmiData
  ] = await Promise.allSettled([
    getGDPData(startDate, today),
    getPriceData(startDate, today),
    getMoneySupplyData(startDate, today),
    getPMIData(startDate, today)
  ]);
  
  return {
    timestamp: new Date().toISOString(),
    config: getConfigStatus(),
    gdp: gdpData.status === 'fulfilled' ? gdpData.value : null,
    price: priceData.status === 'fulfilled' ? priceData.value : null,
    money: moneyData.status === 'fulfilled' ? moneyData.value : null,
    pmi: pmiData.status === 'fulfilled' ? pmiData.value : null,
  };
}

module.exports = {
  getEDBData,
  getGDPData,
  getPriceData,
  getMoneySupplyData,
  getPMIData,
  getMacroDashboard,
  hasValidConfig,
  getConfigStatus,
  printConfigGuide,
};
