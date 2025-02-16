import { io } from "https://cdn.socket.io/4.8.1/socket.io.esm.min.js";

const socket = io((location.search ||= `?id=${Math.random()}`));

socket.on("event", (target) => {
  if (Array.isArray(target))
    grid.append(
      ...target.map(([word, color]) => {
        const button = document.createElement("button");
        button.textContent = word;
        button.style.color = color;
        return button;
      })
    );
  else
    document
      .evaluate(`//button[text()="${target}"]`, document)
      .iterateNext()
      .click();
});

onclick = ({ target, isTrusted }) => {
  if (!target.matches("button")) return;
  if (isTrusted) socket.emit("event", target.textContent);
  if (target.matches("#turn + button")) return next();

  target.disabled = true;
  const { color } = target.style;
  if (!document.querySelector(`[style~="${color};"]:enabled`)) {
    alert("Game over!");
    role.value = "spymaster";
  } else if (color != turn.textContent) next();
};

function next() {
  turn.textContent = turn.textContent === "red" ? "blue" : "red";
  turn.className = turn.textContent;
}
