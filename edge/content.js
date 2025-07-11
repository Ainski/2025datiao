document.addEventListener('DOMContentLoaded', () => {
  sendContent(); // 新增初始化调用
  
  // 保留原有页面内容采集
  chrome.runtime.sendMessage({
    action: 'pageContent',
    content: document.documentElement.outerHTML
  });
});

// 合并重复的MutationObserver
const observer = new MutationObserver(() => {
  sendContent();
  chrome.runtime.sendMessage({ 
    action: 'updateContent',
    content: document.documentElement.outerHTML 
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true
});

// 统一消息处理
chrome.runtime.onMessage.addListener((request) => {
  if (request.action === 'updateContent') {
    sendContent();
  }
});

const sendContent = () => {
  // 获取所有评价卡片的完整文本内容
  const all=document.documentElement.outerHTML;
  //console.log(all);
  const cards = Array.from(document.querySelectorAll('.jdc-pc-rate-card-main-desc'))
    .map(card => card.innerText.trim());
  console.log(cards);

  chrome.runtime.sendMessage({
    action: 'updateRateCards',
    cards: cards.filter(text => text.length > 0) // 仅过滤空内容
  });
};

let isMonitoring = false;

// Wrap observer in IIFE to prevent redeclaration
(function initObserver() {
  const observer = new MutationObserver(mutations => {
    // Existing observation logic
  });
  
  // Existing observation configuration
  observer.observe(document, { childList: true, subtree: true });
})();

// Existing message listener
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'startMonitoring') {
    // Existing monitoring logic
  }
});

// 修改初始事件监听为一次性执行
document.addEventListener('DOMContentLoaded', () => {
  chrome.runtime.sendMessage({
    action: 'pageContent',
    content: document.documentElement.outerHTML
  });
}, {once: true});
