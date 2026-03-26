/** @format */
/**
 * Eastmoney Fund Skill - 东方财富基金数据接口
 * 提供基金列表、基金详情、基金净值、基金排行等数据
 */

const fetch = require('node-fetch');

// 东方财富API基础URL
const BASE_URL = 'https://datacenter-web.eastmoney.com/api/data/v1/get';
const FUND_API_URL = 'https://fundact.eastmoney.com/bond/web/queryallbonds';

/**
 * 调用东方财富API
 * @param {string} reportName - 报表名称
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 响应数据
 */
async function callAPI(reportName, params = {}) {
  const queryParams = new URLSearchParams({
    reportName: reportName,
    columns: 'ALL',
    ...params
  });
  
  const url = `${BASE_URL}?${queryParams.toString()}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    timeout: 30000
  });
  
  if (!response.ok) {
    throw new Error(`HTTP错误: ${response.status}`);
  }
  
  const data = await response.json();
  
  if (data.code !== 0 && data.result?.code !== 0) {
    throw new Error(`API错误: ${data.message || '未知错误'}`);
  }
  
  return data.result || data;
}

/**
 * 获取基金列表
 * @param {number} pageSize - 每页数量
 * @returns {Promise<Array>} 基金列表
 */
async function getFundList(pageSize = 500) {
  try {
    const data = await callAPI('RPT_FUND_INFO', {
      pageNumber: 1,
      pageSize: pageSize
    });
    
    if (data?.data) {
      return data.data.map(item => ({
        code: item.FUND_CODE,
        name: item.FUND_NAME,
        type: item.FUND_TYPE,
        manager: item.FUND_MANAGER,
        company: item.FUND_COMPANY,
        nav: parseFloat(item.NAV || 0),
        navDate: item.NAV_DATE,
        totalNav: parseFloat(item.TOTAL_NAV || 0),
        growth1m: parseFloat(item.GROWTH_1M || 0),
        growth3m: parseFloat(item.GROWTH_3M || 0),
        growth6m: parseFloat(item.GROWTH_6M || 0),
        growth1y: parseFloat(item.GROWTH_1Y || 0),
        growthYtd: parseFloat(item.GROWTH_YTD || 0),
      }));
    }
    
    return [];
  } catch (error) {
    console.error('获取基金列表失败:', error.message);
    return [];
  }
}

/**
 * 获取基金排行（按业绩）
 * @param {string} period - 周期 (1m, 3m, 6m, 1y, ytd)
 * @param {number} topN - 前N名
 * @returns {Promise<Array>} 基金排行
 */
async function getFundRanking(period = '1y', topN = 20) {
  try {
    const data = await callAPI('RPT_FUND_PERFORMANCE', {
      pageNumber: 1,
      pageSize: topN,
      sortColumns: `GROWTH_${period.toUpperCase()}`,
      sortTypes: -1
    });
    
    if (data?.data) {
      return data.data.map((item, index) => ({
        rank: index + 1,
        code: item.FUND_CODE,
        name: item.FUND_NAME,
        type: item.FUND_TYPE,
        manager: item.FUND_MANAGER,
        nav: parseFloat(item.NAV || 0),
        growth: parseFloat(item[`GROWTH_${period.toUpperCase()}`] || 0),
        growthYtd: parseFloat(item.GROWTH_YTD || 0),
      }));
    }
    
    return [];
  } catch (error) {
    console.error('获取基金排行失败:', error.message);
    return [];
  }
}

/**
 * 获取基金详情
 * @param {string} fundCode - 基金代码
 * @returns {Promise<Object>} 基金详情
 */
async function getFundDetail(fundCode) {
  try {
    const data = await callAPI('RPT_FUND_INFO', {
      filter: `(FUND_CODE="${fundCode}")`,
      pageNumber: 1,
      pageSize: 1
    });
    
    if (data?.data && data.data.length > 0) {
      const item = data.data[0];
      return {
        code: item.FUND_CODE,
        name: item.FUND_NAME,
        type: item.FUND_TYPE,
        manager: item.FUND_MANAGER,
        company: item.FUND_COMPANY,
        nav: parseFloat(item.NAV || 0),
        navDate: item.NAV_DATE,
        totalNav: parseFloat(item.TOTAL_NAV || 0),
        growth1m: parseFloat(item.GROWTH_1M || 0),
        growth3m: parseFloat(item.GROWTH_3M || 0),
        growth6m: parseFloat(item.GROWTH_6M || 0),
        growth1y: parseFloat(item.GROWTH_1Y || 0),
        growthYtd: parseFloat(item.GROWTH_YTD || 0),
        establishedDate: item.ESTABLISHED_DATE,
        scale: parseFloat(item.FUND_SCALE || 0),
        riskLevel: item.RISK_LEVEL,
      };
    }
    
    return null;
  } catch (error) {
    console.error('获取基金详情失败:', error.message);
    return null;
  }
}

/**
 * 搜索基金
 * @param {string} keyword - 搜索关键词
 * @returns {Promise<Array>} 搜索结果
 */
async function searchFunds(keyword) {
  try {
    const data = await callAPI('RPT_FUND_INFO', {
      filter: `(FUND_NAME_LIKE="${keyword}" OR FUND_CODE_LIKE="${keyword}")`,
      pageNumber: 1,
      pageSize: 20
    });
    
    if (data?.data) {
      return data.data.map(item => ({
        code: item.FUND_CODE,
        name: item.FUND_NAME,
        type: item.FUND_TYPE,
        manager: item.FUND_MANAGER,
        nav: parseFloat(item.NAV || 0),
        growth1y: parseFloat(item.GROWTH_1Y || 0),
      }));
    }
    
    return [];
  } catch (error) {
    console.error('搜索基金失败:', error.message);
    return [];
  }
}

/**
 * 获取基金历史净值
 * @param {string} fundCode - 基金代码
 * @param {number} days - 天数
 * @returns {Promise<Array>} 历史净值
 */
async function getFundHistoryNav(fundCode, days = 30) {
  try {
    const data = await callAPI('RPT_FUND_NAV_HISTORY', {
      filter: `(FUND_CODE="${fundCode}")`,
      pageNumber: 1,
      pageSize: days,
      sortColumns: 'NAV_DATE',
      sortTypes: -1
    });
    
    if (data?.data) {
      return data.data.map(item => ({
        date: item.NAV_DATE,
        nav: parseFloat(item.NAV || 0),
        totalNav: parseFloat(item.TOTAL_NAV || 0),
        dailyGrowth: parseFloat(item.DAILY_GROWTH || 0),
      })).reverse();
    }
    
    return [];
  } catch (error) {
    console.error('获取基金历史净值失败:', error.message);
    return [];
  }
}

/**
 * 获取基金公司列表
 * @returns {Promise<Array>} 基金公司列表
 */
async function getFundCompanyList() {
  try {
    const data = await callAPI('RPT_FUND_COMPANY', {
      pageNumber: 1,
      pageSize: 200
    });
    
    if (data?.data) {
      return data.data.map(item => ({
        name: item.COMPANY_NAME,
        fundCount: parseInt(item.FUND_COUNT || 0),
        totalScale: parseFloat(item.TOTAL_SCALE || 0),
        growth1y: parseFloat(item.GROWTH_1Y || 0),
      }));
    }
    
    return [];
  } catch (error) {
    console.error('获取基金公司列表失败:', error.message);
    return [];
  }
}

module.exports = {
  getFundList,
  getFundRanking,
  getFundDetail,
  searchFunds,
  getFundHistoryNav,
  getFundCompanyList,
  callAPI,
};
