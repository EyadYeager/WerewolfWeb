const express = require('express');
const http = require('http');
const socketIo = require('socket.io');


const app = express();
const server = http.createServer(app);
// Specify CORS options
const io = socketIo(server, {
    cors: {
        origin: "*", // This allows all origins. For production, specify your frontend origin, e.g., "http://localhost:3000"
        methods: ["GET", "POST"] // Allowed HTTP request methods for CORS requests
    }
});
io.on('connection', (socket) => {
    console.log('User connected');
    // Listen for incoming messages
    socket.on('message', (message) => {
        console.log('Message:', message);
        // Broadcast the message to all connected clients
        io.emit('message', message);
    });
    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});