#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
    } else {
      args[key] = next;
      i += 1;
    }
  }
  return args;
}

function toNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function safeRatio(numerator, denominator) {
  if (numerator === null || denominator === null) return null;
  if (denominator === 0) return null;
  return numerator / denominator;
}

function loadRecords(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8').trim();
  if (!raw) return [];

  if (raw.startsWith('[')) {
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) {
      throw new Error('JSON input must be an array.');
    }
    return data.filter((x) => x && typeof x === 'object');
  }

  return raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, idx) => {
      const obj = JSON.parse(line);
      if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
        throw new Error(`JSONL line ${idx + 1} must be an object.`);
      }
      return obj;
    });
}

function normalizeRecord(item) {
  const revenue = toNumber(item.revenue);
  const fiscalExpenditure = toNumber(item.fiscal_expenditure);
  const generalDebt = toNumber(item.general_debt_balance) || 0;
  const hiddenDebt = toNumber(item.hidden_debt_est) || 0;
  const interestDebt = toNumber(item.interest_bearing_debt) || 0;
  const shortTermDebt = toNumber(item.short_term_debt);
  const cashReserve = toNumber(item.cash_reserve);

  const totalDebt = generalDebt + hiddenDebt + interestDebt;
  const debtToRevenue = safeRatio(totalDebt, revenue);
  const debtToExpenditure = safeRatio(totalDebt, fiscalExpenditure);
  const cashToShortDebt = safeRatio(cashReserve, shortTermDebt);

  const debtServiceCoverage = toNumber(item.debt_service_coverage);
  const revenueGrowth = toNumber(item.revenue_growth);
  const selfSufficiencyRatio = toNumber(item.self_sufficiency_ratio);

  const policySupportText = String(item.policy_support_text || '');
  const eventText = String(item.event_text || '');
  const fiscalStatusText = String(item.fiscal_status_text || '');

  const requiredKeys = [
    revenue,
    fiscalExpenditure,
    toNumber(item.general_debt_balance),
    debtServiceCoverage,
    cashReserve,
    shortTermDebt,
    revenueGrowth,
    selfSufficiencyRatio,
  ];
  const present = requiredKeys.filter((x) => x !== null).length;
  const dataCompleteness = requiredKeys.length === 0 ? 0 : present / requiredKeys.length;

  return {
    entity_name: String(item.entity_name || '(未命名主体)'),
    region: String(item.region || ''),
    as_of_date: String(item.as_of_date || ''),
    revenue,
    fiscal_expenditure: fiscalExpenditure,
    general_debt_balance: toNumber(item.general_debt_balance),
    hidden_debt_est: toNumber(item.hidden_debt_est),
    interest_bearing_debt: toNumber(item.interest_bearing_debt),
    short_term_debt: shortTermDebt,
    cash_reserve: cashReserve,
    debt_service_coverage: debtServiceCoverage,
    revenue_growth: revenueGrowth,
    self_sufficiency_ratio: selfSufficiencyRatio,
    total_debt: totalDebt,
    debt_to_revenue: debtToRevenue,
    debt_to_fiscal_expenditure: debtToExpenditure,
    cash_to_short_debt: cashToShortDebt,
    policy_support_text: policySupportText,
    event_text: eventText,
    fiscal_status_text: fiscalStatusText,
    data_completeness: dataCompleteness,
    source_raw: item,
  };
}

function main() {
  const args = parseArgs(process.argv);
  const input = args.input;
  const output = args.output;
  const pretty = Boolean(args.pretty);

  if (!input) {
    console.error('Usage: node scripts/gov_dd_preprocess.js --input <raw.json|raw.jsonl> [--output <processed.json>] [--pretty]');
    process.exit(1);
  }

  if (!fs.existsSync(input)) {
    console.error(`Input file not found: ${input}`);
    process.exit(1);
  }

  const records = loadRecords(input);
  const normalized = records.map(normalizeRecord);
  const payload = JSON.stringify(normalized, null, pretty ? 2 : 0);

  if (output) {
    fs.writeFileSync(output, payload, 'utf8');
    console.log(`Processed ${normalized.length} records -> ${path.resolve(output)}`);
  } else {
    process.stdout.write(payload + '\n');
  }
}

main();
