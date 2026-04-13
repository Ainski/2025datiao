// ===== 调试开关：控制控制台输出 =====
// true = 输出所有调试信息
// false = 静默运行，仅显示错误信息
const DEBUG_MODE = true;

// 封装调试日志函数
function debugLog(...args) {
  if (DEBUG_MODE) {
    console.log(...args);
  }
}

function debugWarn(...args) {
  if (DEBUG_MODE) {
    console.warn(...args);
  }
}

function debugError(...args) {
  // 错误信息始终输出，不受 DEBUG_MODE 影响
  console.error(...args);
}

// 防止重复注入
if (window.luohouInjected) {
  debugLog('罗睺镜: 脚本已注入，跳过');
} else {
  window.luohouInjected = true;
  debugLog('罗睺镜: 脚本首次注入，初始化中...', { DEBUG_MODE });

  // 全局数据存储
  window.luohouData = {
    allCardsByUrl: {},
    currentUrl: window.location.href,
    panel: null,
    isPanelOpen: false
  };

  // ===== 面板相关 =====
  
  // 创建侧边栏面板
  function createPanel() {
    if (window.luohouData.panel) {
      return window.luohouData.panel;
    }

    const panel = document.createElement('div');
    panel.id = 'luohou-panel';
    panel.style.cssText = `
      position: fixed;
      top: 0;
      right: -500px;
      width: 450px;
      height: 100vh;
      background: white;
      box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
      z-index: 2147483647;
      transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    `;

    panel.innerHTML = `
      <div style="padding: 20px; border-bottom: 1px solid #e2e8f0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="font-size: 18px; font-weight: 600; margin: 0;">🔍 罗睺镜</h2>
          <button id="luohou-close-btn" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; transition: background 0.3s;">✕</button>
        </div>
        <div id="luohou-url" style="font-size: 12px; margin-top: 8px; opacity: 0.9; word-break: break-all; max-height: 40px; overflow: hidden;"></div>
      </div>
      
      <div style="flex: 1; overflow-y: auto; padding: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="font-size: 14px; font-weight: 600; color: #2d3748;">⭐ 商品评价（<span id="luohou-card-count">0</span>条）</h3>
        </div>
        <div id="luohou-cards-container">
          <div style="text-align: center; color: #a0aec0; padding: 40px 20px; font-size: 14px;">暂无评价数据<br><span style="font-size: 12px;">点击"采集内容"按钮开始采集</span></div>
        </div>
      </div>
      
      <div style="padding: 16px; border-top: 1px solid #e2e8f0; background: #f7fafc;">
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
          <button id="luohou-confirm-btn" style="flex: 1; padding: 10px; border: none; border-radius: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s; box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);">
            🚀 采集内容
          </button>
          <button id="luohou-submit-btn" style="flex: 1; padding: 10px; border: none; border-radius: 8px; background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: white; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s; box-shadow: 0 2px 6px rgba(72, 187, 120, 0.3);">
            📤 提交分析
          </button>
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
          <button id="luohou-clear-btn" style="flex: 1; padding: 10px; border: none; border-radius: 8px; background: linear-gradient(135deg, #fc8181 0%, #e53e3e 100%); color: white; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s; box-shadow: 0 2px 6px rgba(252, 129, 129, 0.3);">
            🗑️ 清空缓存
          </button>
        </div>
        <div id="luohou-status" style="display: none; font-size: 12px; padding: 8px 10px; background: white; border-radius: 6px; border-left: 3px solid #667eea; color: #667eea;"></div>
      </div>
    `;

    document.body.appendChild(panel);
    window.luohouData.panel = panel;

    // 绑定事件
    document.getElementById('luohou-close-btn').addEventListener('click', () => togglePanel(false));
    document.getElementById('luohou-confirm-btn').addEventListener('click', () => collectContent(false)); // 手动模式
    document.getElementById('luohou-submit-btn').addEventListener('click', submitAnalysis);
    document.getElementById('luohou-clear-btn').addEventListener('click', clearCache);

    return panel;
  }

  // 切换面板显示/隐藏
  function togglePanel(show) {
    const panel = createPanel();
    
    if (show === undefined) {
      show = !window.luohouData.isPanelOpen;
    }

    window.luohouData.isPanelOpen = show;
    
    if (show) {
      panel.style.right = '0';
      // 初始化面板时显示 URL
      document.getElementById('luohou-url').textContent = window.luohouData.currentUrl;
      renderCards();
    } else {
      panel.style.right = '-500px';
    }
  }

  // 渲染卡片
  function renderCards() {
    const container = document.getElementById('luohou-cards-container');
    if (!container) return;

    const url = window.luohouData.currentUrl;
    const cardStore = window.luohouData.allCardsByUrl[url] || {};
    const sortedCards = Object.entries(cardStore).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));

    if (sortedCards.length === 0) {
      container.innerHTML = '<div style="text-align: center; color: #a0aec0; padding: 40px 20px; font-size: 14px;">暂无评价数据<br><span style="font-size: 12px;">点击"采集内容"按钮开始采集</span></div>';
      document.getElementById('luohou-card-count').textContent = '0';
      return;
    }

    container.innerHTML = '';
    document.getElementById('luohou-card-count').textContent = sortedCards.length;

    sortedCards.forEach(([dataIndex, card]) => {
      const cardEl = document.createElement('div');
      cardEl.style.cssText = 'background: white; border-radius: 10px; padding: 14px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; transition: all 0.3s;';
      
      const stars = '⭐'.repeat(card.rating > 0 ? card.rating : 5);
      
      cardEl.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div style="font-weight: 600; color: #2d3748; font-size: 13px;">评价 #${parseInt(dataIndex) + 1}</div>
          <div style="color: #666; font-size: 12px;">${card.username || '匿名用户'}</div>
        </div>
        <div style="margin-bottom: 6px;">
          <span style="font-size: 13px;">${stars}</span>
          ${card.date ? `<span style="color: #999; font-size: 11px; margin-left: 6px;">${card.date}</span>` : ''}
        </div>
        ${card.specs ? `<div style="background: #f7fafc; padding: 5px 8px; border-radius: 5px; margin-bottom: 8px; font-size: 11px; color: #666;">${card.specs}</div>` : ''}
        <div style="color: #4a5568; font-size: 13px; line-height: 1.6; margin-bottom: 10px;">
          ${card.content.replace(/\n/g, '<br>')}
        </div>
        <div style="background: #f7fafc; border-radius: 6px; padding: 10px; border-left: 3px solid #667eea;">
          <div style="color: #667eea; font-weight: 600; font-size: 12px; margin-bottom: 4px;">分析结果</div>
          <div style="color: #4a5568; font-size: 12px; line-height: 1.5;">${card.analysisResult || '等待提交分析...'}</div>
        </div>
      `;

      cardEl.addEventListener('mouseenter', () => {
        cardEl.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.12)';
        cardEl.style.transform = 'translateY(-2px)';
      });
      cardEl.addEventListener('mouseleave', () => {
        cardEl.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        cardEl.style.transform = 'translateY(0)';
      });

      container.appendChild(cardEl);
    });
  }

  // ===== 数据采集 =====

  // 存储上次采集的数据指纹，用于检测变化
  window.lastDataHash = {};

  function collectContent(autoMode = false) {
    // 自动模式下不显示状态提示
    if (!autoMode) {
      showStatus('正在采集评价内容...', 'info');
    }

    const currentUrl = window.location.href;
    window.luohouData.currentUrl = currentUrl;
    
    const cardContainers = document.querySelectorAll('[data-index]');

    const cards = Array.from(cardContainers).map((container) => {
      const dataIndex = container.getAttribute('data-index');
      const card = container.querySelector('.jdc-pc-rate-card') || container;

      const nickEl = card.querySelector('.jdc-pc-rate-card-nick');
      const username = nickEl ? nickEl.innerText.trim() : '匿名用户';

      const dateEl = card.querySelector('.date.list');
      const date = dateEl ? dateEl.innerText.trim() : '';

      const starImg = card.querySelector('.jdc-pc-rate-card-info-left img');
      let rating = 5;
      if (starImg) {
        const starSrc = starImg.getAttribute('src') || '';
        if (starSrc.includes('star-bad')) {
          rating = 1;
        } else if (starSrc.includes('star-middle')) {
          rating = 3;
        }
      }

      const descEl = card.querySelector('.jdc-pc-rate-card-main-desc');
      const content = descEl ? descEl.innerText.trim() : '';

      const infoEl = card.querySelector('.info');
      const specs = infoEl ? infoEl.innerText.trim() : '';

      return { dataIndex, username, date, rating, content, specs };
    }).filter(card => card.content.length > 0);

    // 生成当前数据的哈希值（用于对比是否变化）
    const currentDataHash = cards.map(c => `${c.dataIndex}:${c.content}`).join('|');
    const lastHash = window.lastDataHash[currentUrl];
    
    // 如果数据没有变化，跳过后续处理（避免反复触发）
    if (autoMode && currentDataHash === lastHash) {
      return;
    }
    
    // 更新数据哈希
    window.lastDataHash[currentUrl] = currentDataHash;

    debugLog(`罗睺镜: 采集到${cards.length}条评价，URL: ${currentUrl}`);
    debugLog('罗睺镜: 评价索引:', cards.map(c => c.dataIndex));

    // 累加存储
    if (!window.luohouData.allCardsByUrl[currentUrl]) {
      window.luohouData.allCardsByUrl[currentUrl] = {};
    }

    const cardStore = window.luohouData.allCardsByUrl[currentUrl];
    let newCount = 0;
    let updateCount = 0;

    cards.forEach(card => {
      const existingCard = cardStore[card.dataIndex];
      // 只有当卡片不存在，或者内容有变化时才更新
      if (!existingCard) {
        newCount++;
        cardStore[card.dataIndex] = { ...card, lastUpdated: new Date().toISOString() };
      } else if (existingCard.content !== card.content) {
        // 内容发生变化，保留已有的分析结果
        updateCount++;
        cardStore[card.dataIndex] = { 
          ...card, 
          analysisResult: existingCard.analysisResult, // 保留分析结果
          lastUpdated: new Date().toISOString() 
        };
      }
    });

    // 只有当有新数据或更新时才保存
    if (newCount > 0 || updateCount > 0) {
      // 保存到 storage
      chrome.storage.local.set({ allCardsByUrl: window.luohouData.allCardsByUrl });
    }

    const totalCount = Object.keys(cardStore).length;
    
    // 只在手动点击或数据变化时显示提示
    if (!autoMode) {
      if (newCount > 0 || updateCount > 0) {
        showStatus(`新增${newCount}条评价${updateCount > 0 ? `，更新${updateCount}条` : ''}，当前共${totalCount}条`, 'success');
      } else {
        showStatus('暂无新评价数据', 'info');
      }
    } else if (newCount > 0) {
      // 自动模式下只在有新数据时显示简短提示
      debugLog(`罗睺镜: 自动新增${newCount}条评价，当前共${totalCount}条`);
      // 如果面板已打开，显示提示
      if (window.luohouData.isPanelOpen) {
        showStatus(`自动采集到${newCount}条新评价`, 'success');
      }
    }

    // 更新 UI（无论面板是否打开都更新）
    updatePanelUI(totalCount);
  }
  
  // 更新面板 UI（独立函数，确保数据变化时能实时更新）
  function updatePanelUI(totalCount) {
    // 更新计数
    const countEl = document.getElementById('luohou-card-count');
    if (countEl) {
      countEl.textContent = totalCount || 0;
    }
    
    // 如果面板已打开，渲染卡片
    if (window.luohouData.isPanelOpen) {
      renderCards();
    }
  }

  // ===== 清空缓存 =====
  
  function clearCache() {
    const url = window.luohouData.currentUrl;
    const cardStore = window.luohouData.allCardsByUrl[url];
    
    if (!cardStore || Object.keys(cardStore).length === 0) {
      showStatus('当前页面暂无缓存数据', 'info');
      return;
    }
    
    const count = Object.keys(cardStore).length;
    
    // 确认清空
    if (confirm(`确定要清空当前页面的 ${count} 条评价缓存吗？\n\n此操作不可恢复。`)) {
      clearCacheSilent();
      showStatus(`已清空${count}条评价缓存`, 'success');
    }
  }
  
  // 静默清空缓存（供 popup 调用）
  function clearCacheSilent() {
    const url = window.luohouData.currentUrl;
    const cardStore = window.luohouData.allCardsByUrl[url];
    
    if (!cardStore || Object.keys(cardStore).length === 0) {
      return { success: false, hasData: false };
    }
    
    const count = Object.keys(cardStore).length;
    
    // 删除当前 URL 的缓存
    delete window.luohouData.allCardsByUrl[url];
    
    // 保存到 storage
    chrome.storage.local.set({ allCardsByUrl: window.luohouData.allCardsByUrl });
    
    // 更新 UI
    const countEl = document.getElementById('luohou-card-count');
    if (countEl) countEl.textContent = '0';
    renderCards();
    
    debugLog(`罗睺镜: 已清空${count}条评价缓存，URL: ${url}`);
    return { success: true, hasData: true, count: count };
  }

  // ===== 提交分析 =====

  // 标记是否正在提交（用于暂停自动采集和中止）
  window.isSubmitting = false;
  window.abortSubmission = false; // 中止信号

  function submitAnalysis() {
    const btn = document.getElementById('luohou-submit-btn');
    
    // 如果正在提交，点击则中止
    if (window.isSubmitting) {
      window.abortSubmission = true;
      btn.innerHTML = '<span>⏹️ 正在中止...</span>';
      btn.disabled = true;
      showStatus('正在中止分析...', 'info');
      return;
    }

    const url = window.luohouData.currentUrl;
    const cardStore = window.luohouData.allCardsByUrl[url] || {};

    if (Object.keys(cardStore).length === 0) {
      showStatus('暂无评价数据可提交', 'error');
      return;
    }

    // 重置中止信号
    window.abortSubmission = false;
    window.isSubmitting = true;
    
    // 更新按钮为"中止分析"
    btn.innerHTML = '<span>⏹️ 中止分析</span>';
    btn.style.background = 'linear-gradient(135deg, #fc8181 0%, #e53e3e 100%)';
    btn.style.boxShadow = '0 2px 6px rgba(252, 129, 129, 0.3)';
    
    showStatusWithSpinner('逐条提交中，点击按钮可中止...');

    // 获取所有评价，按 dataIndex 排序
    const sortedEntries = Object.entries(cardStore).sort((a, b) => parseInt(a[0]) - parseInt(b[0]));
    const total = sortedEntries.length;

    // 逐条提交
    submitNext(sortedEntries, 0, total, cardStore, url);
  }

  // 递归逐条提交
  function submitNext(sortedEntries, index, total, cardStore, url) {
    const btn = document.getElementById('luohou-submit-btn');
    
    // 检查是否被中止
    if (window.abortSubmission) {
      window.isSubmitting = false;
      window.abortSubmission = false;
      
      // 恢复按钮状态
      btn.innerHTML = '<span>📤 提交分析</span>';
      btn.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
      btn.style.boxShadow = '0 2px 6px rgba(72, 187, 120, 0.3)';
      btn.disabled = false;
      btn.style.opacity = '1';
      
      showStatus(`已中止分析，已处理${index}/${total}条`, 'info');
      return;
    }
    
    if (index >= total) {
      // 全部完成
      window.isSubmitting = false;
      window.abortSubmission = false;
      chrome.storage.local.set({ allCardsByUrl: window.luohouData.allCardsByUrl });
      renderCards();
      
      // 恢复按钮状态
      btn.innerHTML = '<span>📤 提交分析</span>';
      btn.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
      btn.style.boxShadow = '0 2px 6px rgba(72, 187, 120, 0.3)';
      btn.disabled = false;
      btn.style.opacity = '1';
      
      showStatus(`全部提交完成！共处理${total}条评价`, 'success');
      return;
    }

    const [dataIndex, card] = sortedEntries[index];
    const current = index + 1;

    // 更新状态提示
    showStatusWithSpinner(`正在提交第 ${current}/${total} 条...`);

    // 发送单条评价
    fetch('http://localhost:8989/api/input', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': '1IlIl1|1Il||||/\\|1'
      },
      body: JSON.stringify({ 
        comments: [card.content],  // 只发送一条
        url: url
      })
    })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP错误 ${res.status}`);
      return res.json();
    })
    .then(data => {
      // 后端返回的是数组，取第一个元素
      if (data && data.length > 0) {
        const result = data[0];
        // 修复：使用正确的字段名 eval_result
        const evalResult = result.eval_result || result.eval_res || '未返回分析结果';
        cardStore[dataIndex].analysisResult = evalResult.replace(/\n/g, '<br>');
        
        // 立即更新 UI
        renderCards();
        
        debugLog(`罗睺镜: 第${current}条评价已分析完成`);
      }
      
      // 递归处理下一条
      submitNext(sortedEntries, index + 1, total, cardStore, url);
    })
    .catch(err => {
      console.error(`第${current}条评价提交失败:`, err);
      
      // 标记失败
      cardStore[dataIndex].analysisResult = `<span style="color: #e53e3e;">提交失败: ${err.message}</span>`;
      renderCards();
      
      // 继续处理下一条
      submitNext(sortedEntries, index + 1, total, cardStore, url);
    });
  }

  // ===== 状态提示 =====
  
  function showStatus(message, type = 'info') {
    const status = document.getElementById('luohou-status');
    if (!status) return;
    
    status.textContent = message;
    status.style.display = 'block';
    status.style.borderLeftColor = type === 'success' ? '#48bb78' : type === 'error' ? '#fc8181' : '#667eea';
    status.style.color = type === 'success' ? '#38a169' : type === 'error' ? '#e53e3e' : '#667eea';
    status.style.background = type === 'success' ? '#f0fff4' : type === 'error' ? '#fff5f5' : 'white';

    if (type !== 'error') {
      setTimeout(() => { status.style.display = 'none'; }, 3000);
    }
  }

  function showStatusWithSpinner(message) {
    const status = document.getElementById('luohou-status');
    if (!status) return;
    
    if (!document.getElementById('spin-style')) {
      const style = document.createElement('style');
      style.id = 'spin-style';
      style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
      document.head.appendChild(style);
    }
    
    status.innerHTML = `<span style="display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(102, 126, 234, 0.3); border-top-color: #667eea; border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 6px; vertical-align: middle;"></span>${message}`;
    status.style.display = 'block';
  }

  // ===== 消息监听 =====
  
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'togglePanel') {
      togglePanel();
      sendResponse({ isOpen: window.luohouData.isPanelOpen });
    } else if (message.action === 'getPanelState') {
      sendResponse({ isOpen: window.luohouData.isPanelOpen });
    } else if (message.action === 'triggerCollection') {
      collectContent(false); // 手动模式
      sendResponse({ status: 'triggered' });
    } else if (message.action === 'clearCache') {
      const result = clearCacheSilent();
      sendResponse(result);
    }
    return true;
  });

  // ===== 初始化 =====
  
  // 从 storage 加载缓存
  chrome.storage.local.get(['allCardsByUrl'], (result) => {
    window.luohouData.allCardsByUrl = result.allCardsByUrl || {};
    if (window.luohouData.allCardsByUrl[window.luohouData.currentUrl]) {
      debugLog(`罗睺镜: 加载了${Object.keys(window.luohouData.allCardsByUrl[window.luohouData.currentUrl]).length}条缓存评价`);
    }
  });

  // MutationObserver 监听页面变化（防抖 500ms，自动模式）
  let collectTimer = null;
  const observer = new MutationObserver(() => {
    // 如果正在提交，暂停自动采集
    if (window.isSubmitting) {
      return;
    }
    
    clearTimeout(collectTimer);
    collectTimer = setTimeout(() => {
      collectContent(true); // 自动模式
    }, 500);
  });

  // 页面加载完成后立即采集并启动观察者
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      collectContent(true); // 首次自动采集
      observer.observe(document.body, { childList: true, subtree: true, attributes: true });
    });
  } else {
    collectContent(true); // 首次自动采集
    observer.observe(document.body, { childList: true, subtree: true, attributes: true });
  }

  debugLog('罗睺镜: 初始化完成');
}
