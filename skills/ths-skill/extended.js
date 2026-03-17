/**
 * THS Extended Indicators
 * 同花顺扩展指标 - 行业排名、机构持仓等
 */

const ths = require('./index');

/**
 * 获取股票行业排名
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 行业排名数据
 */
async function getIndustryRanking(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_industry_rank_roe_stock', indiparams: ['20241231'] },
    { indicator: 'ths_industry_rank_profit_growth_stock', indiparams: ['20241231'] },
    { indicator: 'ths_industry_rank_revenue_growth_stock', indiparams: ['20241231'] },
    { indicator: 'ths_industry_rank_gross_margin_stock', indiparams: ['20241231'] },
    { indicator: 'ths_industry_rank_net_margin_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    roeRank: table.ths_industry_rank_roe_stock?.[0],
    profitGrowthRank: table.ths_industry_rank_profit_growth_stock?.[0],
    revenueGrowthRank: table.ths_industry_rank_revenue_growth_stock?.[0],
    grossMarginRank: table.ths_industry_rank_gross_margin_stock?.[0],
    netMarginRank: table.ths_industry_rank_net_margin_stock?.[0]
  };
}

/**
 * 获取机构持仓数据
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 机构持仓数据
 */
async function getInstitutionHolding(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_institution_hold_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_fund_hold_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_qfii_hold_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_insurance_hold_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_social_security_hold_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_northbound_hold_ratio_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    institutionRatio: table.ths_institution_hold_ratio_stock?.[0],
    fundRatio: table.ths_fund_hold_ratio_stock?.[0],
    qfiiRatio: table.ths_qfii_hold_ratio_stock?.[0],
    insuranceRatio: table.ths_insurance_hold_ratio_stock?.[0],
    socialSecurityRatio: table.ths_social_security_hold_ratio_stock?.[0],
    northboundRatio: table.ths_northbound_hold_ratio_stock?.[0]
  };
}

/**
 * 获取估值指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 估值数据
 */
async function getValuationIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_pe_ttm_stock', indiparams: [] },
    { indicator: 'ths_pb_stock', indiparams: [] },
    { indicator: 'ths_ps_stock', indiparams: [] },
    { indicator: 'ths_pcf_stock', indiparams: [] },
    { indicator: 'ths_peg_stock', indiparams: ['20241231'] },
    { indicator: 'ths_ev_ebitda_stock', indiparams: [] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    peTTM: table.ths_pe_ttm_stock?.[0],
    pb: table.ths_pb_stock?.[0],
    ps: table.ths_ps_stock?.[0],
    pcf: table.ths_pcf_stock?.[0],
    peg: table.ths_peg_stock?.[0],
    evEbitda: table.ths_ev_ebitda_stock?.[0]
  };
}

/**
 * 获取成长能力指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 成长能力数据
 */
async function getGrowthIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_revenue_growth_3y_stock', indiparams: ['20241231'] },
    { indicator: 'ths_profit_growth_3y_stock', indiparams: ['20241231'] },
    { indicator: 'ths_np_growth_qoq_stock', indiparams: ['20241231'] },
    { indicator: 'ths_revenue_growth_qoq_stock', indiparams: ['20241231'] },
    { indicator: 'ths_total_asset_growth_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    revenueGrowth3Y: table.ths_revenue_growth_3y_stock?.[0],
    profitGrowth3Y: table.ths_profit_growth_3y_stock?.[0],
    npGrowthQoQ: table.ths_np_growth_qoq_stock?.[0],
    revenueGrowthQoQ: table.ths_revenue_growth_qoq_stock?.[0],
    assetGrowth: table.ths_total_asset_growth_stock?.[0]
  };
}

/**
 * 获取盈利能力指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 盈利能力数据
 */
async function getProfitabilityIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_roe_stock', indiparams: ['20241231'] },
    { indicator: 'ths_roa_stock', indiparams: ['20241231'] },
    { indicator: 'ths_roic_stock', indiparams: ['20241231'] },
    { indicator: 'ths_gross_margin_stock', indiparams: ['20241231'] },
    { indicator: 'ths_net_margin_stock', indiparams: ['20241231'] },
    { indicator: 'ths_operating_margin_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    roe: table.ths_roe_stock?.[0],
    roa: table.ths_roa_stock?.[0],
    roic: table.ths_roic_stock?.[0],
    grossMargin: table.ths_gross_margin_stock?.[0],
    netMargin: table.ths_net_margin_stock?.[0],
    operatingMargin: table.ths_operating_margin_stock?.[0]
  };
}

/**
 * 获取偿债能力指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 偿债能力数据
 */
async function getSolvencyIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_current_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_quick_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_debt_asset_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_equity_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_interest_coverage_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    currentRatio: table.ths_current_ratio_stock?.[0],
    quickRatio: table.ths_quick_ratio_stock?.[0],
    debtRatio: table.ths_debt_asset_ratio_stock?.[0],
    equityRatio: table.ths_equity_ratio_stock?.[0],
    interestCoverage: table.ths_interest_coverage_stock?.[0]
  };
}

/**
 * 获取运营效率指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 运营效率数据
 */
async function getEfficiencyIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_inventory_turnover_stock', indiparams: ['20241231'] },
    { indicator: 'ths_receivable_turnover_stock', indiparams: ['20241231'] },
    { indicator: 'ths_total_asset_turnover_stock', indiparams: ['20241231'] },
    { indicator: 'ths_inventory_turnover_days_stock', indiparams: ['20241231'] },
    { indicator: 'ths_receivable_turnover_days_stock', indiparams: ['20241231'] },
    { indicator: 'ths_cash_cycle_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    inventoryTurnover: table.ths_inventory_turnover_stock?.[0],
    receivableTurnover: table.ths_receivable_turnover_stock?.[0],
    assetTurnover: table.ths_total_asset_turnover_stock?.[0],
    inventoryDays: table.ths_inventory_turnover_days_stock?.[0],
    receivableDays: table.ths_receivable_turnover_days_stock?.[0],
    cashCycle: table.ths_cash_cycle_stock?.[0]
  };
}

/**
 * 获取现金流指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 现金流数据
 */
async function getCashFlowIndicators(stockCode) {
  const thsCode = stockCode.startsWith('6') ? `${stockCode}.SH` : `${stockCode}.SZ`;
  
  const indicators = [
    { indicator: 'ths_operating_cash_flow_stock', indiparams: ['20241231'] },
    { indicator: 'ths_free_cash_flow_stock', indiparams: ['20241231'] },
    { indicator: 'ths_cash_flow_ratio_stock', indiparams: ['20241231'] },
    { indicator: 'ths_cash_recovery_ratio_stock', indiparams: ['20241231'] }
  ];
  
  const data = await ths.getBasicData(thsCode, indicators);
  const table = data.tables[0]?.table || {};
  
  return {
    operatingCashFlow: table.ths_operating_cash_flow_stock?.[0],
    freeCashFlow: table.ths_free_cash_flow_stock?.[0],
    cashFlowRatio: table.ths_cash_flow_ratio_stock?.[0],
    cashRecoveryRatio: table.ths_cash_recovery_ratio_stock?.[0]
  };
}

/**
 * 获取所有扩展指标
 * @param {string} stockCode - 股票代码
 * @returns {Promise<Object>} 所有扩展指标
 */
async function getAllExtendedIndicators(stockCode) {
  const [
    industryRanking,
    institutionHolding,
    valuation,
    growth,
    profitability,
    solvency,
    efficiency,
    cashFlow
  ] = await Promise.allSettled([
    getIndustryRanking(stockCode),
    getInstitutionHolding(stockCode),
    getValuationIndicators(stockCode),
    getGrowthIndicators(stockCode),
    getProfitabilityIndicators(stockCode),
    getSolvencyIndicators(stockCode),
    getEfficiencyIndicators(stockCode),
    getCashFlowIndicators(stockCode)
  ]);
  
  return {
    industryRanking: industryRanking.status === 'fulfilled' ? industryRanking.value : null,
    institutionHolding: institutionHolding.status === 'fulfilled' ? institutionHolding.value : null,
    valuation: valuation.status === 'fulfilled' ? valuation.value : null,
    growth: growth.status === 'fulfilled' ? growth.value : null,
    profitability: profitability.status === 'fulfilled' ? profitability.value : null,
    solvency: solvency.status === 'fulfilled' ? solvency.value : null,
    efficiency: efficiency.status === 'fulfilled' ? efficiency.value : null,
    cashFlow: cashFlow.status === 'fulfilled' ? cashFlow.value : null
  };
}

// 导出函数
module.exports = {
  getIndustryRanking,
  getInstitutionHolding,
  getValuationIndicators,
  getGrowthIndicators,
  getProfitabilityIndicators,
  getSolvencyIndicators,
  getEfficiencyIndicators,
  getCashFlowIndicators,
  getAllExtendedIndicators
};
