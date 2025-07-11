// 移除自动注入逻辑，保留消息转发功能
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.action === 'updateRateCards' && sender.tab?.id) {
    chrome.tabs.sendMessage(sender.tab.id, message);
  }
});

// 添加全局错误监听
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  try {
    if (message.action === 'getURL') { // 修改request为message
      chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        sendResponse({url: tabs[0].url});
      });
      return true;
    }
  } catch (e) {
    console.error('Runtime message error:', e);
  }
});

// 统一使用destructuring语法
// 使用IIFE封装异步逻辑
chrome.webNavigation.onCompleted.addListener(({url, tabId}) => {
  (async () => {
    if (url.startsWith('https://item.jd.com/')) {
      const tab = await chrome.tabs.get(tabId);
      if (tab?.status === 'complete') {
        // 在脚本注入后主动请求内容
        chrome.scripting.executeScript({
          target: { tabId },
          files: ['content.js']
        }).then(() => {
          chrome.tabs.sendMessage(tabId, { action: 'updateContent' });
        });
      }
    }
  })().catch(console.error);
});
