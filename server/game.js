function oneButtonDoBothThings() {
    hideRole();
    hideName();
    hideChat()
}

const hideRole = async () => {
    const role = await document.getElementById("role-text");
    console.log(role.style.display)
    if (role.style.display === "none" || role.style.display === "") {
        role.style.display = "block";
    } else {
        role.style.display = "none";
    }
}

const hideName = async () => {
    document.querySelectorAll(".name-text").forEach(function (role2) {
        if (role2.classList.contains("username")) {
            role2.classList.add("werewolf");
            role2.classList.remove("username")
            console.log('white to red')
        } else {
            role2.classList.remove("werewolf");
            console.log('red to white')
            role2.classList.add('username')
        }
    });
}

const hideChat = async () => {
    const chat = await document.getElementById("chat-box");
    if ( chat.style.display === "none" || chat.style.display === "") {
        chat.style.display = "block";
    } else {
        chat.style.display = "none";
    }
}
var socket

function SetupChat(username) {


    socket = io('http://146.190.21.110:5000');

    socket.on('message', function (message) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        document.getElementById('messages').appendChild(messageElement);
    });
}

function sendMessage(username) {
    const messageInput = document.getElementById('chat-message');
    const message = messageInput.value;
    socket.emit('message', username + ": " + message);
    messageInput.value = '';
}
