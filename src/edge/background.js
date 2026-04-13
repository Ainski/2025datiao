// 页面加载完成后注入 content.js
chrome.webNavigation.onCompleted.addListener(({url, tabId}) => {
  if (url.includes('item.jd.com')) {
    chrome.tabs.get(tabId, (tab) => {
      if (tab?.status === 'complete') {
        chrome.scripting.executeScript({
          target: { tabId },
          files: ['content.js']
        }).catch(err => console.log('罗睺镜: 脚本注入跳过', err));
      }
    });
  }
});
