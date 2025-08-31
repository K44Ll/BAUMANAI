document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const clearBtn = document.getElementById("clear-chat");

    // Função para pegar CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Função para adicionar mensagem no front-end
    function appendMessage(msg, sender) {
        const div = document.createElement("div");
        div.classList.add("message", sender); // 'user' ou 'bot'
        div.innerHTML = msg;
        chatBox.appendChild(div);
    }

    // Carregar todas as mensagens do servidor
    async function carregarMensagens() {
        try {
            const resp = await fetch("/chat/mensagens/");
            const data = await resp.json();
            chatBox.innerHTML = ""; // limpa o chat antes
            data.mensagens.forEach(msg => {
                const usuario = msg.usuario ? msg.usuario : "BaumanAI";
                appendMessage(`<b>${usuario}</b> [${msg.hora}]: ${msg.texto}`, msg.usuario ? "user" : "bot");
            });
        } catch (err) {
            console.error("Erro ao carregar mensagens:", err);
        }
    }

    // Enviar nova mensagem
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const texto = chatInput.value.trim();
        if (!texto) return;

        chatInput.value = ""; // limpa input

        try {
            const resp = await fetch("/chatapi/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ message: texto })
            });
            const data = await resp.json();
            if (data.response) {
                carregarMensagens(); // atualiza chat com nova mensagem
            } else if (data.error) {
                alert("Erro: " + data.error);
            }
        } catch (err) {
            console.error("Erro ao chamar a API:", err);
        }
    });

    // Botão de limpar chat (apenas admin)
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (confirm("Tem certeza que deseja limpar o chat?")) {
                fetch("/clear-chat/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json"
                    }
                })
                .then(resp => resp.json())
                .then(data => {
                    if (data.status === "ok") {
                        chatBox.innerHTML = ""; // limpa front-end
                    } else {
                        alert("Erro ao limpar o chat");
                    }
                })
                .catch(err => console.error("Erro ao limpar chat:", err));
            }
        });
    }

    // Atualizar chat a cada 2s
    setInterval(carregarMensagens, 2000);
    carregarMensagens();
});
