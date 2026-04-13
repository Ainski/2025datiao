// 初始化时检查面板状态
chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
  if (tabs[0]) {
    chrome.tabs.sendMessage(tabs[0].id, {action: 'getPanelState'}, (response) => {
      if (chrome.runtime.lastError || !response) {
        updateButton(false);
      } else {
        updateButton(response.isOpen);
      }
    });
  }
});

// 切换面板
document.getElementById('toggle-btn').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (!tabs[0]) return;

    chrome.tabs.sendMessage(tabs[0].id, {action: 'togglePanel'}, (response) => {
      if (chrome.runtime.lastError) {
        showStatus('请先刷新页面', 'error');
      } else {
        updateButton(response.isOpen);
      }
    });
  });
});

// 清空缓存
document.getElementById('clear-btn').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    if (!tabs[0]) return;

    chrome.tabs.sendMessage(tabs[0].id, {action: 'clearCache'}, (response) => {
      if (chrome.runtime.lastError) {
        showStatus('请先刷新页面', 'error');
      } else if (response && response.success) {
        showStatus(`已清空${response.count}条缓存`, 'success');
      } else if (response && !response.hasData) {
        showStatus('当前页面暂无缓存', 'info');
      }
    });
  });
});

function updateButton(isOpen) {
  const btn = document.getElementById('toggle-btn');
  const status = document.getElementById('status');
  
  if (isOpen) {
    btn.textContent = '关闭面板';
    btn.classList.add('active');
    status.style.display = 'block';
    status.textContent = '面板已开启';
  } else {
    btn.textContent = '开启面板';
    btn.classList.remove('active');
    status.style.display = 'none';
  }
}

function showStatus(msg, type) {
  const status = document.getElementById('status');
  status.textContent = msg;
  status.style.display = 'block';
  status.style.borderLeftColor = type === 'error' ? '#fc8181' : type === 'success' ? '#48bb78' : '#667eea';
  status.style.color = type === 'error' ? '#e53e3e' : type === 'success' ? '#38a169' : '#667eea';
  status.style.background = type === 'error' ? '#fff5f5' : type === 'success' ? '#f0fff4' : '#f7fafc';
  setTimeout(() => { status.style.display = 'none'; }, 2000);
}
