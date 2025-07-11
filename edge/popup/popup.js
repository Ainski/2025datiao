chrome.runtime.sendMessage({action: 'getURL'}, (response) => {
  document.getElementById('url').textContent = response.url;
});

// chrome.runtime.onMessage.addListener(message => {
//   if (message.action === 'updateRateCards') {
//     const container = document.getElementById('cards-container');
//     container.innerHTML = message.cards.map(card => `
//       <div style="margin:10px;padding:15px;background:white;border-radius:6px">
//         <div style="color:#666">${card.user}</div>
//         <div style="color:#f90;margin:5px 0">${'★'.repeat(card.rating)}</div>
//         <div>${card.content}</div>
//       </div>
//     `).join('');
//     document.getElementById('card-count').textContent = message.cards.length;
//   }
// });
chrome.runtime.onMessage.addListener(message => {
  if (message.action === 'updateRateCards') {
    // 修改updateRateCards消息处理（仅存储数据）
    chrome.runtime.onMessage.addListener(message => {
      if (message.action === 'updateRateCards') {
        // 存储原始数据到全局变量
        window.cardList = message.cards;
        document.getElementById('status').textContent = `已缓存${message.cards.length}条评价`;
      }
    });
    
    // 修改确认按钮事件（添加视图更新）


  }
});
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'pageContent') {
    document.getElementById('content').textContent = message.content;
  }
});

// 分离原有的事件处理
document.getElementById('confirm-btn').addEventListener('click', () => {
  const container = document.getElementById('cards-container');
  container.innerHTML = '';
  
  // 使用存储的数据渲染视图
  window.cardList?.forEach((text, index) => {
    const card = document.createElement('div');
    card.style.cssText = 'margin:10px; padding:15px; background:#fff; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);';
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between;">
        <div style="flex: 1; padding-right: 15px;">
          <div style="color:#333; font-weight:500;">评价 #${index + 1}</div>
          <div style="color:#666; margin-top:8px; line-height:1.5;">
            ${text.replace(/\n/g, '<br>')}
          </div>
        </div>
        <div id="analysis-result-${index}" style="flex: 1; padding-left: 15px; border-left: 1px solid #eee;">
          <div style="color:#333; font-weight:500;">分析结果</div>
          <div style="color:#666; margin-top:8px;">等待提交分析...</div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
});

// 更新提交处理逻辑（L68-102）

// 修改后的提交按钮处理
// 修改后的提交处理逻辑
document.getElementById('submit-btn').addEventListener('click', () => {
  const btn = document.getElementById('submit-btn');
  const status = document.getElementById('status');
  
  btn.disabled = true;
  status.style.display = 'block';
  status.textContent = '提交中...';

  // 直接从DOM获取评价内容
  const cards = Array.from(document.querySelectorAll('#cards-container > div'))
    .map(card => card.innerText.trim().replace(/评价 #\d+/,''));

  fetch('http://localhost:8989/api/input', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': '1IlIl1|1Il||||/\\|1'
    },
    body: JSON.stringify({
      comments: cards,
      url: document.getElementById('url').textContent
    })
  })
  .then(res => {
    if (!res.ok) throw new Error(`HTTP错误 ${res.status}`);
    btn.disabled = false;
    return res.json();
  })
  .then(data => {
    const container = document.getElementById('cards-container');
    // 清空旧内容
    container.innerHTML = '';
    data.forEach((item, index) => {
      const card = document.createElement('div');
      card.style.cssText = 'margin:10px; padding:15px; background:#fff; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);';
        card.innerHTML = `
        <div style="display: flex; justify-content: space-between;">
          <div style="flex: 1; padding-right: 15px;">
            <div style="color:#333; font-weight:500;">评价 #${index + 1}</div>
            <div style="color:#666; margin-top:8px; line-height:1.5;">
              ${item.comment.replace(/\n/g, '<br>')}
            </div>
          </div>
          <div id="analysis-result-${index}" style="flex: 1; padding-left: 15px; border-left: 1px solid #eee;">
            <div style="color:#333; font-weight:500;">分析结果</div>
            
            <div style="color:#666; margin-top:8px; line-height:1.5;">
              ${item.eval_res.replace(/\n/g, '<br>')}
            </div>
          </div>
        </div>
        `;
      container.appendChild(card);
    });
    btn.disabled = false;
  })
  .catch(err => {
    console.error('提交失败:', err);
    btn.disabled = false;
    status.textContent = `提交失败: ${err.message}`;
  });

});

// 更新卡片渲染逻辑
function renderCards(cards) {
  const container = document.getElementById('comments-column');
  container.innerHTML = cards.map((card, index) => 
    `<div class="comment-card" data-index="${index}">
      <!-- 原有卡片内容 -->
    </div>`
  ).join('');
};