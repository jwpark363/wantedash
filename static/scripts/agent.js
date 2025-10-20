// Send Message
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;
    
    const timestamp = getCurrentTime();
    const userMsg = { role: 'user', content: message, timestamp };
    
    addMessageToUI('user', message, timestamp);
    messages.push(userMsg);
    
    // Update session
    const session = chatSessions.find(s => s.id === currentSessionId);
    if (session) {
        session.messages = messages;
        if (session.title === '새로운 대화') {
            session.title = message.substring(0, 30) + (message.length > 30 ? '...' : '');
            updateChatHistory();
        }
    }
    
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    isLoading = true;
    sendBtn.disabled = true;
    sendBtn.innerHTML = '⏳';
    showLoading();
    

    //함수호출
    try {
        const response = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        const data = await response.json();
        console.log(data);
        hideLoading();        
        const aiTimestamp = getCurrentTime();
        addMessageToUI('assistant', data.output, aiTimestamp);
        messages.push({ role: 'assistant', content: data.output, timestamp: aiTimestamp });
    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        addMessageToUI('assistant', '오류가 발생했습니다. 다시 시도해주세요.', getCurrentTime());
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        sendBtn.innerHTML = '➤';
    }       
}