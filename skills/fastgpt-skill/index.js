/** @format */
/**
 * FastGPT Skill - FastGPT智能体API调用
 * 支持多智能体配置
 * API文档: https://doc.fastgpt.io/zh-CN/docs/openapi/intro
 */

const fetch = require('node-fetch');
const https = require('https');

// 强制使用 IPv4 的 agent（避免 IPv6 连接问题）
const ipv4Agent = new https.Agent({
  family: 4,
});

// 匡时财经教育大模型（默认）
const CONFIG_FINANCE = {
  name: '匡时财经教育大模型',
  baseUrl: 'https://llm.sufe.edu.cn/api',
  apiKey:
    'openapi-k8hectBmrYi98tWMLrFiG82e1Zh84rl21BKtGn58fadAA9MgWCW5RQf0Z',
  appId: '69294ff78c7e924e69e4021e',
};

// 博弈与社会课程智能体
const CONFIG_GAME_SOCIETY = {
  name: '博弈与社会课程智能体',
  baseUrl: 'https://llm.sufe.edu.cn/api',
  apiKey: 'openapi-jb5QttqoWJVm0BsJlJc99zDf7YLKGQ0zWN0YQqT8RyTBHHTjMQro1qhdJ',
  appId: '69af7e8437c92a1b66b0c7e0',
};

// 长三角一体化大模型
const CONFIG_YRD_INTEGRATION = {
  name: '长三角一体化大模型',
  baseUrl: 'https://llm.sufe.edu.cn/api',
  apiKey: 'openapi-y9rmxc79jRKAkc1l8atGEkY3ZMog6IP1xUezQvJl3wE0n0JueRXcp6RULj7',
  appId: '690cc232f4bb50b9dbd5bf6a',
};

// 数值分析课程智能体
const CONFIG_NUMERICAL_ANALYSIS = {
  name: '数值分析课程智能体',
  baseUrl: 'https://llm.sufe.edu.cn/api',
  apiKey: 'openapi-uFakwAoK00m9DjfxeH9usJMzmDaPtf0gyJoG04NsgI7PQfVlAs5sGVSu2',
  appId: '698c3c7037c92a1b66a90970',
};

// 默认配置
const DEFAULT_CONFIG = CONFIG_FINANCE;

/**
 * 获取智能体配置
 * @param {string} agentName - 智能体名称 ('finance' | 'game-society' | 'yrd' | 'numerical')
 * @returns {Object} 智能体配置
 */
function getConfig(agentName = 'finance') {
  const configs = {
    'finance': CONFIG_FINANCE,
    'game-society': CONFIG_GAME_SOCIETY,
    'yrd': CONFIG_YRD_INTEGRATION,
    'numerical': CONFIG_NUMERICAL_ANALYSIS,
    'default': DEFAULT_CONFIG,
  };
  return configs[agentName] || DEFAULT_CONFIG;
}

/**
 * 调用FastGPT智能体对话
 * @param {string} message - 用户消息
 * @param {Object} options - 配置选项
 * @param {string} options.agent - 智能体名称 ('finance' | 'game-society' | 'yrd')
 * @param {string} options.chatId - 对话ID（用于上下文关联）
 * @param {string} options.customUid - 自定义用户ID
 * @param {boolean} options.stream - 是否流式返回
 * @returns {Promise<Object>} 返回对话结果
 */
async function chat(message, options = {}) {
  const agentName = options.agent || 'finance';
  const config = getConfig(agentName);
  
  const {
    chatId = generateChatId(),
    customUid = 'finclaw-user',
    stream = false,
    detail = false,
  } = options;

  const url = `${config.baseUrl}/v1/chat/completions`;

  const body = {
    chatId,
    stream,
    detail,
    messages: [
      {
        content: message,
        role: 'user',
      },
    ],
    customUid,
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      agent: ipv4Agent,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `FastGPT API错误: ${response.status} - ${errorText}`
      );
    }

    const data = await response.json();
    return {
      success: true,
      agentName: config.name,
      chatId,
      response: data.choices?.[0]?.message?.content || data,
      raw: data,
    };
  } catch (error) {
    return {
      success: false,
      agentName: config.name,
      error: error.message,
    };
  }
}

/**
 * 多轮对话
 * @param {Array} messages - 消息数组 [{role, content}, ...]
 * @param {Object} options - 配置选项
 * @param {string} options.agent - 智能体名称 ('finance' | 'game-society' | 'yrd')
 * @returns {Promise<Object>} 返回对话结果
 */
async function chatMulti(messages, options = {}) {
  const agentName = options.agent || 'finance';
  const config = getConfig(agentName);
  
  const {
    chatId = generateChatId(),
    customUid = 'finclaw-user',
    stream = false,
    detail = false,
  } = options;

  const url = `${config.baseUrl}/v1/chat/completions`;

  const body = {
    chatId,
    stream,
    detail,
    messages,
    customUid,
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      agent: ipv4Agent,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `FastGPT API错误: ${response.status} - ${errorText}`
      );
    }

    const data = await response.json();
    return {
      success: true,
      agentName: config.name,
      chatId,
      response: data.choices?.[0]?.message?.content || data,
      raw: data,
    };
  } catch (error) {
    return {
      success: false,
      agentName: config.name,
      error: error.message,
    };
  }
}

/**
 * 生成唯一对话ID
 * @returns {string} 对话ID
 */
function generateChatId() {
  return `finclaw-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 简单问答 - 直接返回文本
 * @param {string} question - 问题
 * @param {string} agentName - 智能体名称
 * @returns {Promise<string>} 回答文本
 */
async function ask(question, agentName = 'finance') {
  const result = await chat(question, { agent: agentName });
  if (result.success) {
    return result.response;
  }
  throw new Error(result.error);
}

/**
 * 财经教育专用 - 带格式的问答
 * @param {string} question - 问题
 * @returns {Promise<string>} 格式化回答
 */
async function researchAsk(question) {
  const prefix = `[匡时财经教育大模型] `;
  try {
    const answer = await ask(question, 'finance');
    return `${prefix}${answer}`;
  } catch (error) {
    return `${prefix}调用失败: ${error.message}`;
  }
}

/**
 * 博弈与社会课程专用 - 带格式的问答
 * @param {string} question - 问题
 * @returns {Promise<string>} 格式化回答
 */
async function gameSocietyAsk(question) {
  const prefix = `[博弈与社会课程智能体] `;
  try {
    const answer = await ask(question, 'game-society');
    return `${prefix}${answer}`;
  } catch (error) {
    return `${prefix}调用失败: ${error.message}`;
  }
}

module.exports = {
  chat,
  chatMulti,
  ask,
  researchAsk,
  gameSocietyAsk,
  generateChatId,
  getConfig,
  CONFIGS: {
    FINANCE: CONFIG_FINANCE,
    GAME_SOCIETY: CONFIG_GAME_SOCIETY,
    YRD_INTEGRATION: CONFIG_YRD_INTEGRATION,
    NUMERICAL_ANALYSIS: CONFIG_NUMERICAL_ANALYSIS,
  },
};
