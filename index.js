import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { generate } from "random-words"

const app = express();
const server = createServer(app).listen(80);
const io = new Server(server);
const events = new WeakMap();

app.use(express.static("public"));

io.on("connection", (socket) => {
    const { id } = socket.handshake.query;
    const room = (socket.join(id), io.sockets.adapter.rooms.get(id));
    if (!events.has(room)) events.set(room, [[...init()]]);

    events.get(room).forEach(socket.emit.bind(socket, "event"));
    socket.on("event", (event) => {
        events.get(room).push(event);
        socket.broadcast.to(id).emit("event", event);
    });
});

function* init() {
    const colors = [
        ...Array(9).fill("red"),
        ...Array(8).fill("blue"),
        ...Array(7).fill("black"),
        ...Array(1).fill("purple"),
    ];
    for (const word of generate(25))
        yield [word.toUpperCase(), ...colors.splice(
            Math.floor(Math.random() * colors.length), 1)]
}
