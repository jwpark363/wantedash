// chat의 session_id로 사용
// 로컬 스토리지에 해당 정보 저장 후 사용
// 저장된 값이 있으면 해당 정보 사용
const _local_user_id = localStorage.getItem('wantedash-userid')
const userSession = _local_user_id ? _local_user_id : 'user::'+crypto.randomUUID();
if(_local_user_id == null){
    localStorage.setItem('wantedash-userid', userSession)
}
console.log("USER SESSION ID : " + userSession)

let messages = [];
let isLoading = false;
let chatSessions = [];
// chat의 conversation_id로 사용
let currentSessionId = crypto.randomUUID();
const chatArea = document.getElementById('chatArea');
const chatContent = document.getElementById('chatContent');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const welcomeScreen = document.getElementById('welcomeScreen');

// Initialize first session
function newChatTitle(){
    const now = new Date();
    return makeChatTitle(now);
    // const year = now.getFullYear();
    // const month = now.getMonth() + 1; // 0부터 시작하므로 +1
    // const date = now.getDate();
    // const hours = now.getHours();
    // const minutes = now.getMinutes();
    // const seconds = now.getSeconds();
    // return `${year}/${month}/${date} ${hours}:${minutes}:${seconds}`
}

function makeChatTitle(_date){
    const year = _date.getFullYear();
    const month = _date.getMonth() + 1; // 0부터 시작하므로 +1
    const date = _date.getDate();
    const hours = _date.getHours();
    const minutes = _date.getMinutes();
    const seconds = _date.getSeconds();
    return `${year}/${month}/${date} ${hours}:${minutes}:${seconds}`
}


// chatSessions.push({
//     id: currentSessionId,
//     title: newChatTitle(),
//     messages: []
// });

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

// Handle Enter key
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Toggle Sidebar (Mobile)
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// Toggle Settings
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('active');
}

// New Chat
function newChat(is_first) {
    currentSessionId = crypto.randomUUID();
    chatSessions.push({
        id: currentSessionId,
        title: newChatTitle(),
        messages: []
    });
    if(!is_first){
        messages = [];
        chatContent.innerHTML = '';
        welcomeScreen.style.display = 'block';
    }
    updateChatHistory();
}

// Update Chat History
function updateChatHistory() {
    const historyEl = document.getElementById('chatHistory');
    const reversedSessions = chatSessions.slice().reverse();
    let html = '';
    for (let i = 0; i < reversedSessions.length; i++) {
        const session = reversedSessions[i];
        const isActive = session.id === currentSessionId ? 'active' : '';
        html += '<div class="chat-item ' + isActive + '" onclick="loadSession(\'' + session.id + '\')">';
        html += '<span class="chat-item-icon">💬</span>';
        html += '<span class="chat-item-text">' + session.title + '</span>';
        html += '</div>';
    }
    historyEl.innerHTML = html;
}

// Load Session
function loadSession(sessionId) {
    console.log("loadSession : " + sessionId)
    const session = chatSessions.find(s => s.id === sessionId);
    if (session) {
        currentSessionId = sessionId;
        messages = session.messages;
        chatContent.innerHTML = '';
        
        if (messages.length === 0) {
            welcomeScreen.style.display = 'block';
        } else {
            welcomeScreen.style.display = 'none';
            messages.forEach(msg => {
                addMessageToUI(msg.role, msg.content, msg.timestamp);
            });
        }
        updateChatHistory();
    }
}

// Set Input
function setInput(text) {
    messageInput.value = text;
    messageInput.focus();
}

// Clear Chat
function clearChat() {
    if (confirm('현재 대화 내용을 삭제하시겠습니까?')) {
        const session = chatSessions.find(s => s.id === currentSessionId);
        if (session) {
            session.messages = [];
        }
        messages = [];
        chatContent.innerHTML = '';
        welcomeScreen.style.display = 'block';
    }
}

// Get Current Time
function getCurrentTime() {
    return getChatTime(new Date());
    // return new Date().toLocaleTimeString('ko-KR', { 
    //     hour: '2-digit', 
    //     minute: '2-digit' 
    // });
}
function getChatTime(date){
    return date.toLocaleTimeString('ko-KR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Scroll to Bottom
function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Add Message to UI
function addMessageToUI(role, content, timestamp) {
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🧞';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content-wrapper">
            <div class="message-content">${content}</div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;
    
    chatContent.appendChild(messageDiv);
    scrollToBottom();
}

// Show Loading
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.id = 'loadingIndicator';
    
    loadingDiv.innerHTML = `
        <div class="message-avatar">🧞</div>
        <div class="loading-content">
            <div class="spinner"></div>
            <span>생각하는 중...</span>
        </div>
    `;
    
    chatContent.appendChild(loadingDiv);
    scrollToBottom();
}

// Hide Loading
function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// 초기 초대 항목 등록 하기
console.log('초기 항목 등록하기');
// Welcome 항목
(async () => {
    const job_list = await fetch('http://localhost:8000/jobs').then(res => res.json());
    console.log(job_list);
    const grid = document.getElementById('welcomeGrid');
    const welcome_data = ['업무 문의']
    // welcome_data = welcome_data.concat(job_list['jobs'])
    welcome_data.concat(job_list['jobs']).forEach(data => {
        const card = document.createElement('div');
        card.classList.add('example-card');
        card.innerHTML = `<p>${data}</p>`;
        card.addEventListener('click', function() {
            setInput(data)
        });
        grid.appendChild(card);
    });
})();
// chat history
(async () => {
    // console.log(`http://localhost:8000/api/messages/${userSession}`)
    const history = await fetch(`http://localhost:8000/api/messages/${userSession}`).then(res => res.json());
    console.log("****** chat history ******")
    console.log(history)
    //불러온 데이터 처리
    if(history){
        //1 session 리스트 가져오기
        const session_list = [...new Set(history.result.map(message => message.conversation_id))]
        let count = 1;
        let _chat_title = ''
        for(const _id of session_list){
            const _messages = []
            //2. 각 session의 메시지 리스트 가져오기
            const _id_messages = history.result.filter(message => message.conversation_id === _id)
            _id_messages.forEach((message,idx) => {
                if(idx === 0){
                    _chat_title = makeChatTitle(new Date(message.created_at));
                }
                if(message.type === 'HUMAN'){
                    _messages.push({
                        role: 'user',
                        content: message.content,
                        timestamp: getChatTime(new Date(message.created_at))
                    });
                }else if(message.type === 'AI'){
                    _messages.push({
                        role: 'assistant',
                        content: message.content,
                        timestamp: getChatTime(new Date(message.created_at))
                    });
                }
            })
            chatSessions.push({
                id: _id,
                title: _chat_title,  //`히스토리 ${count}`,
                messages: _messages
            });
            count ++;
        }
        updateChatHistory();
    }
    newChat(true);
})();
