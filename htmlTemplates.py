css = '''
<style>
.chat-message{
    padding:1rem;
    border-radius:12px;
    margin-bottom:1rem;
    display:flex;
    align-items:center;
    box-shadow:0px 3px 10px rgba(0,0,0,0.15);
}
.chat-message.user{
    background:#1e293b;
}
.chat-message.bot{
    background:#0f766e;
}
.chat-message .avatar{
    width:15%;
}
.chat-message .avatar img{
    width:60px;
    height:60px;
    border-radius:50%;
    object-fit:cover;
}
.chat-message .message{
    width:85%;
    padding-left:1rem;
    color:white;
    font-size:16px;
    line-height:1.5;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/gemini_1.width-1000.format-webp.webp">
    </div>
    <div class="message">
        <b>Gemini AI</b><br>
        {{MSG}}
    </div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
    </div>
    <div class="message">
        <b>You</b><br>
        {{MSG}}
    </div>
</div>
'''